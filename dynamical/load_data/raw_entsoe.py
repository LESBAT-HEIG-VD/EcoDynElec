import pandas as pd
import numpy as np
from time import time
import os

# +

#################
#################
# ## Extract
##############

# -


def extract(ctry=None, dir_gen=None, dir_imp=None, savedir_gen=None, savedir_imp=None,
            save_resolution=None, is_verbose=False):
    """Easy command to execute all at once"""
    t0 = time()
    if os.path.isdir(r"{}".format(dir_gen)):
        if is_verbose: print("\tGeneration data.")
        Gen = create_per_country(path_dir=dir_gen, case='generation', ctry=ctry, savedir=savedir_gen,
                           savedir_resolution=save_resolution,is_verbose=is_verbose)
            
    if os.path.isdir(r"{}".format(dir_imp)):
        if is_verbose: print("\tCross-border flow data.")
        Imp = create_per_country(path_dir=dir_imp, case='import', ctry=ctry, savedir=savedir_imp,
                           savedir_resolution=save_resolution, is_verbose=is_verbose)
    
    if is_verbose: print("\tExtraction time: {:.2f} sec.".format(time()-t0))
    
    if ((dir_gen is not None)&(dir_imp is None)): return Gen
    elif ((dir_gen is None)&(dir_imp is not None)): return Imp
    else: return Gen, Imp


# +

#################
#################
# ## Create per country
##############

# -


def create_per_country(path_dir, case, ctry=None, savedir=None, savedir_resolution=None, is_verbose=False):
    # Obtain parameter set for the specific case
    destination,origin,data,area = get_parameters(case)
    
    # Import content of raw files
    df = load_files(path_dir, destination,origin,data,area,is_verbose=is_verbose)
    
    # Get auxilary information
    resolution = get_best_resolution(df, destination, case, savedir=savedir_resolution,
                                     is_verbose=is_verbose) # Resolutions
    prod_units = get_origin_unit(df,origin) # list of prod units or origin countries
    time_line = get_time_line(unique_dates=df.DateTime.unique()) # time line of the data
    
    # Format and save files for every country
    Data = {} # Data storage object
    t0 = time()
    for i,c in enumerate(resolution.index): # for all countries
        if ctry is not None:
            if c not in ctry: continue; # skip if c not in ctry list.
        if is_verbose: print(f"Extracting {case} for {c} ({i+1}/{resolution.shape[0]})...", end="\r")
        # Get data from the country and sort by date
        country_data = df[df.loc[:,destination]==c].drop_duplicates().sort_values(by="DateTime")

        # Select only the Generation data, then resample in 15min and interpolate (regardless of ResolutionCode)
        country_prod = country_data.pivot(index='DateTime',columns=origin, values=data)
        country_prod = country_prod.fillna(0).resample('15min').asfreq(None).interpolate()
        del country_data # free memory space

        # Add all columns
        country_detailed = pd.DataFrame(None,columns=prod_units,index=time_line,
                                        dtype='float32').resample('15min').asfreq(None) # init. with None
        country_detailed.loc[:,country_prod.columns] = country_prod # fill with data
        del country_prod # free memory space
        country_detailed = country_detailed.interpolate().fillna(0) # NAN: interpolate (& ffill), then 0 for remaining

        # Transform MW every 15min --> MWh every 15 min
        country_detailed /= 4

        # Save files
        if savedir is not None:
            country_detailed.to_csv(f"{savedir}{c}_{case}_MWh.csv")
        Data[c] = country_detailed # Store information
        del country_detailed # free memory space
    if is_verbose: print(f"Extract raw {case}: {round(time()-t0,2)} sec.             ")
    return Data


# +

#################
#################
# ## Load files
##############

# -


def load_files(path_dir, destination=None,origin=None,data=None,area=None,case=None,is_verbose=False):
    if None in [destination,origin,data,area]:
        if case is None:
            raise KeyError("Missing information to load files: what 'case' is it ?")
        else:
            destination,origin,data,area = get_parameters(case)
    
    # Types to reduce size of data table
    column_types = {'Year':'int8', 'Month':'int8', 'Day':'int8', 'FlowValue':'float32',
                    'ActualGenerationOutput': 'float32', 'ActualConsumption': 'float32'}
    useful = ['DateTime',destination,'ResolutionCode',origin,data] # columns to keep

    files = [path_dir + f for f in os.listdir(path_dir)] # gather file pathways

    t0 = time()
    container = []
    for i,f in enumerate(files): # For all files
        if is_verbose: print(f"Extract file {i+1}/{len(files)}...", end="\r")
        # Extract the information
        d = pd.read_csv(f,sep="\t", encoding='utf-8', parse_dates=['DateTime'], dtype=column_types)

        # Only select country level & Useful columns
        d = d.loc[d.loc[:,area]=="CTY", useful]
        container.append(d)
        del d # free memory space

    # Concatenates all files
    if is_verbose: print("Concatenate all files...",end="\r")
    df = pd.concat(container)
    del container # free memory space

    if is_verbose: print(f"Data loading: {round(time()-t0,2)} sec")
    if is_verbose: print(f"Memory usage table: {round(df.memory_usage().sum()/(1024**2),2)} MB")
    return df


# +

#################
#################
# ## Get best resolution
##############

# -


def get_best_resolution(df, destination, case, savedir=None, is_verbose=False):
    """Get the resolution map for all countries"""
    t0 = time()
    get_resolution = lambda x: x[2:4]+"min" # mini-function to extract resolution in minutes
    resolution = pd.Series({c: df[df.loc[:,destination]==c].loc[:,'ResolutionCode'].apply(get_resolution).unique().min()
                             for c in df.loc[:,destination].unique()},name="Resolution").sort_index() # gather all at once
    if os.path.isdir(r"{}".format(savedir)):
        resolution.to_csv(f"{savedir}Original_resolution_{case}.csv") # save file
    if is_verbose: print(f"Get original resolutions: {round(time()-t0,2)} sec.")
    return resolution


# +

####################
####################
# ## Get origin unit
##############

# -


def get_origin_unit(df,origin):
    """Gets ordered list of sources (origin countries or production units)"""
    return np.sort(df.loc[:,origin].unique())


# +

#################
#################
# ## Get time line
##############

# -


def get_time_line(unique_dates):
    """Gets the time line and corrects it if needed"""
    # Get the time line
    time_line = pd.DatetimeIndex(np.sort(unique_dates))

    # Add last hour in 15min, if not already here
    if ((time_line[-1].hour==23) & (time_line[-1].minute==0)):
        time_line = pd.DatetimeIndex(time_line.to_list() + [time_line[-1]+pd.Timedelta("45T")])

    return time_line


# +

#################
#################
# ## Get parameters
##############

# -

def get_parameters(case):
    """Function used to define parameters for later code"""
    if case=='import':
        destination = 'InMapCode'
        origin = 'OutMapCode'
        data = 'FlowValue'
        area = 'OutAreaTypeCode'

    elif case=='generation':
        destination = 'MapCode'
        origin = 'ProductionType'
        data = 'ActualGenerationOutput'
        area = 'AreaTypeCode'

    else:
        raise KeyError(f"case {case} not understood.")
    
    return destination, origin, data, area
