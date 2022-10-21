import numpy as np
import pandas as pd
import os
from time import time

#################### Local functions
from dynamical.checking import check_frequency, check_regularity_frequency
from dynamical.residual import include_global_residual
from dynamical.load_data.raw_entsoe import extract
from dynamical.load_data.autocomplete import get_steps_per_hour


# +
# Module to load production and cross-border flows from Entso-E

# +

#####################################
# ####################################
# IMPORT DATA
# ####################################
# ####################################

# -

def import_data(ctry, start=None, end=None, freq="H", target="CH",
                involved_countries=None, prod_gap=None, sg_data=None, net_exchange=False,
                path_gen=None, path_gen_raw=None, path_imp=None, path_imp_raw=None, savedir=None,
                residual_global=False, correct_imp=True,
                clean_data=True, n_hours=2, days_around=7, limit=.4, is_verbose=True):
    
    """
    Main function managing the import and pre-treatment of Entso-e production and cross-border flow data.
    
    Patameter:
        ctry: list of countries to include in the computing (list)
        start: starting date (str or datetime)
        end: ending date (str or datetime)
        freq: time step (str, default: H)
        target: target country (str, default: CH)
        involved_countries: list of all countries involved, with the countries to include in the computing
                            and their neighbours (to implement the exchanges with 'Other' countries)
                            (list, default: None)
        prod_gap: information about the nature of the residual (pandas DataFrame)
        sg_data: information from Swiss Grid (pandas DataFrame, default: None)
        net_exchange: to simplify cross-border flows to net after resampling (bool, default False)
        path_gen: directory where preprocessed Entso-e generation files are stored (str)
        path_imp: directory containing the files for preprocessed cross-border flow data (str)
        path_gen_raw: directory where raw Entso-e generation files are stored (str)
        path_imp_raw: directory containing the raw Entso-E files for cross-border flow data (str)
        savedir: directory to save auxilary information for loaded data (str, default: None)
        savegen: directory to save generation data from raw files (str, default: None)
        saveimp: directory to save exchanges data from raw files (str, default: None)
        residual_global: to consider the production residual as produced electricity that can be
                        exchanged with neighbour countries (bool, default: False)
        correct_imp: to replace cross-border flow of Entso-e for Swizerland with data from Swiss Grid
                    (bool, default: False)
        clean_generation: to enable automatic data cleaning / filling (bool, default: True)
        n_hours: Max number of successive missing hours to be considered as occasional event
                (int, default: 2)
        days_around: number of days after and before a gap to consider to create a 'typical mean day'
                (int, default: 7)
        is_verbose: to display information (bool, default: False)
    
    Return:
        pandas DataFrame with all productions and all exchanges from all included countries.
    """
    
    t0 = time()
    
    ### GENERATION DATA
    Gen = import_generation(path_gen=path_gen, path_raw=path_gen_raw, ctry=ctry, start=start, end=end,
                            savedir=savedir, n_hours=n_hours, days_around=days_around, limit=limit,
                            clean_generation=clean_data, is_verbose=is_verbose) # import generation data
    Gen = adjust_generation(Gen, freq=freq, residual_global=residual_global, sg_data=sg_data,
                            prod_gap=prod_gap, is_verbose=is_verbose) # adjust the generation data
    
    ### EXCHANGE DATA
    Cross = import_exchanges(ctry=ctry, start=start, end=end, savedir=savedir,
                             n_hours=n_hours, days_around=days_around, limit=limit, clean_imports=clean_data,
                             path_imp=path_imp, path_raw=path_imp_raw, freq=freq, is_verbose=is_verbose) # Imprt data
    
    Cross = adjust_exchanges(Cross=Cross, neighbourhood=involved_countries, net_exchange=net_exchange, freq=freq,
                             sg_data=sg_data if correct_imp else None, is_verbose=is_verbose)
    
    ### GATHER GENERATION AND EXCHANGE
    electric_mix = _join_generation_exchanges(Gen=Gen, Cross=Cross, is_verbose=is_verbose)
    
    
    if is_verbose: print("Import of data: {:.1f} sec".format(time()-t0))
    return electric_mix


# +

#####################################
# ####################################
# Import Generation
# ####################################
# ####################################

# -

