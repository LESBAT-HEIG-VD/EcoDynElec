import numpy as np
import pandas as pd
import os
from time import time

#################### Local functions
from dynamical.checking import check_frequency
from dynamical.residual import include_global_residual
from dynamical.load_data.raw_entsoe import extract


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
                clean_generation=True, n_hours=2, days_around=7, is_verbose=True):
    
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
    Gen = import_generation(path_gen=path_gen, path_raw=path_gen_raw, ctry=ctry,
                            start=start, end=end, savedir=savedir,
                            is_verbose=is_verbose) # import generation data
    Gen = adjust_generation(Gen, freq=freq, residual_global=residual_global, sg_data=sg_data,
                            clean_generation=clean_generation, n_hours=n_hours, days_around=days_around, prod_gap=prod_gap,
                            is_verbose=is_verbose) # adjust the generation data
    
    ### EXCHANGE DATA
    Cross = import_exchanges(neighbourhood=involved_countries, ctry=ctry,
                             start=start, end=end, savedir=savedir,
                             path_imp=path_imp, path_raw=path_imp_raw, freq=freq, is_verbose=is_verbose) # Imprt data
    
    Cross = adjust_exchanges(Cross=Cross, net_exchange=net_exchange, freq=freq,
                             sg_data=sg_data if correct_imp else None)
    # Correct the cross-border flows at Swiss border.
    # if correct_imp:
    #     if is_verbose: print("Adapt Exchage Data of Swizerland...")
    #     Cross = adjust_exchanges(Cross=Cross,sg_data=sg_data,freq=freq) # Adjust the exchange data
    
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

def import_generation(ctry, start, end, path_gen=None, path_raw=None,
                      savedir=None, is_verbose=False):
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
        Gen = extract(ctry=ctry, dir_gen=path, savedir_gen=savegen,
                      save_resolution=savedir, is_verbose=is_verbose) # if from raw files

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

def adjust_generation(Gen, freq='H', residual_global=False, sg_data=None, clean_generation=True, n_hours=2, days_around=7,
                      prod_gap=None, is_verbose=False):
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
    ### Identify missing values
    Empty_Gen, Empty_Nuc = gather_missing_generation(Gen=Gen,
                                                      add_on=residual_global,
                                                      is_verbose=is_verbose)
    ### Classify missing values as occasional or missing period
    Empty_Unique, Empty_Period = sort_missing_generation(Empty_Gen=Empty_Gen,
                                                          Empty_Nuc=Empty_Nuc,
                                                          n_hours=n_hours,
                                                          add_on=residual_global,
                                                          is_verbose=is_verbose)
    
    if clean_generation:
        ### Fill missing values consequently
        Gen = fill_missing_generation(Gen,
                                       Empty_Unique=Empty_Unique,
                                       Empty_Period=Empty_Period,
                                       n_hours=n_hours,
                                       days_around=days_around,
                                       add_on=residual_global,
                                       is_verbose=is_verbose)
    elif is_verbose: # If no data cleaning but verbose: count the missings
        missing_report = pd.DataFrame({f: {'count':len(Empty_Gen[f]), 'percent': round(100*len(Empty_Gen[f])/Gen[f].shape[0],1)}
                         for f in Gen})
        if missing_report.values.sum()>0:
            print(f"\nNumber of generation hours suspected as missing:")
            print(pd.DataFrame(missing_report),end="\n\n")
        
    
    ### Resample data to the right frequence
    Gen = resample_generation(Gen=Gen, freq=freq, add_on=residual_global, is_verbose=is_verbose)
    
    ### Includes residual production
    if residual_global:
        Gen = include_global_residual(Gen=Gen, freq=freq, sg_data=sg_data, prod_gap=prod_gap,
                                       is_verbose=is_verbose)
    
    return Gen


# +

#####################################
# ####################################
# Gather missing generation
# ####################################
# ####################################

# -

