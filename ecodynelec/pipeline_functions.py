"""This module contains the functions to run the `pipeline` module

This module contains:
    - load_config: loads the configuration parameters.
    - check_download: checks if the entso-e data needs to be downloaded.
    - load_raw_prod_exchanges: loads the raw production and exchanges data.
    - load_impact_matrix: loads the impact matrix.
    - check_mapping: checks the mapping between production and impacts.
    - get_mix: computes the electric mix of the target countries.
    - get_impacts: computes the impacts of these mixs.
    - get_productions : computes production values in kWh for each source.
    - translate_to_timezone: translates the data into the timezone.
    - save_results: saves the results.
    - localize_from_utc: shifts the time-zone from results.
"""
import os.path

import numpy as np
import pandas as pd

from ecodynelec import saving
from ecodynelec.impacts import compute_impacts
from ecodynelec.parameter import Parameter
from ecodynelec.preprocessing import auxiliary as aux
from ecodynelec.preprocessing.downloading import download
from ecodynelec.preprocessing.load_impacts import extract_mapping, extract_UI
from ecodynelec.preprocessing.loading import import_data
from ecodynelec.preprocessing.residual import include_local_residual
from ecodynelec.progress_info import ProgressInfo
from ecodynelec.tracking import track_mix, set_FU_vector


def load_config(config):
    """Loads the configuration parameters.

    Parameters
    ----------
        config: ecodynelec.Parameter or str
            a set of configuration parameters to govern the computation,
            either as Parameter object or str pointing at an xlsx file.

    Returns
    -------
    ecodynelec.Parameter
        The loaded Parameter object.
    """
    if isinstance(config, Parameter):  # If a parameter object
        p = config
    elif isinstance(config, str):
        if any([config.endswith(k) for k in ('.xlsx', '.xls', '.ods')]):
            p = Parameter(excel=config)
        else:
            raise NotImplementedError(f"File extension for {config} is not supported.")
    else:
        raise ValueError('Missing a configuration to pass parameters.')
    # Check if residual is global OR local
    if np.logical_and(p.residual_global, p.residual_local):
        raise ValueError("Residual can not be both global and local.")
    # Convert target to list is not already
    if isinstance(p.target, str):
        p.target = [p.target]
    return p


def check_download(parameters: Parameter, is_verbose: bool = False):
    """Checks if the config requires to download the entso-e data, and if so, downloads it.

    Parameters
    ----------
        parameters: ecodynelec.Parameter
            Parameters returned by :py:func:`load_config`.
        is_verbose: bool, default to False
            To display information
    """
    if parameters.server.useServer:
        if None in [parameters.path.generation, parameters.path.exchanges]:  # If one path was not given
            raise KeyError("Can not download files: missing path raw_generation and/or raw_exchange to save files.")
        if is_verbose: print("Download Entso-E data from server...")
        download(config=parameters, is_verbose=is_verbose)  # Save files in a local dirrectory