def import_generation(ctry, start, end, path_gen=None, path_raw=None, savedir=None,
                      n_hours:int=2, days_around:int=7, limit:float=.4, clean_generation:bool=True,
                      is_verbose=False):
    """
    Function to import generation data from Entso-e information source.
    
    Parameter:
        path_gen: directory where preprocessed Entso-e generation files are stored (str) [prioritary path]
        path_gen_raw: directory where raw Entso-e generation files are stored (str) [secondary path]
        ctry: countries to incldue in the study (list)
        start: starting date (str or datetime)
        end: ending date (str or datetime)
        savedir: directory path to save auxilary results (str, default: None)
        savegen: directory path to save generation files (str, if path_raw not None, default: None)
        is_verbose: to display information (bool, default: False)
    """
    path, savegen = None, None
    if ((path_raw is None)&(path_gen is None)):
        raise KeyError("No path is given for Generation data.")
    elif ((path_raw is None)&(path_gen is not None)): # Got a file prepared
        path = path_gen # Then use prepared file
    elif ((path_raw is not None)&(path_gen is None)): # Need raw file
        path = path_raw # Then use raw file
    else: # Both are not None
        path, savegen = path_raw, path_gen # Then use raw and save in path_gen.
    
    #######################
    ###### Generation data
    #######################

    if is_verbose: print("Load generation data...")
    # Selecton of right files according to the choice of countres
    if path==path_gen:
        files = {}
        for c in ctry: # Gather prepared files per country
            try:
                files[c] = [f for f in os.listdir(path) if f.find(c)!=-1][0]
            except Exception as e:
                raise KeyError(f"No generation data for {c}: {e}")
                
        Gen = {} # Dict for the generation of each country
        
    elif path==path_raw: # Just fill the Gen directly for row files
        Gen = extract(ctry=ctry, dir_gen=path, savedir_gen=savegen, save_resolution=savedir,
                      n_hours=n_hours, days_around=days_around, limit=limit, correct_imp=clean_generation,
                      is_verbose=is_verbose) # if from raw files

    for c in ctry:# Preprocess all files / data per country
        # Extract the generation data file
        if path==path_gen: # Load preprocessed files
            Gen[c] = pd.read_csv(path+files[c],index_col=0) # Extraction of preprocessed files
        
        # Check and modify labels if needed
        add_space = pd.Index(np.array([k[-1] for k in Gen[c].columns])!=[' ']) # all cols not ending with ' '
        Gen[c].columns = Gen[c].columns + add_space*" " # get an additional ' ' at the end
            
        # Set indexes to time data
        Gen[c].index = pd.to_datetime(Gen[c].index,yearfirst=True) # Convert index into datetime
        
        # Only select the required piece of information
        Gen[c] = Gen[c].loc[start:end]

        source = list(Gen[c].columns) # production plants types
        source[source.index("Other ")] = "Other fossil " # rename one specific column (space at the end is important !)

        Gen[c].columns = [s.replace(" ","_")+c for s in source] # rename columns
        
    return Gen


# +

#####################################
# ####################################
# Adjust Generation
# ####################################
# ####################################

# -

def adjust_generation(Gen, freq='H', residual_global=False,
                      sg_data=None, prod_gap=None, is_verbose=False):
    """Function that leads organizes the data adjustment.
    It sorts finds and sorts missing values, fills it, resample the data and
    add a residual as global production
    
    Parameter:
        Gen: dict of dataFrames containing the generation for each country
        freq: time step durtion (str, default: H)
        residual_prod: whether to include the residual or not (bool, default: False)
        sg_data: information from Swiss Grid (pandas DataFrame, default: None)
        clean_generation: to enable automatic data cleaning / filling (bool, default: True)
        n_hours: Max number of successive missing hours to be considered as occasional event
                (int, default: 2)
        days_around: number of days after and before a gap to consider to create a 'typical mean day'
                (int, default: 7)
        prod_gap: information about the nature of the residual (pandas DataFrame)
        is_verbose: bool. Whether to display information or not.
        
    Return
        dict of pandas DataFrames: modified Gen dict.
    """
    ### Resample data to the right frequence
    if is_verbose: print(f"\t4/{4+int(residual_global)} - Resample exchanges to {freq} steps...")
    Gen = resample_data(Gen, freq=freq, case='gen')
    # print("===========\nGENERATION\n===========")
    # print(Gen)
    
    ### Includes residual production
    if residual_global:
        Gen = include_global_residual(Gen=Gen, freq=freq, sg_data=sg_data, prod_gap=prod_gap,
                                       is_verbose=is_verbose)
    
    return Gen


# +

#####################################
# ####################################
# Resample generation
# ####################################
# ####################################

# -

# def resample_generation(Gen, freq, add_on=False, is_verbose=False):
#     """
#     Function that resamples the generation data. It can only downsample (lower the resolution) by summing.
    
#     Parameter:
#         Gen: dict of DataFrames containing the generation data.
#         freq: the time step (resolution)
#         add_on: a display flourish (bool, default: False)
#         is_verbose: to display information (bool, default: False)
    