def gather_missing_generation(Gen, add_on=False, is_verbose=False):
    """
    Function to find missing information in the Entso-e data.
    It distinguishes missing values and missing nuclear generation.
    Parameter:
        Gen: dict of pandas DataFrame with production data for each country.
        add_on: display flourish (bool, default: False)
        is_verbose: to display information (bool, default: False)
    Return:
        2 dict of lists, one with dates of missing generations and one with dates of missing nuclear
    """
    #######################
    ### Correction of Generation data
    #######################
    if is_verbose: print(f"Correction of generation data:\n\t1/{4+int(add_on)} - Gather missing values...")
    ### Data with no nuclear production (good repair for missng datas)
    ## Exceptions to nuclear missing datas
    NoNuc = ["CH"] # There is no problem with swiss -> missing values are OK !
    for f in Gen.keys(): # for all countries
        if Gen[f]["Nuclear_{}".format(f)].sum()==0: # if the sum of all nuclear production is null
            NoNuc.append(f) # register the country as non nuclear producer
    
    
    ### Dates with partial or total missing production
    Empty_Gen = {} # total missing production
    Empty_Nuc = {} # partial missing production
    empty_nuc = [] # to store some missing data
    for f in Gen.keys(): # for all considered countries
        # Missing production
        Empty_Gen[f] = list(Gen[f][Gen[f].sum(axis=1)==0].index) # list of dates of missing production
        
        # Missing nuclear
        if f in NoNuc: # if country without nuclear
            Empty_Nuc[f]=[] # nothing to look for
        else:
            Empty_Nuc[f] = []
            empty_nuc = list(Gen[f][Gen[f]["Nuclear_{}".format(f)]==0].index) # dates of missing nuclear
            for k in empty_nuc:
                if k not in Empty_Gen[f]: # if not already in missing generation data...
                    Empty_Nuc[f].append(k) # ... then append it into list of "only" missing nuclear
    
    return Empty_Gen, Empty_Nuc


# +

#####################################
# ####################################
# Sort missing generation
# ####################################
# ####################################

# -

def sort_missing_generation(Empty_Gen, Empty_Nuc, n_hours=2, add_on=False, is_verbose=False):
    """
    Function that classifies the missing values to prepare for value filling.
    Parameter:
        Empty_Gen: dict of missing data for all units at one time step.
        Empty_Nuc: dict of missing values in nuclear production (for countries with nuclear production)
        n_hour: Max number of successive missing hours to be considered as occasional event
                (int, default: 2)
        add_on: display flourish (bool, default: False)
        is_verbose: to display information (bool, default: False)
    Return:
        2 dict of lists of missing moments and one for missing periods.
    """
    if is_verbose: print(f"\t2/{4+int(add_on)} - Sort missing values...")
    ### Distinction between periods of missing data and occasional ones.
    Empty_Period = {}
    Empty_Unique = {}
    
    for f in Empty_Gen.keys():
        Empty_Period[f] = []
        Empty_Unique[f] = []
        Empty = sorted(Empty_Gen[f] + Empty_Nuc[f]) # sort all missing datas together (nuclear and not nuclear)
        if len(Empty)==0:
            pass # if nothing is missing -> nothing is done
        elif len(Empty)<=n_hours: # if only few missing dates...
            for t in Empty_Gen[f]:
                Empty_Unique[f].append(t) # ...everything registered as occasional missing datas.
        else:
            t,h = 1,0
            while t<len(Empty): # look through all datas
                if Empty[t]==Empty[h]+pd.Timedelta("{} hour".format(t-h)): # if 2 datas from the same "period"
                    t+=1 # go for looking if the next date belongs to the period too
                else: # if different "periods"...
                    if t-h>n_hours: # if the period is longer than the limit
                        Empty_Period[f].append((Empty[h],t-h)) # Register (start,duration) as a period 
                    else: # if period is 1 or 2 hours long
                        for i in range(t-h):
                            Empty_Unique[f].append(Empty[h+i]) # add all investigated datas of this period as occasional missing data
                    h += t-h # beginning of another "period" investigationo
                    t+=1 # hour 0 of the group already seen --> go to possible hour 2.
            
            if t-h>n_hours: # for the last "period", if it is long enough
                Empty_Period[f].append((Empty[h],t-h)) # Stock (start,duration) as a period
            else: # if period is 1 or 2 hours long
                for i in range(t-h):
                    Empty_Unique[f].append(Empty[h+i]) # add all investigated datas of this period as occasional missing data
    
    return Empty_Unique, Empty_Period


# +

#####################################
# ####################################
# Fill missing generation
# ####################################
# ####################################

# -