def load_raw_prod_exchanges(parameters, is_verbose: bool = False, progress_bar: ProgressInfo = None):
    """Loads the raw production and exchange data from entso-e.

    Parameters
    ----------
        parameters: ecodynelec.Parameter or str
            a set of configuration parameters to govern the computation,
            either as Parameter object or str pointing at an xlsx file.
        is_verbose: bool, default to False
            To display progress information
        progress_bar: ecodynelec.ProgressInfo, default to None
            The progress bar to use, or None

    Returns
    -------
    A tuple of three pandas.DataFrame:
        praw_prodExch: DataFrame with all productions and all exchanges from all included countries.
        prod_gap: information about the nature of the residual
        sg_data: production information from Swiss Grid
    """
    p = load_config(parameters)
    check_download(p, is_verbose=is_verbose)

    if progress_bar:
        progress_bar.set_sub_label('Load auxiliary datasets...')
    # Load SwissGrid -> if Residual or SG exchanges
    if np.logical_or(np.logical_or(p.residual_global, p.residual_local), p.sg_imports):
        # Load SwissGrid data, adjusting the date parameters for the time zone difference
        # EcoDynElec is using UTC while SwissGrid is using Europe/Zurich (UTC+1 in winter, UTC+2 in summer)
        # We use the most little time step possible to avoid issues with the time zones
        range = pd.date_range(start=p.start, end=p.end, freq="15min")
        range = range.tz_localize('UTC').tz_convert('Europe/Zurich').tz_localize(None) # Translate to Europe/Zurich timezone then remove tz info (for comparison with data source files)
        sg_data = aux.load_swissGrid(path_sg=p.path.swissGrid, start=str(range[0]), end=str(range[-1]), freq='15min')
        # Shift the SwissGrid data index back by one hour to convert from Europe/Zurich to UTC
        sg_data.index = sg_data.index.tz_localize('Europe/Zurich', nonexistent='shift_backward').tz_convert('UTC').tz_localize(None)
        # Resample the SwissGrid data to the desired frequency, after the time zone conversion
        sg_data = sg_data.resample(p.freq).sum()
    else:
        sg_data = None
    if progress_bar:
        progress_bar.progress()
        progress_bar.set_sub_label('Load neighbors...')

    # Load Country of interest -> Always
    neighbours = aux.load_useful_countries(path_neighbour=p.path.neighbours, ctry=p.ctry)

    if progress_bar:
        progress_bar.progress()
        progress_bar.set_sub_label('Load production gap...')

    # Load production gap data -> if Residual
    if np.logical_or(p.residual_global, p.residual_local):
        prod_gap = aux.load_gap_content(path_gap=p.path.gap, start=p.start, end=p.end, freq=p.freq, header=59)
    else:
        prod_gap = None

    if progress_bar:
        progress_bar.progress()
        progress_bar.set_sub_label('Load ENTSO-E data...')

    # Load generation and exchange data from entso-e
    raw_prod_exch = import_data(ctry=p.ctry, start=p.start, end=p.end, freq=p.freq, involved_countries=neighbours,
                               prod_gap=prod_gap, sg_data=sg_data,
                               path_gen=p.path.generation, path_imp=p.path.exchanges,
                               savedir=p.path.savedir, net_exchange=p.net_exchanges,
                               residual_global=p.residual_global, correct_imp=p.sg_imports,
                               clean_data=p.data_cleaning, is_verbose=is_verbose, progress_bar=progress_bar)
    return raw_prod_exch, prod_gap, sg_data


def load_impact_matrix(parameters: Parameter, is_verbose: bool = False):
    """Loads the impact matrix from the specified parameters.

    Parameters
    ----------
        parameters: ecodynelec.Parameter
            Parameters returned by load_config.
        is_verbose: bool, default to False
            To display progress information

    Returns
    -------
        impact_matrix: pandas.DataFrame
            The unit impact vector of electricity production
    """

    # Load impact matrix (UI vector by default)
    if parameters.path.mapping is not None:  # Priority to the mapping spreadhseet, as soon as it is specified
        impact_matrix = extract_mapping(ctry=parameters.ctry, mapping_path=parameters.path.mapping,
                                        cst_import=parameters.cst_imports,
                                        residual=np.logical_or(parameters.residual_global, parameters.residual_local),
                                        target=parameters.target, is_verbose=is_verbose)
    else:  # If no mapping specified, go for the UI vector: it can grab the default vector automatically
        impact_matrix = extract_UI(path_ui=parameters.path.ui_vector, ctry=parameters.ctry, target=parameters.target,
                                   cst_imports=parameters.cst_imports,
                                   residual=np.logical_or(parameters.residual_global, parameters.residual_local))
    return impact_matrix


def get_mix(parameters: Parameter, raw_prod_exch: pd.DataFrame, sg_data: pd.DataFrame = None,
            prod_gap: pd.DataFrame = None, return_matrix: bool = False, is_verbose: bool = False):
    """Loads the mix from the specified parameters.
    Also includes the local residual if return_matrix is False and parameters.residual_local is True.

    Parameters
    ----------
        parameters: ecodynelec.Parameter
            Parameters returned by load_config.
        raw_prod_exch: pandas.DataFrame
            The raw production and exchange data, as returned by load_raw_prod_exchanges.
        sg_data: pandas.DataFrame, default to None
            The SwissGrid data, as returned by load_raw_prod_exchanges.
        prod_gap: pandas.DataFrame, default to None
            The production gap data, as returned by load_raw_prod_exchanges.
        return_matrix: bool, default to False
            If True, returns the whole mix matrix instead of the mix dictionary
            (the impact matrix sorted by target country).
        is_verbose: bool, default to False
            To display progress information

    Returns
    -------
        return_matrix is False:
            A dictionary of pandas.DataFrame, with the mix for each target (parameter.target)
            (containing the contribution of each production mean in 1 kWh consumed in the target country).
            This includes the local residual if parameters.residual_local is True.
        return_matrix is True:
            The raw table with the electricity mix in the studied countries
            (parameter.ctry + 'Other'), containing each production mean of each country.
            This does not include the local residual.
    :type: dict or pandas.DataFrame

    """
    # Load network losses -> if Network Loss asked
    if parameters.network_losses:
        network_losses = aux.load_grid_losses(network_loss_path=parameters.path.networkLosses, start=parameters.start,
                                              end=parameters.end)
    else:
        network_losses = None

    mix_df = track_mix(raw_data=raw_prod_exch, freq=parameters.freq, network_losses=network_losses,
                       residual_global=parameters.residual_global,
                       is_verbose=is_verbose)
    if return_matrix:
        # old behavior for 'get_inverted_matrix' pipeline
        time_steps = []
        for step in mix_df.index.levels[0]:
            time_steps.append(mix_df.loc[step, :])
        return time_steps
    mix_dict = {}
    for target in parameters.target:
        mix_dict[target] = mix_df[f'Mix_{target}'].unstack()

    if parameters.residual_local:
        if is_verbose: print("Compute local residual...")
        for target in parameters.target:
            local = [k for k in raw_prod_exch.columns if k.endswith(f'_{target}')]
            mix_dict[target] = include_local_residual(mix_data=mix_dict[target], sg_data=sg_data,
                                                      local_prod=raw_prod_exch.loc[:, local],
                                                      gap=prod_gap, freq=parameters.freq, target=target)
    return mix_dict


