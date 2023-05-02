"""This module contains the functions to run the `pipeline` module

This module contains:
    - load_config: loads the configuration parameters.
    - check_download: checks if the entso-e data needs to be downloaded.
    - load_raw_prod_exchanges: loads the raw production and exchanges data.
    - load_impact_matrix: loads the impact matrix.
    - check_mapping: checks the mapping between production and impacts.
    - get_mix: computes the electric mix of the target countries.
    - get_impacts: computes the impacts of these mixs.
    - translate_to_timezone: translates the data into the timezone.
    - save_results: saves the results.
    - localize_from_utc: shifts the time-zone from results.
"""
import os.path

import numpy as np

from ecodynelec import saving
from ecodynelec.impacts import compute_impacts
from ecodynelec.parameter import Parameter
from ecodynelec.preprocessing import auxiliary as aux
from ecodynelec.preprocessing.downloading import download
from ecodynelec.preprocessing.load_impacts import extract_mapping, extract_UI
from ecodynelec.preprocessing.loading import import_data
from ecodynelec.preprocessing.residual import include_local_residual
from ecodynelec.progress_info import ProgressInfo
from ecodynelec.tracking import track_mix


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


def check_download(parameters, is_verbose=False):
    """Checks if the config requires to download the entso-e data, and if so, downloads it.
    Parameters
    ----------
        parameters: ecodynelec.Parameter
            a set of configuration parameters to govern the computation.
        is_verbose: bool, default to False
            to display information, defaults to False
    """
    if parameters.server.useServer:
        if None in [parameters.path.generation, parameters.path.exchanges]:  # If one path was not given
            raise KeyError("Can not download files: missing path raw_generation and/or raw_exchange to save files.")
        if is_verbose: print("Download Entso-E data from server...")
        download(config=parameters, is_verbose=is_verbose)  # Save files in a local dirrectory


def load_raw_prod_exchanges(parameters, is_verbose=False, progress_bar: ProgressInfo=None):
    """Loads the raw production and exchange data from entso-e.
    Parameters
    ----------
        parameters: ecodynelec.Parameter
            a set of configuration parameters to govern the computation.
        is_verbose: bool, default to False
            to display information, defaults to False
    Returns
    -------
    A tuple of three pandas.DataFrame:
    praw_prodExch: DataFrame with all productions and all exchanges from all included countries.
    prod_gap: information about the nature of the residual
    sg_data: information from Swiss Grid
    """
    p = load_config(parameters)
    check_download(p, is_verbose=is_verbose)

    if progress_bar:
        progress_bar.set_sub_label('Load auxiliary datasets...')
    # Load SwissGrid -> if Residual or SG exchanges
    if np.logical_or(np.logical_or(p.residual_global, p.residual_local), p.sg_imports):
        sg_data = aux.load_swissGrid(path_sg=p.path.swissGrid, start=p.start, end=p.end, freq=p.freq)
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
    raw_prodExch = import_data(ctry=p.ctry, start=p.start, end=p.end, freq=p.freq, involved_countries=neighbours,
                               prod_gap=prod_gap, sg_data=sg_data,
                               path_gen=p.path.generation, path_imp=p.path.exchanges,
                               savedir=p.path.savedir, net_exchange=p.net_exchanges,
                               residual_global=p.residual_global, correct_imp=p.sg_imports,
                               clean_data=p.data_cleaning, is_verbose=is_verbose, progress_bar=progress_bar)
    return raw_prodExch, prod_gap, sg_data


def load_impact_matrix(parameters, is_verbose=False):
    """Loads the impact matrix from the specified parameters.
    Parameters
    ----------
        parameters: ecodynelec.Parameter
            a set of configuration parameters to govern the computation.
        is_verbose: bool, default to False
            to display information, defaults to False
        Returns
        -------
        impact_matrix: pandas.DataFrame
            The impact matrix.
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


def get_mix(parameters, raw_prodExch, sg_data, prod_gap, return_matrix=False, is_verbose=False):
    """Loads the mix from the specified parameters.
    Also includes the local residual if return_matrix is False and parameters.residual_local is True.
    TODO USE DOC FROM TRACKING
    Parameters
    ----------
        parameters: ecodynelec.Parameter
            a set of configuration parameters to govern the computation.
        raw_prodExch: pandas.DataFrame
            The raw production and exchange data.
        sg_data: pandas.DataFrame
            The SwissGrid data.
        prod_gap: pandas.DataFrame
            The production gap data.
        return_matrix: bool, default to False
            If True, returns the mix matrix instead of the mix dictionary.
        is_verbose: bool, default to False
            to display information, defaults to False
        Returns
    -------
    mix_dict: dict
        A dictionary of pandas.DataFrame, with the mix for each target.
    mix_matrix: pandas.DataFrame
        The mix matrix.
    """
    # Load network losses -> if Network Loss asked
    if parameters.network_losses:
        network_losses = aux.load_grid_losses(network_loss_path=parameters.path.networkLosses, start=parameters.start,
                                              end=parameters.end)
    else:
        network_losses = None

    mix_df = track_mix(raw_data=raw_prodExch, freq=parameters.freq, network_losses=network_losses,
                       residual_global=parameters.residual_global,
                       is_verbose=is_verbose)
    if not return_matrix:
        mix_dict = {}
        for target in parameters.target:
            mix_dict[target] = mix_df[f'Mix_{target}'].unstack()

        if parameters.residual_local:
            if is_verbose: print("Compute local residual...")
            for target in parameters.target:
                local = [k for k in raw_prodExch.columns if k[-3:] == f'_{target}']
                mix_dict[target] = include_local_residual(mix_data=mix_dict[target], sg_data=sg_data,
                                                          local_prod=raw_prodExch.loc[:, local],
                                                          gap=prod_gap, freq=parameters.freq, target=target)
        return mix_dict
    return mix_df


def get_impacts(p, mix_dict, impact_matrix, missing_mapping='error', is_verbose=False):
    """Computes the impact of the given electrical mix.
    Parameters
    ----------
        p: ecodynelec.Parameter
            a set of configuration parameters to govern the computation.
        mix_dict: dict
            A dictionary of pandas.DataFrame, with the mix for each target.
        impact_matrix: pandas.DataFrame
            The impact matrix.
        missing_mapping: str, default to 'error'
            strategy for handling producing units with not mapping.
            'error' (default) raises an error, 'worst' takes the highest impact value in
            the available set, 'unit' takes the highest impact value available from a
            similar unit type, defaults to 'error'
        is_verbose: bool, default to False
            to display information, defaults to False
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