#     Return:
#         dict of pandas DataFrame wiht resampled productions
#     """
#     #######################
#     ###### Resample Gen.
#     #######################
#     if ((check_frequency(freq))&(freq!='15min')):
#         if is_verbose: print(f"\t4/{4+int(add_on)} - Resample Generation data to {freq} steps...")
#         for f in Gen.keys(): # For all countries
#             Gen[f] = Gen[f].resample(freq).sum() # Sum as we talk about energy.
            
#     return Gen


# +

#####################################
# ####################################
# Import Exchanges
# ####################################
# ####################################

# -

def import_exchanges(ctry, start, end, path_imp=None, path_raw=None, savedir=None, freq='H',
                     n_hours:int=2, days_around:int=7, limit:float=.4, clean_imports:bool=True,
                     is_verbose=False):
    """
    Function to import the cross-border flows.
    Finds the useful files to load, load the data, group relevant information and adjust time step.
    
    Parameter:
        path_imp: directory containing the files for cross-border flow data (str)
        neighbours: list of useful countries, including neighbour of involved countries (list)
        ctry: list of countries to be represented in the simulation
        start: starting date (str or datetime)
        end: ending date (str or datetime)
        freq: time step (str, default: H)
        is_verbose: display information (bool, default: False)
    """
    path, saveimp = None, None
    if ((path_raw is None)&(path_imp is None)):
        raise KeyError("No path is given for Generation data.")
    elif ((path_raw is None)&(path_imp is not None)): # Got a file prepared
        path = path_imp # Then use prepared file
    elif ((path_raw is not None)&(path_imp is None)): # Need raw file
        path = path_raw # Then use raw file
    else: # Both are not None
        path, saveimp = path_raw, path_imp # Then use raw and save in path_imp.
    
    if is_verbose: print("Get and reduce importation data...")
        
    ### Files to consider
    if path==path_imp:
        files = {}
        for c in ctry:
            try:
                files[c] = [f for f in os.listdir(path_imp) if f.find(c)!=-1][0]
            except Exception as e:
                raise KeyError(f"No exchange data for {c}: {e}")
                
        Cross = {} # Dict for the generation of each country
        
    elif path==path_raw: # Just fill the Gen directly for row files
        Cross = extract(ctry=ctry, dir_imp=path, savedir_imp=saveimp,save_resolution=savedir,
                        n_hours=n_hours, days_around=days_around, limit=limit, correct_imp=clean_imports,
                        is_verbose=is_verbose) # if from raw files

    
    for i,c in enumerate(ctry):# File extraction
        if path==path_imp:
            if is_verbose: print("\t{}/{} - {}...".format(i+1,len(files),c))
            Cross[c] = pd.read_csv(path_imp+files[c],index_col=0) # Extraction

        # Transform index in time data, then keeps only period of interest
        Cross[c].index = pd.to_datetime(Cross[c].index,yearfirst=True) # Considered period only
        Cross[c] = Cross[c].loc[start:end] # select right period
            
    return Cross


# +

#####################################
# ####################################
# Adjust exchanges
# ####################################
# ####################################

# -

def adjust_exchanges(Cross, neighbourhood, net_exchange=False, freq='H', sg_data=None, is_verbose=False):
    """
    Bring adjustments to the exchange data: add SwissGrid data, fill data,
    adjust frequency and set exchanges to net.
    
    Parameter:
        Cross: the Cross-border flow data (dict of pandas DataFrame)
        net_exchange: to consider net cross-border flows (bool, default False)
        sg_data: information from Swiss Grid (pandas DataFrame)
        freq: time step (str, default: H)
    
    Return:
        dict of pandas DataFrame with adjusted cross-border flow data.
    """
    ### ADJUST THE FREQUENCY AND CONVERT TO MWh
    if is_verbose: print(f"Resample exchanges to {freq} steps...")
    Cross = resample_data(Cross, freq=freq, case='imp')
        
    ### ADJUST WITH SWISSGRID DATA (AT SWISS BORDER ONLY)
    if sg_data is not None: # Adjust with SG data
        Cross = set_swissGrid(Cross, sg_data)
    
    ### CREATE THE 'OTHER' AND REMOVE UNUSED
    for c in Cross:
        other = [k for k in neighbourhood if k not in Cross.keys()] # Label as 'other' all non-main selected countries
        Cross[c]['Other'] = Cross[c].loc[:,other].sum(axis=1).copy() # Add the aggregated 'Other'
        
        involved = [k for k in neighbourhood if k in Cross.keys()] + ['Other'] # All neighbours involved in computation
        Cross[c] = Cross[c].loc[:,involved] # Select only relevant information
        Cross[c] = Cross[c].rename(columns=lambda s:f"Mix_{s}_{c}") # Rename columns
    
    
    ### DEAL WITH NET-RAW EXCHANGES
    if net_exchange:
        Cross = create_net_exchange(Cross)
        
    return Cross
        