def get_impacts(mix_dict: dict, impact_matrix: pd.DataFrame, missing_mapping: str = 'error', is_verbose: bool = False):
    """Computes the impact of the given electrical mix.

    Parameters
    ----------
        mix_dict: dict of pandas.DataFrame
            The mix for each target, as returned by get_mix.
        impact_matrix: pandas.DataFrame
            The impact matrix, as returned by load_impact_matrix.
        missing_mapping: str, default to 'error'
            strategy for handling producing units with not mapping.
            'error' (default) raises an error, 'worst' takes the highest impact value in
            the available set, 'unit' takes the highest impact value available from a
            similar unit type, defaults to 'error'
        is_verbose: bool, default to False
            To display progress information

    Returns
    -------
    imp_dict: dict
        A dictionary containing the impacts for each target.
        For each country, this is a dict of tables containing the dynamic impacts of 1kWh of electricity.
    """
    imp_dict = {}
    for target in mix_dict.keys():
        imp_dict[target] = compute_impacts(mix_data=mix_dict[target], impact_data=impact_matrix,
                                           strategy=missing_mapping, is_verbose=is_verbose)
    return imp_dict


def get_productions_imports_kwh(parameters: Parameter, raw_prod_exch: pd.DataFrame, sg: pd.DataFrame, mix_dict: dict):
    """
    Compute the production and imports for each country, in kWh, for each production type, at each time step.

    Parameters
    ----------
    parameters: ecodynelec.Parameter
        Parameters returned by load_config.
    raw_prod_exch: pandas.DataFrame
        The raw production and exchange data, as returned by load_raw_prod_exchanges.
    sg: pandas.DataFrame
        The SwissGrid data, as returned by load_raw_prod_exchanges.
    mix_dict: dict of DataFrame
        The mix for each target, as returned by get_mix.

    Returns
    -------
    prod_dict: dict of DataFrame
        A dictionary of countries and their production/imports, in kWh, for each production type.
    """

    raw_prod_dict = {}
    for target in parameters.target:
        if target == 'CH' and parameters.residual_local:
            if sg is None:
                raise ValueError("To compute the local residual, SwissGrid data must be provided.")
            # CH is a special case, because we need to add the local residual, which is not included in
            # the raw production and exchange data
            # We compute the net power consumption (production + import - export) at each time step
            # then we multiply it by the relative mix matrix to get the mix in kWh
            total_prod = sg.loc[:, 'Production_CH']
            imported = raw_prod_exch[[col for col in raw_prod_exch.columns if col.startswith(f'Mix_') and col.endswith(target)]].sum(axis=1)
            exported = raw_prod_exch[[col for col in raw_prod_exch if col.startswith(f'Mix_{target}')]].sum(axis=1)
            # todo what is good here
            total_consumption = total_prod + imported# - exported
            prod_df = mix_dict[target].multiply(total_consumption, axis=0)
            # Merge import sources together (to create 'Mix_XX_CH' columns)
            raw_prod_dict[target] = prod_df[[col for col in prod_df.columns if col.endswith(f'_{target}')]].copy()
            for c in parameters.ctry:
                if c != target:
                    raw_prod_dict[target][f'Mix_{c}'] = prod_df[[col for col in prod_df.columns if col.endswith(f'_{c}')]].sum(axis=1)
            raw_prod_dict[target][f'Mix_Other'] = prod_df['Mix_Other']
        else:
            # For other countries, the raw prod exchange data is already valid (there is no residual to add)
            # So we just get the right columns
            target_sources = [col for col in raw_prod_exch.columns if
                              col.endswith(target)]
            raw_prod_dict[target] = raw_prod_exch[target_sources]
    return raw_prod_dict


