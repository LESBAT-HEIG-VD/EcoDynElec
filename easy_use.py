import numpy as np
import pandas as pd
import os




# +
####### Local modules
from parameter import Parameter

import load_data.auxiliary as aux
from load_data.impacts import extract_impacts
from load_data.generation_exchanges import import_data

from tracking import track_mix
from residual import include_local_residual
from impacts import compute_impacts

import saving

# +



#############################################
# ############################################
# Easy Execution of the whole algorithm
# ############################################
# ############################################

# +


def execute(p=None, excel=None, is_verbose=False):
    """
    Easy all-in-one execution of the algorighm, containing
    - the import of auxiliary data
    - the import and correction of Entso-E data (import from files)
    - the electricity tracking
    - the computation of the different impacts (GWP, CED, ES2013)
    - a data shift to the right time zone (initially all is in utc)
    - save the data into files
    
    Parameter:
        p: the parameter object (from class Parameter). Default: None
        excel: str to the excel file with parameters. Default: None
        is_verbose: bool to display information. Default: False
    
    Return:
        dict if pandas DataFrame with the impacts of 1kWh of electricity.
    
    """
    ###########################
    ###### PARAMETERS
    ######
    if p is None: # Load
        if excel is None:
            excel = aux.get_default_file(r'ExcelFile_default.xlsx')
        p = Parameter().from_excel(excel=excel)
    
    if np.logical_and(p.residual_global,p.residual_local):
        raise ValueError("Residual can not be both global and local.")
    
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

    # Load impact matrix
    impact_matrix = extract_impacts(ctry=p.ctry, mapping_path=p.path.mapping, cst_import=p.cst_imports,
                                    residual=np.logical_or(p.residual_global, p.residual_local),
                                    target=p.target, is_verbose=is_verbose)
    

    # Load generation and exchange data from entso-e    
    raw_prodExch = import_data(ctry=p.ctry, start=p.start, end=p.end, freq=p.freq, target=p.target,
                               involved_countries=neighbours, prod_gap=prod_gap, sg_data=sg,
                               path_gen=p.path.generation, path_imp=p.path.exchanges,
                               residual_global=p.residual_global, correct_imp=p.sg_imports,
                               is_verbose=is_verbose)




    ########################
    ###### COMPUTE TRACKING
    ######
    mix = track_mix(raw_data=raw_prodExch, freq=p.freq, network_losses=network_losses,
                    target=p.target, residual_global=p.residual_global,
                    net_exchange=p.net_exchanges, is_verbose=is_verbose)


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
    imp = compute_impacts(mix_data=mix, impact_data=impact_matrix, freq=p.freq, is_verbose=is_verbose)
    
    
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



#######################################
# ######################################
# Localize from UTC
# ######################################
# ######################################
# -

def localize_from_utc(data, timezone='CET'):
    """Converts the index of a dataset in utc to another time zone
    Parameter:
        data: pandas DataFrame with TimeIndex as index (time supposed to be in UTC)
        timezone: the timezone to convert in. (str, default: CET)
                See pandas time zones for more information.
    Return:
        pandas DataFrame"""
    return data.tz_localize(tz='utc').tz_convert(tz=timezone).tz_localize(None)