def fill_missing_generation(table, Empty_Unique, Empty_Period, n_hours=2, days_around=7,add_on=False,
                            is_verbose=False):
    """
    Function to fill the missing values in generation data.
    Parameter:
        table: pandas DataFrame with the generation data.
        Empty_Unique: dict of missing values considered as occasional
        Empty_Period: dict of missing values considered as a whole period
        n_period: Max number of successive missing hours to be considered as occasional event
                (int, default: 2)
        days_around: number of days after and before a gap to consider to create a 'typical mean day'
                (int, default: 7)
        add_on: display flourish (bool, default: False)
        is_verbose: to display information (bool, default: False)
    """
    if is_verbose: print(f"\t3/{4+int(add_on)} - Fill missing values...")
        
    ### Filling all missing values
    for f in table.keys(): # for all countries
        
        ### First: fill occasional data
        table[f] = fill_occasional(table=table[f], empty=Empty_Unique[f], n_hours=n_hours)
        
        ### Second: fill periods
        table[f] = fill_periods(table=table[f], empty=Empty_Period[f], days_around=days_around)
    return table


# +

#####################################
# ####################################
# Fill occasional
# ####################################
# ####################################

# -

def fill_occasional(table, empty, n_hours=2):
    """
    Function to fill occasional missing data. Only used for missing of 2 missing hours in a row or less.
    Parameter:
        table: pandas DataFrame with the generation data
        empty: the list of empty slots considered as occasional
        n_hours: Max number of successive missing hours to be considered as occasional event
                    (int, default: 2)
    """
    filled_table = table.copy()
    miss = empty.copy() # copy of list of missing dates
    
    for n,t in enumerate(empty): # for all missing dates
        col = table.loc[t][table.loc[t]==0].index # list of power station to fill (not always all)
        
        try:
            if t+pd.Timedelta("1 hour") in miss: # If 2 hours in a row
                # Replace first missing value with: 1/3 of difference between value(2h after) and value(1h before)
                filled_table.loc[t,col] = round((1/3)*filled_table.loc[t+pd.Timedelta("2 hour"),col]\
                        + (2/3)*filled_table.loc[t-pd.Timedelta("1 hour"),col]  , 2) # rounded at 0.01

            else: # if single missing hour (or second of a pair) -> linear extrapolation
                filled_table.loc[t,col] = (1/2)*(filled_table.loc[t+pd.Timedelta("1 hour"),col] \
                        + filled_table.loc[t-pd.Timedelta("1 hour"),col])
        except KeyError as e:
            #raise ValueError(f"Missing data identified in the first or last time step. Impossible to fix: {e}")
            try:
                filled_table.loc[t,col] = filled_table.loc[t-pd.Timedelta("1 hour"),col] # Fill with previous if at the end
            except KeyError as e:
                next_full = (t+pd.Timedelta("2H") if t+pd.Timedelta("1H") in empty else t+pd.Timedelta("1H"))
                filled_table.loc[t,col] = filled_table.loc[next_full,col] # Fill with next if at the start

        miss.remove(t) # treated hour removed from copied list (to avoid errors)
    return filled_table


# +

#####################################
# ####################################
# Fill periods
# ####################################
# ####################################

# -

def fill_periods(table, empty, days_around=7):
    """
    Function to fill the missing periods with typical day values
    Parameter:
        table: pandas DataFrame with the generation data
        empty: the list of empty slots considered as periods
        days_around: number of days after and before a gap to consider to create a 'typical mean day'
                     (int, default: 7)
    """
    filled_table = table.copy()
    miss = empty.copy() # copy of the missing periods of the country (not to alter it)
    
    for t in miss: # for all missing periods
        # List of columns to fill (if column is null for the whole duration)
        delta = pd.Timedelta("{} minutes".format(15*(t[1]-1))) # entierty of the gap, in minutes
        col = filled_table.columns[(filled_table.loc[t[0]:t[0]+delta].sum()==0).values]

        # Missing data marked as "NaN". Data then not taken into account in the "typical mean day"
        filled_table.loc[t[0]:t[0]+delta,col]=np.nan

        # Creates the "typical mean day" (Average of the considered period)
        early = t[0]-pd.Timedelta("{} days".format(days_around))
        late = t[0]+pd.Timedelta("{} days + {} minutes".format(days_around, 15*(t[1]-1)))
        period = filled_table.loc[early:late,col].copy() # surrounding table (if available)

        typ_day = period.groupby(by=lambda x:(x.hour,x.minute)).mean() # "typical mean day"
        typ_day.index = pd.date_range(start="2018", periods=typ_day.shape[0], freq="15min")
        
        for dt in typ_day.index:
            loc_large = ((filled_table.index.minute==dt.minute)&(filled_table.index.hour==dt.hour))
            localize = filled_table[loc_large].loc[t[0]:t[0]+delta].index
            filled_table.loc[localize,col] = typ_day.loc[dt, col]
            
            
    return filled_table