def translate_to_timezone(parameters: Parameter, raw_prod_dict: dict, mix_dict: dict, imp_dict: dict,
                          is_verbose: bool = False):
    """Translates the data to the right timezone.
    The data is modified in place.

    Parameters
    ----------
        parameters: ecodynelec.Parameter
            Parameters returned by load_config.
        raw_prod_dict: dict or None
            A dictionary of pandas.DataFrame, with the raw production data (in kWh) for each target.
            As returned by get_productions.
        mix_dict: dict or None
            A dictionary of pandas.DataFrame, with the mix for each target.
            As returned by get_mix.
        imp_dict: dict or None
            A dictionary containing the impacts for each target.
            As returned by get_impacts.
        is_verbose: bool, default to False
            To display progress information

    Returns
    -------
    (raw_prod_dict, mix_dict, imp_dict): tuple of dict
        The same dictionaries, with the data translated to the right timezone.
    """
    if parameters.timezone is not None:
        if is_verbose: print(f"Adapt timezone: UTC >> {parameters.timezone}")
        for target in parameters.target:
            if raw_prod_dict is not None:
                raw_prod_dict[target] = localize_from_utc(data=raw_prod_dict[target], timezone=parameters.timezone)
            if mix_dict is not None:
                mix_dict[target] = localize_from_utc(data=mix_dict[target], timezone=parameters.timezone)
            if imp_dict is not None:
                for k in imp_dict[target].keys():
                    imp_dict[target][k] = localize_from_utc(data=imp_dict[target][k], timezone=parameters.timezone)
    return raw_prod_dict, mix_dict, imp_dict


def save_results(parameters: Parameter, raw_prod_dict: dict = None, impact_matrix: pd.DataFrame = None,
                 mix_dict: dict = None, imp_dict: dict = None, is_verbose: bool = False):
    """Saves the results in the specified directory (parameters.path.savedir).

    Parameters
    ----------
    parameters: ecodynelec.Parameter
        Parameters returned by load_config.
    raw_prod_dict: dict or None
        A dictionary of pandas.DataFrame, with the raw production data (in kWh) for each target.
        As returned by get_productions.
    impact_matrix: pandas.DataFrame or None
        The impact matrix, as returned by load_impact_matrix.
    mix_dict: dict or None
        A dictionary of pandas.DataFrame, with the mix for each target, as returned by get_mix.
    imp_dict: dict or None
        A dictionary containing the impacts for each target, as returned by get_impacts.
    is_verbose: bool, default to False
        To display progress information
    """
    if parameters.path.savedir is not None:
        if is_verbose: print("Save data...")
        if parameters.path.mapping is not None and impact_matrix is not None:  # Impact vector saved only if use of Mapping xlsx
            saving.save_impact_vector(impact_matrix, savedir=parameters.path.savedir, cst_import=parameters.cst_imports,
                                      residual=np.logical_or(parameters.residual_global, parameters.residual_local))
        for country in parameters.target:
            path = os.path.abspath(f'{parameters.path.savedir}{country}/')
            if not os.path.isdir(path):
                os.makedirs(path)
            if raw_prod_dict is not None:
                saving.save_dataset(data=raw_prod_dict[country], savedir=f'{parameters.path.savedir}{country}/',
                                    name="RawProdExch",
                                    freq=parameters.freq)
            if mix_dict is not None:
                saving.save_dataset(data=mix_dict[country], savedir=f'{parameters.path.savedir}{country}/', name=f"Mix",
                                    freq=parameters.freq)
            if imp_dict is not None:
                imp = imp_dict[country]
                for k in imp:
                    saving.save_dataset(data=imp[k], savedir=f'{parameters.path.savedir}{country}/',
                                        name=f'Impact_{k.replace("_", "-")}', freq=parameters.freq)


def localize_from_utc(data: pd.DataFrame, timezone: str = 'CET'):
    """Converts the index of a dataframe from UTC to another time zone.

    :param data: table with TimeIndex, assumed to be UTC
    :type data: `pandas.DataFrame`
    :param timezone: the time zone to convert to, defaults to 'CET'
    :return: a table with shifted TimeIndex to the right time zone
    :rtype: `pandas.DataFrame`
    """
    return data.tz_localize(tz='utc').tz_convert(tz=timezone).tz_localize(None)