def translate_to_timezone(p, raw_prod_exch, mix_dict, imp_dict, is_verbose=False):
    """Translates the data to the right timezone.
    Parameters
    ----------
        p: ecodynelec.Parameter
            a set of configuration parameters to govern the computation.
        raw_prod_exch: pandas.DataFrame or None
            The raw production and exchange data.
        mix_dict: dict or None
            A dictionary of pandas.DataFrame, with the mix for each target.
        imp_dict: dict or None
            A dictionary containing the impacts for each target.
        is_verbose: bool, default to False
            to display information, defaults to False
    Returns
    -------
    raw_prod_exch: pandas.DataFrame
        The raw production and exchange data.
    mix_dict: dict
        A dictionary of pandas.DataFrame, with the mix for each target.
    imp_dict: dict
        A dictionary containing the impacts for each target.
    """
    if p.timezone is not None:
        if is_verbose: print(f"Adapt timezone: UTC >> {p.timezone}")
        if raw_prod_exch is not None:
            raw_prod_exch = localize_from_utc(data=raw_prod_exch, timezone=p.timezone)
        for target in p.target:
            if mix_dict is not None:
                mix_dict[target] = localize_from_utc(data=mix_dict[target], timezone=p.timezone)
            if imp_dict is not None:
                for k in imp_dict[target].keys():
                    imp_dict[target][k] = localize_from_utc(data=imp_dict[target][k], timezone=p.timezone)
    return raw_prod_exch, mix_dict, imp_dict


def save_results(p, raw_prod_dict=None, impact_matrix=None, mix_dict=None, imp_dict=None, is_verbose=False):
    # BUT CHANGE FORMAT OF mix_dict and imp_dict to dataframes

    if p.path.savedir is not None:
        if is_verbose: print("Save data...")
        if p.path.mapping is not None and impact_matrix is not None:  # Impact vector saved only if use of Mapping xlsx
            saving.save_impact_vector(impact_matrix, savedir=p.path.savedir, cst_import=p.cst_imports,
                                      residual=np.logical_or(p.residual_global, p.residual_local))
        for country in p.target:
            path = os.path.abspath(f'{p.path.savedir}{country}/')
            if not os.path.isdir(path):
                os.makedirs(path)
            if raw_prod_dict is not None:
                saving.save_dataset(data=raw_prod_dict[country], savedir=f'{p.path.savedir}{country}/', name="RawProdExch",
                                    freq=p.freq)
            if mix_dict is not None:
                saving.save_dataset(data=mix_dict[country], savedir=f'{p.path.savedir}{country}/', name=f"Mix", freq=p.freq)
            if imp_dict is not None:
                imp = imp_dict[country]
                for k in imp:
                    saving.save_dataset(data=imp[k], savedir=f'{p.path.savedir}{country}/',
                                        name=f'Impact_{k.replace("_", "-")}', freq=p.freq)
    return


def localize_from_utc(data, timezone='CET'):
    """Converts the index of a dataframe from UTC to another time zone.

    :param data: table with TimeIndex, assumed to be UTC
    :type data: `pandas.DataFrame`
    :param timezone: the time zone to convert to, defaults to 'CET'
    :return: a table with shifted TimeIndex to the right time zone
    :rtype: `pandas.DataFrame`
    """
    # """Converts the index of a dataset in utc to another time zone
    # Parameter:
    #     data: pandas DataFrame with TimeIndex as index (time supposed to be in UTC)
    #     timezone: the timezone to convert in. (str, default: CET)
    #             See pandas time zones for more information.
    # Return:
    #     pandas DataFrame"""
    return data.tz_localize(tz='utc').tz_convert(tz=timezone).tz_localize(None)