# +

#####################################
# ####################################
# Resample generation
# ####################################
# ####################################

# -

def resample_generation(Gen, freq, add_on=False, is_verbose=False):
    """
    Function that resamples the generation data. It can only downsample (lower the resolution) by summing.
    
    Parameter:
        Gen: dict of DataFrames containing the generation data.
        freq: the time step (resolution)
        add_on: a display flourish (bool, default: False)
        is_verbose: to display information (bool, default: False)
    
    Return:
        dict of pandas DataFrame wiht resampled productions
    """
    #######################
    ###### Resample Gen.
    #######################
    if ((check_frequency(freq))&(freq!='15min')):
        if is_verbose: print(f"\t4/{4+int(add_on)} - Resample Generation data to {freq} steps...")
        for f in Gen.keys(): # For all countries
            Gen[f] = Gen[f].resample(freq).sum() # Sum as we talk about energy.
            
    return Gen


# +

#####################################
# ####################################
# Import Exchanges
# ####################################
# ####################################

# -

def import_exchanges(neighbourhood, ctry, start, end, path_imp=None, path_raw=None,
                     savedir=None, freq='H', is_verbose=False):
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
        Cross = extract(ctry=ctry, dir_imp=path, savedir_imp=saveimp,
                      save_resolution=savedir, is_verbose=is_verbose) # if from raw files

    
    for i,c in enumerate(ctry):# File extraction
        if path==path_imp:
            if is_verbose: print("\t{}/{} - {}...".format(i+1,len(files),c))
            Cross[c] = pd.read_csv(path_imp+files[c],index_col=0) # Extraction

        # Transform index in time data and convert it from UTC to CET, then keeps only period of interest
        Cross[c].index = pd.to_datetime(Cross[c].index,yearfirst=True) # Considered period only
        Cross[c] = Cross[c].loc[start:end] # select right period
        
        # Format the import data by selecting and gathering columns
        Cross[c] = Cross[c].loc[:,neighbourhood] # Keep only usefull countries
        other = [c for c in neighbourhood if c not in ctry] # Label as 'other' all non-main selected countries
        Cross[c]["Other"] = Cross[c][other].sum(axis=1) # Sum of "other countries"
        Cross[c].drop(columns=[k for k in neighbourhood if k not in ctry],inplace=True) # Delete details of "other countries"
        Cross[c].columns = [f"Mix_{s}_{c}" for s in Cross[c].columns] # Rename columns
    
    
    ### Resampling the temporal data
    if ((is_verbose)&(freq!='15min')): print(f"Resample Exchanged energy to frequence {freq}...")
    if ((check_frequency(freq))&(freq!='15min')):
        for c in Cross.keys(): # For all countries
            Cross[c] = Cross[c].resample(freq).sum() # Sum as we talk about energy.
            
    return Cross


# +

#####################################
# ####################################
# Adjust exchanges
# ####################################
# ####################################

# -

def adjust_exchanges(Cross, net_exchange=False, sg_data=None, freq='H'):
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
    ### ADJUST WITH SWISSGRID DATA (AT SWISS BORDER ONLY)
    if sg_data is not None: # Adjust with SG data
        Cross = set_swissGrid(Cross, sg_data)
        
    ### FILL THE DATA
    
    
    ### ADJUST THE FREQUENCY
    
    
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
            
            # decide = (d[f"Mix_{ctry[i]}_{ctry[j]}"] >= d[f"Mix_{ctry[j]}_{ctry[i]}"]) # direction
            # diff = d[f"Mix_{ctry[i]}_{ctry[j]}"] - d[f"Mix_{ctry[j]}_{ctry[i]}"] # exchange difference
            # d.loc[:,f"Mix_{ctry[i]}_{ctry[j]}"] = decide*diff # if flow from i to j --> + value
            # d.loc[:,f"Mix_{ctry[j]}_{ctry[i]}"] = (decide-1)*diff # if from j to i <-- -value

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
