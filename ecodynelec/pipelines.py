"""The `pipelines` module is the main module of `ecodynelec`.
It consists in a collection of high-level functions triggering
processes intricating most of the functions of the package.

This module contains:
    - execute: whole process from downloading / loading the data to the computation of impacts
    - get_inverted_matrix: process from downloading to track the electricity.
    - localize_from_utc: shifts the time-zone from results.
"""
import pandas as pd
from IPython.core.display_functions import display
from ipywidgets import IntProgress

from ecodynelec.preprocessing.residual import import_residual

from ecodynelec.checking import check_mapping
# +
####### Local modules
from ecodynelec.pipeline_functions import load_config, check_download, load_raw_prod_exchanges, get_mix, get_impacts, \
    translate_to_timezone, save_results, load_impact_matrix
from ecodynelec.progress_info import ProgressInfo


# +


#############################################
# ############################################
# Easy Execution of the whole algorithm
# ############################################
# ############################################

# +


def execute(config, missing_mapping='error', is_verbose=False):
    """Executes the whole computation process, i.e. (1) downloads required data;
    (2) load auxiliary data; (3) load and correct Entso-E data; (4) compute the 
    electricity tracking; (5) computes the environmental impacts; (6) save and return.
    
    Parameters
    ----------
        config: ecodynelec.Parameter or str
            a set of configuration parameters to govern the computation,
            either as Parameter object or str pointing at an xlsx file.
        missing_mapping: str, default to 'error'
            strategy for handling producing units with not mapping.
            'error' (default) raises an error, 'worst' takes the highest impact value in
            the available set, 'unit' takes the highest impact value available from a 
            similar unit type, defaults to 'error'
        is_verbose: bool, default to False
            to display information, defaults to False

    Returns
    -------
    dict
        a collection of tables containing the dynamic impacts of 1kWh of electricity
    """

    ###########################
    ###### PARAMETER & VERIF
    ######
    p = load_config(config)
    n_target = len(p.target)

    ###########################
    ###### DOWNLOAD FROM SERVER
    ######
    check_download(parameters=p, is_verbose=is_verbose)

    ###########################
    ###### LOAD DATASETS
    ######
    raw_prodExch, prod_gap, sg = load_raw_prod_exchanges(parameters=p, is_verbose=is_verbose)

    impact_matrix = load_impact_matrix(parameters=p, is_verbose=is_verbose)

    # Verify the adequacy between production and impacts
    check_mapping(mapping=impact_matrix, mix=raw_prodExch, strategy=missing_mapping)

    ########################
    ###### COMPUTE TRACKING
    ######
    mix_dict = get_mix(p, raw_prodExch, sg, prod_gap, is_verbose=is_verbose)

    return mix_dict
    # print('Before', raw_prodExch.columns)
    # raw_mix = raw_mix.drop(raw_mix.loc[:, [not k[-2:] in p.target for k in raw_mix.columns]],
    #         axis=1)  # Keep only the production columns
    # print('After', raw_prodExch.columns)

    ##########################
    ####### ADD LOCAL RESIDUAL
    #######

    ############################
    ###### COMPUTE ELEC IMPACTS
    ######
    imp_dict = get_impacts(p, mix_dict, impact_matrix, missing_mapping, is_verbose=is_verbose)

    ###############################
    ###### TRANSLATE INTO TIMEZONE
    ######
    _, _, imp_dict = translate_to_timezone(p, raw_prod_exch=None, mix_dict=None, imp_dict=imp_dict, is_verbose=is_verbose)

    ################################
    ####### SAVE DATA
    #######
    save_results(p, impact_matrix=impact_matrix, imp_dict=imp_dict, is_verbose=is_verbose)

    if is_verbose: print("done.")
    if n_target == 1:
        return imp_dict[p.target[0]]
    return imp_dict


########################################
# ######################################
# Aymeric's new pipeline
# ######################################
# ######################################
# -