#
###############################################################################
# ###########################
# # Set SwissGrid at Swiss border
# ###########################
# ###########################
#

def set_swissGrid(Cross, sg_data):
    """
    Function to replace the cross-border flow data of ENTSO-E by the cross-border flow data of SwissGrid. Data passed must be in 15min.
    
    Parameter:
        Cross: the Cross-border flow data (dict of pandas DataFrame)
        sg_data: information from Swiss Grid (pandas DataFrame)
    
    Return:
        dict of pandas DataFrame with cross-border flow data for all the countries of the studied area.
    """    
    #### Replace the data in the DataFrames
    places = ["AT","DE","FR","IT"] # Neighbours of Swizerland (as the function is only for Swizerland)
    
    for c in places:
        if f"Mix_{c}_CH" in Cross['CH'].columns:
            Cross["CH"].loc[:,f"Mix_{c}_CH"] = sg_data.loc[:,f"Mix_{c}_CH"] # Swiss imprts
        if c in Cross.keys():
            Cross[c].loc[:,f"Mix_CH_{c}"] = sg_data.loc[:,f"Mix_CH_{c}"] # Swiss exports
    
    return Cross


#
###############################################################################
# ###########################
# # Create net exchanges
# ###########################
# ###########################
#

def create_net_exchange(Cross):
    """
    Adapt the cross-border flow to consider exchanges at each border and time step as net.
    Net exchange means that electricity can only go from A to B or from B to A, but not in 
    both directions at the same time.
    """
    #d = data.copy()
    ctry = list( Cross.keys() )
    
    # Correction of the cross-border (turn into net exchanges) over each time step
    for i in range(len(ctry)):
        for j in range(len(ctry)-1,i,-1):
            
            decide = (Cross[ctry[j]].loc[:,f"Mix_{ctry[i]}_{ctry[j]}"]
                      >= Cross[ctry[i]].loc[:,f"Mix_{ctry[j]}_{ctry[i]}"]) # direction
            diff = (Cross[ctry[j]].loc[:,f"Mix_{ctry[i]}_{ctry[j]}"]
                    - Cross[ctry[i]].loc[:,f"Mix_{ctry[j]}_{ctry[i]}"]) # exchange difference
            
            Cross[ctry[j]].loc[:,f"Mix_{ctry[i]}_{ctry[j]}"] = decide*diff # if flow i to j --> +value
            Cross[ctry[i]].loc[:,f"Mix_{ctry[j]}_{ctry[i]}"] = (decide-1)*diff # if j to i <-- -value

    return Cross


# +

#####################################
# ####################################
# Join Generation Exchanges
# ####################################
# ####################################

# -

def _join_generation_exchanges(Gen, Cross, is_verbose=False):
    """Function to join generation and cross-border flow information."""
    
    if is_verbose: print("Gather generation and importation...")
    ### Union of all tables of importation and generation together
    Union = {}
    for f in Gen.keys(): # for all countries
        Union[f] = pd.concat([Gen[f],Cross[f]],axis=1) # gathering of the data
    
    return pd.concat([Union[f] for f in Union.keys()],axis=1) # Join all the tables together


# +

#####################################
# ####################################
# Resample Data
# ####################################
# ####################################

# -

def resample_data(Data, freq, case):
    """
    Function that turns data from MW to MWh and adapts its frequency.
    The data is assumed to be in MW, in a table with 15min indexes.
    
    Parameter:
        Data: dict of DataFrames containing the generation data.
        freq: the frequency (length of time step)
    
    Return:
        dict of pandas DataFrame wiht resampled and converted energy
    """
    ### VERIFY THE FREQUENCY
    check_frequency(freq)
    if check_regularity_frequency(freq): # If frequency is regular for pandas
        ### Normal resampling and MW -> MWh conversion
        for f in Data: # For all keys
            conv_factor = get_steps_per_hour(freq, dtype=float) # Factor to convert MW to MWh
            # Resample Power and turn into energy
            Data[f] = (Data[f]
                       .resample(freq)
                       .mean()#apply(lambda x:x.mean()) # Mean works also to downscale
                       .interpolate()
                       .fillna(0)) / conv_factor
            
    else: # Frequency is month or year
        ### Use Hours to convert MW -> MWh, then resample to correct frequency
        for f in Data: # For all keys
            conv_factor = get_steps_per_hour('H') # Factor to convert MW to MWh
            # Resample Power and turn into energy
            Data[f] = (((Data[f]
                         .resample(freq)
                         .mean()#apply(lambda x:x.mean()) # Average as power still
                         .interpolate()
                         .fillna(0)
                        )
                        / conv_factor # Turn MW -> MWh
                       )
                       .resample(freq)
                       .sum() # Sum as energy now
                      )
            
    return Data