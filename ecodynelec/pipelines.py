"""The `pipelines` module is the main module of `ecodynelec`.
It consists in a collection of high-level functions triggering
processes intricating most of the functions of the package.

This module contains:
    - execute: whole process from downloading / loading the data to the computation of impacts
    - get_inverted_matrix: process from downloading to track the electricity.
    - localize_from_utc: shifts the time-zone from results.
"""
import numpy as np
import pandas as pd
import os




# +
####### Local modules
from ecodynelec.parameter import Parameter

from ecodynelec.preprocessing.downloading import download
import ecodynelec.preprocessing.auxiliary as aux
from ecodynelec.preprocessing.load_impacts import extract_mapping, extract_UI
from ecodynelec.preprocessing.loading import import_data
from ecodynelec.preprocessing.residual import include_local_residual

from ecodynelec.tracking import track_mix
from ecodynelec.impacts import compute_impacts
from ecodynelec.checking import check_mapping

from ecodynelec import saving

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
    """

    ###########################
    ###### PARAMETER & VERIF
    ######
    if isinstance(config, Parameter): # If a parameter object
        p = config
    elif isinstance(config, str):
        if any([config.endswith(k) for k in ('.xlsx','.xls','.ods')]):
            p = Parameter(excel=config)
        else:
            raise NotImplementedError(f"File extension for {config} is not supported.")
    else:
        raise ValueError('Missing a configuration to pass parameters.')
        
    
    if np.logical_and(p.residual_global,p.residual_local):
        raise ValueError("Residual can not be both global and local.")
    
    ###########################
    ###### DOWNLOAD FROM SERVER
    ######
    if p.server.useServer:
        if None in [p.path.generation, p.path.exchanges]: # If one path was not given
            raise KeyError("Can not download files: missing path raw_generation and/or raw_exchange to save files.")
        if is_verbose: print("Download Entso-E data from server...")
        download(config=p, is_verbose=is_verbose) # Save files in a local dirrectory
        
    
    ###########################
    ###### LOAD DATASETS
    ######
    if is_verbose: print("Load auxiliary datasets...")
    # Load SwissGrid -> if Residual or SG exchanges
    if np.logical_or(np.logical_or(p.residual_global,p.residual_local), p.sg_imports):
        sg = aux.load_swissGrid(path_sg=p.path.swissGrid, start=p.start, end=p.end, freq=p.freq)
    else: sg=None

    # Load Country of interest -> Always
    neighbours = aux.load_useful_countries(path_neighbour=p.path.neighbours, ctry=p.ctry)

    # Load network losses -> if Network Loss asked
    if p.network_losses:
        network_losses = aux.load_grid_losses(network_loss_path=p.path.networkLosses, start=p.start, end=p.end)
    else: network_losses = None
        
    # Load production gap data -> if Residual
    if np.logical_or(p.residual_global,p.residual_local):
        prod_gap = aux.load_gap_content(path_gap=p.path.gap, start=p.start, end=p.end, freq=p.freq, header=59)
    else: prod_gap=None

    # Load impact matrix (UI vector by default)
    if p.path.mapping is not None: # Priority to the mapping spreadhseet, as soon as it is specified
        impact_matrix = extract_mapping(ctry=p.ctry, mapping_path=p.path.mapping, cst_import=p.cst_imports,
                                            residual=np.logical_or(p.residual_global, p.residual_local),
                                            target=p.target, is_verbose=is_verbose)
    
    else: # If no mapping specified, go for the UI vector: it can grab the default vector automatically
        impact_matrix = extract_UI(path_ui=p.path.ui_vector, ctry=p.ctry, target=p.target,
                                   cst_imports=p.cst_imports,
                                   residual=np.logical_or(p.residual_global, p.residual_local))
        
    

    # Load generation and exchange data from entso-e
    raw_prodExch = import_data(ctry=p.ctry, start=p.start, end=p.end, freq=p.freq, target=p.target,
                               involved_countries=neighbours, prod_gap=prod_gap, sg_data=sg,
                               path_gen=p.path.generation, path_imp=p.path.exchanges,
                               savedir=p.path.savedir, net_exchange=p.net_exchanges, 
                               residual_global=p.residual_global, correct_imp=p.sg_imports,
                               clean_data=p.data_cleaning, is_verbose=is_verbose)
    
    
    # Verify the adequacy between production and impacts
    check_mapping(mapping=impact_matrix, mix=raw_prodExch, strategy=missing_mapping)


    ########################
    ###### COMPUTE TRACKING
    ######
    mix = track_mix(raw_data=raw_prodExch, freq=p.freq, network_losses=network_losses,
                    target=p.target, residual_global=p.residual_global,
                    is_verbose=is_verbose)


    ##########################
    ####### ADD LOCAL RESIDUAL
    #######
    if p.residual_local:
        if is_verbose: print("Compute local residual...")
        local = [k for k in raw_prodExch.columns if k[-3:]==f'_{p.target}']
        mix = include_local_residual(mix_data=mix, sg_data=sg, local_prod=raw_prodExch.loc[:,local],
                                      gap=prod_gap, freq=p.freq)


    ############################
    ###### COMPUTE ELEC IMPACTS
    ######
    imp = compute_impacts(mix_data=mix, impact_data=impact_matrix,
                          strategy=missing_mapping, is_verbose=is_verbose)
    
    
    ###############################
    ###### TRANSLATE INTO TIMEZONE
    ######
    if p.timezone is not None:
        if is_verbose: print(f"Adapt timezone: UTC >> {p.timezone}")
        raw_prodExch = localize_from_utc(data=raw_prodExch, timezone=p.timezone)
        mix = localize_from_utc(data=mix, timezone=p.timezone)
        for k in imp:
            imp[k] = localize_from_utc(data=imp[k], timezone=p.timezone)
    
    
    ################################
    ####### SAVE DATA
    #######
    if p.path.savedir is not None:
        if is_verbose: print("Save data...")
        if p.path.mapping is not None: # Impact vector saved only if use of Mapping xlsx
            saving.save_impact_vector(impact_matrix, savedir=p.path.savedir, cst_import=p.cst_imports,
                                     residual=np.logical_or(p.residual_global,p.residual_local))
        saving.save_dataset(data=raw_prodExch, savedir=p.path.savedir, name="ProdExchange", freq=p.freq)
        saving.save_dataset(data=mix, savedir=p.path.savedir, name=f"Mix", target=p.target, freq=p.freq)
        for k in imp:
            saving.save_dataset(data=imp[k], savedir=p.path.savedir, name=f'Impact_{k.replace("_","-")}',
                         target=p.target, freq=p.freq)
    
    if is_verbose: print("done.")
    return imp

# +



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
    """

    ###########################
    ###### PARAMETER & VERIF
    ######
    if isinstance(config, Parameter): # If a parameter object
        p = config
    elif isinstance(config, str):
        if any([config.endswith(k) for k in ('.xlsx','.xls','.ods')]):
            p = Parameter(excel=config)
        else:
            raise NotImplementedError(f"File extension for {config} is not supported.")
    else:
        raise ValueError('Missing a configuration to pass parameters.')
        
    
    if np.logical_and(p.residual_global,p.residual_local):
        raise ValueError("Residual can not be both global and local.")
    
    ###########################
    ###### DOWNLOAD FROM SERVER
    ######
    if p.server.useServer:
        if None in [p.path.generation, p.path.exchanges]: # If one path was not given
            raise KeyError("Can not download files: missing path raw_generation and/or raw_exchange to save files.")
        if is_verbose: print("Download Entso-E data from server...")
        download(config=p, is_verbose=is_verbose) # Save files in a local dirrectory
    
    ###########################
    ###### LOAD DATASETS
    ######
    if is_verbose: print("Load auxiliary datasets...")
    # Load SwissGrid -> if Residual or SG exchanges
    if np.logical_or(np.logical_or(p.residual_global,p.residual_local), p.sg_imports):
        sg = aux.load_swissGrid(path_sg=p.path.swissGrid, start=p.start, end=p.end, freq=p.freq)
    else: sg=None

    # Load Country of interest -> Always
    neighbours = aux.load_useful_countries(path_neighbour=p.path.neighbours, ctry=p.ctry)

    # Load network losses -> if Network Loss asked
    if p.network_losses:
        network_losses = aux.load_grid_losses(network_loss_path=p.path.networkLosses, start=p.start, end=p.end)
    else: network_losses = None
        
    # Load production gap data -> if Residual
    if np.logical_or(p.residual_global,p.residual_local):
        prod_gap = aux.load_gap_content(path_gap=p.path.gap, start=p.start, end=p.end, freq=p.freq, header=59)
    else: prod_gap=None
    

    # Load generation and exchange data from entso-e
    raw_prodExch = import_data(ctry=p.ctry, start=p.start, end=p.end, freq=p.freq, target=p.target,
                               involved_countries=neighbours, prod_gap=prod_gap, sg_data=sg,
                               path_gen=p.path.generation, path_imp=p.path.exchanges,
                               savedir=p.path.savedir, net_exchange=p.net_exchanges, 
                               residual_global=p.residual_global, correct_imp=p.sg_imports,
                               clean_data=p.data_cleaning, is_verbose=is_verbose)
    
    
    ########################
    ###### COMPUTE TRACKING
    ######
    mix = track_mix(raw_data=raw_prodExch, freq=p.freq, network_losses=network_losses,
                    target=p.target, residual_global=p.residual_global,
                    return_matrix=True, is_verbose=is_verbose)
    
    if is_verbose: print("done.")
    return mix


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