def get_prod_mix_impacts(config, missing_mapping='error', is_verbose=False, progress_bar: ProgressInfo=None):
    """Executes the whole computation process, i.e. (1) downloads required data;
    (2) load auxiliary data; (3) load and correct Entso-E data; (4) compute the
    electricity tracking; (5) computes the environmental impacts; (6) save and return.

    Parameters
    ----------
        config: ecodynelec.Parameter or str
            a set of configration parameters to govern the computation,
            either as Parameter object or str pointing at an xlsx file.
        missing_mapping: str, default to 'error'
            strategy for handling producing units with not mapping.
            'error' (default) raises an error, 'worst' takes the highest impact value in
            the available set, 'unit' takes the highest impact value available from a
            similar unit type, defaults to 'error'
        is_verbose: bool, default to False
            to display information, defaults to False

    Returns
    -------
    dict
        a collection of tables containing the dynamic impacts of 1kWh of electricity
        todo explain
    """

    if progress_bar:
        progress_bar.set_max_value(11)
        progress_bar.progress('Load config...', 0)

    ###########################
    ###### PARAMETER & VERIF
    ######
    p = load_config(config)
    n_target = len(p.target)

    ###########################
    ###### DOWNLOAD FROM SERVER
    ######
    if progress_bar:
        progress_bar.progress('Download from ENTSO-E...')
    check_download(parameters=p, is_verbose=is_verbose)

    ###########################
    ###### LOAD DATASETS
    ######
    if progress_bar:
        progress_bar.progress('Load raw prods...')
    raw_prodExch, prod_gap, sg = load_raw_prod_exchanges(parameters=p, is_verbose=is_verbose, progress_bar=progress_bar)

    # Group raw production (and import) mixes by target
    # raw_prod_dict = {}
    # for target in p.ctry:
    #     target_dict = {col: raw_prodExch[col] for col in raw_prodExch.columns if col.endswith(target)}
    #     raw_prod_dict[target] = pd.DataFrame.from_dict(target_dict)
    if progress_bar:
        progress_bar.progress('Load impact matrix...')
    impact_matrix = load_impact_matrix(parameters=p, is_verbose=is_verbose)

    # Verify the adequacy between production and impacts
    check_mapping(mapping=impact_matrix, mix=raw_prodExch, strategy=missing_mapping)

    ########################
    ###### COMPUTE TRACKING
    ######
    if progress_bar:
        progress_bar.progress('Compute mix tracking...')
    mix_dict = get_mix(p, raw_prodExch, sg, prod_gap, is_verbose=is_verbose)

    ############################
    ###### COMPUTE ELEC IMPACTS
    ######
    if progress_bar:
        progress_bar.progress('Compute impacts...')
    imp_dict = get_impacts(p, mix_dict, impact_matrix, missing_mapping, is_verbose=is_verbose)

    ##########################
    ####### COMPUTE MIX IN kWh
    #######

    if progress_bar:
        progress_bar.progress('Compute mix in kWh...')
    # Drop non-production lines of the mix (i.e. the first part of the mix matrix)
    for mix in mix_dict.keys():
        mix_dict[mix] = mix_dict[mix].drop(mix_dict[mix].loc[:, [k.startswith('Mix') and not k.endswith('Other') for k in mix_dict[mix].columns]],
          axis=1).astype('float32')

    # Compute the total consumption of each country
    # We compute the net power consumption (production + import - export) for each country at each time step
    # then we multiply it by the relative mix matrix to get the mix in kWh
    # todo add function in pipeline_functions
    raw_prod_dict = {}
    for target in p.target:
        if target == 'CH':
            ch_sources = [col for col in raw_prodExch.columns if col.endswith(target)]
            total_consumption = raw_prodExch[ch_sources].sum(axis=1)
            export = raw_prodExch[[col for col in raw_prodExch if col.startswith(f'Mix_{target}')]].sum(axis=1)
            total_consumption = total_consumption - export
            # If residual_local is True, the residual is not yet included in the total consumption
            if target == 'CH' and config.residual_local and sg is not None:
                # see residual.import_residual
                local_sources = [col for col in ch_sources if not col.startswith('Mix_')]
                residual = sg.loc[:,'Production_CH'] - raw_prodExch[local_sources].sum(axis=1)
                total_consumption = total_consumption + residual
            raw_prod_dict[target] = mix_dict[target].multiply(total_consumption, axis=0)
        else:
            ch_sources = [col for col in raw_prodExch.columns if col.endswith(target) and not col.startswith('Mix')]
            raw_prod_dict[target] = raw_prodExch[ch_sources]

    ###############################
    ###### TRANSLATE INTO TIMEZONE
    ######
    if progress_bar:
        progress_bar.progress('Save data...')
    raw_prodExch, mix_dict, imp_dict = translate_to_timezone(p, raw_prodExch, mix_dict, imp_dict, is_verbose=is_verbose)

    ################################
    ####### SAVE DATA
    #######
    save_results(p, raw_prod_dict, impact_matrix, mix_dict, imp_dict, is_verbose=is_verbose)

    if progress_bar:
        progress_bar.progress('Done.')
    if is_verbose: print("done.")
    if n_target == 1:
        return raw_prod_dict[p.target[0]], mix_dict[p.target[0]], imp_dict[p.target[0]]
    return raw_prod_dict, mix_dict, imp_dict


########################################
# ######################################
# Get inverted matrix
# ######################################
# ######################################
# -
def get_inverted_matrix(config=None, is_verbose=False):
    """Triggers the computation process until the electricity tracking to return the
    electricity mix in all involved coutries. No data saving is involved.
    
    :param config: a set of parameters to govern the computation, defaults to None
    :type config: class:`ecodynelec.Parameter`, optional
    :param is_verbose: to display information, defaults to False
    :type is_verbose: bool, optional
    :return: a collection of tables containing the decomposition of 1kWh of electricity
    :rtype: dict of `pandas.DataFrame`
    TODO UPDATE DOC
    """

    ###########################
    ###### PARAMETER & VERIF
    ######
    p = load_config(config)

    ###########################
    ###### DOWNLOAD FROM SERVER
    ######
    check_download(parameters=p, is_verbose=is_verbose)

    ###########################
    ###### LOAD DATASETS
    ######
    raw_prodExch, prod_gap, sg = load_raw_prod_exchanges(parameters=p, is_verbose=is_verbose)

    ########################
    ###### COMPUTE TRACKING
    ######
    mix_df = get_mix(p, raw_prodExch, sg, prod_gap, return_matrix=True, is_verbose=is_verbose)

    if is_verbose: print("done.")
    return mix_df


# +

#######################################
# ######################################
# Localize from UTC
# ######################################
# ######################################
# -

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
