"""
Module, whose only objective is to update and copy the data necessary for the software to work correctly.
The source can be anywhere and is defaulted to the support_files (assuming the file is used from within
the repository and not after an install. If installed, the files must be specified each time). Updating
the information from SwissGrid uses source codes from https://swissgrid.ch. It is much more intensive and
requires a specific parametrization of the updater function.
"""
import os
import shutil
import pandas as pd
import numpy as np
from time import time
from concurrent.futures import ProcessPoolExecutor

from dynamical.preprocessing.auxiliary import get_default_file








def update_all(path_dir=None, path_swissGrid=None, is_verbose=False):
    """
    Updates all possible software files at once.
    
    Parameter
    ----------
        path_dir: str, optional
            path to the directory containing updated files. Typically, this is the `support_files/`
            directory of the cloned git repository of EcoDynElec. The directory must contain ALL
            the files of interest, otherwise the execution is aboarded.
            If None, an attempt to use a default path is made, with no promises.
        path_swissGrid: str, optional
            path to a directory containting files downloaded from https://swissgrid.ch. If not given,
            the swiss-grid information is not updated. This will have no impact if no path_dir is given.
            To solely update the swiss-grid data, please use the `update_sg` function.
        is_verbose: bool, optional
            to display information. Default to False.
    """
    ### Verify the path_dir
    if path_dir is None:
        ### Try to reach a default directory
        path_dir = os.path.join(os.dirname(os.dirname(os.path.abspath(__file__))), 'support_files')
    
    if os.path.isdir( default_path ): # Verify if path is valid
        path_dir = default_path
    else:
        raise FileNotFoundError(f"Need to specify a directory containing updated files to save them into software files.")
        
    ### Verify the names if using path_dir
    expected = ["Neighbourhood_EU.csv","Functional_Unit_Vector.csv","Pertes_OFEN.csv","Repartition_Residus.xlsx"]
    files = os.path.listdir(path_dir)
    if not all(exp in files):
        missing = [f for f in expected if f not in files]
        raise FileNotFoundError(f"The following files are missing. Please use individual update functions for individual updates. {missing}")
    
    
    ### Process all common updates
    if is_verbose: print(f"Update Neighbourhood file...")
    update_neighbours(os.path.join(path_dir,"Neighbourhood_EU.csv"))
    if is_verbose: print(f"Update FU vector file")
    update_FUVector(os.path.join(path_dir,"Functional_Unit_Vector.csv"))
    if is_verbose: print(f"Update Losses file")
    update_Losses(os.path.join(path_dir,"Pertes_OFEN.csv"))
    if is_verbose: print(f"Update Residual share file")
    update_residual_share(os.path.join(path_dir,"Repartition_Residus.xlsx"), save=True)
    
    
    ### Go on with SwissGrid
    if path_swissGrid is not None:
        if os.path.isdir(path_swissGrid):
            content = os.listdir(path_swissGrid)
            if len(content)>0:
                if all(os.path.splitext(f)[1].startswith(".xls") for f in content):
                    update_sg(path_dir=os.path.abspath(path_swissGrid), save=True, is_verbose=is_verbose)
                else:
                    raise KeyError(f"Not all files are source .xls or .xlsx in directory {path_swissGrid}")
            else:
                raise FileNotFoundError(f"{path_swissGrid} is an empty directory...")
        else:
            raise FileNotFoundError(f"{path_swissGrid} is no directory.")
    elif is_verbose: print("SwissGrid files were not updated.")
    
    return








###################################
####### GENERAL UPDATES ###########
###################################

def update_copy(path, name):
    ### Verify
    if not os.path.isfile(path): raise FileNotFoundError(f"Could not find {path}")
    
    ### Where to save
    savepath = get_default_file(name)
    
    ### Copy
    shutil.copy(path, savepath)

def update_neighbours(path):
    update_copy(path, "Neighbourhood_EU.csv")
    
def update_FUVector(path):
    update_copy(path, "Functional_Unit_Vector.csv")
    
def update_Losses(path):
    update_copy(path, "Pertes_OFEN.csv")

def update_residual_share(path, save=True):
    """Extracts the data relative to residual share estimate and save it in software files"""
    ### Verification
    # Error will be raised by pandas if needed
    
    ### Extraction
    interest = {'Centrales au fil de l’eau': "Hydro_Res",
                'Centrales therm. classiques et renouvelables':"Other_Res"}
    df = pd.read_excel(path, header=59, index_col=0).loc[interest.keys()].rename(index=interest)
    df = (df/df.sum(axis=0)).T
    
    ### Saving
    if save:
        savepath = get_default_file("Share_residual.csv")
        df.to_csv(savepath, index=True)
    
    return df





###################################
##### SPECIFIC TO SWISS-GRID ######
###################################

def update_sg(path_dir=None, path_files=None, save=True, is_verbose=False):
    """
    Function to update the SwissGrid values from source files.
    It requires the source files from swissgrid.ch to be downloaded manually.
    The files are downloaded in parallel to save time, as .xlsx are
    particularly long to load.
    
    The data is returned and automatically overwrites previous version in the
    software files if save=True.
    
    Parameters
    -----------
        path_dir: str, optional
            path do directory containing EXCLUSIVELY the files from swissgrid.ch
            Either path_dir or path_files must be specified.
        path_files: list-like, optional
            list of paths to the files downloaded from swissgrid.ch on local computer
            Either path_dir or path_files must be specified.
        save: bool, optional
            to decide whether to overwrite the software files with the new extracted data
            default is True.
        is_verbose: to display information
        
    Returns
    --------
        pandas.DataFrame
    """
    ### List the elements / files
    if (path_dir is None)&(path_files is None):
        raise FileNotFoundError("Needs to specify a directory or a list of files")
    
    elif path_dir is not None:
        files = [os.path.abspath( os.path.join(path_dir, f) )
                 for f in sorted(os.listdir(path_dir))]
    else:
        files = path_files
        
    ### Verification
    faulty = [f for f in files if not os.path.isfile(f)]
    if faulty: raise FileNotFoundError(f"Following files were not found: {faulty}")
    
    ### Extract data
    if is_verbose: print("Extracting SwissGrid files...")
    t0 = time()
    whole_sg = []
    with ProcessPoolExecutor() as pool:
        for table in pool.map( prepare_sg_year, files ):
            whole_sg.append(table)
    whole_sg = pd.concat(whole_sg, axis=0).sort_index()
    if is_verbose:
        print(f"\tLoaded {len(files)} tables: {time()-t0:.2f} sec")
        print(f"\tMemory usage: {whole_sg.memory_usage().sum()/1024**2:.1f} MB")
    
    
    ### Save the data
    if save:
        target = get_default_file("SwissGridTotal.csv")
        if is_verbose: print(f"Re-writing {target}...")
        ## Build the path to file
        whole_sg.to_csv(target, index=True)
    
    ### Return
    if is_verbose: print(f"Updating SG total: {time()-t0:.2f} sec")
    return whole_sg



def _rename_columns_sg(columns):
    new_cols = {}
    for c in columns:
        if 'energy consumed by end users' in c: new_cols[c] = "Consommation_CH"
        elif 'energy production' in c: new_cols[c] = 'Production_CH'
        elif 'energy consumption' in c: new_cols[c] = 'Consommation_Brut_CH'
        elif "->" in c: new_cols[c] = c.strip()[-6:]
    return new_cols

def _set_index_sg(idx):
    start = pd.to_datetime(idx[0])
    new_idx = pd.date_range(start=start, freq='15T', periods=len(idx))
    return new_idx - pd.Timedelta('15min')

def _prepare_sg_year(path, year=None):
    if os.path.isfile(path):
        sg_file = path
    else:
        if year is None: raise ValueError("If path does not point at a file, a year value is needed")
        elif any(isinstance(year, k) for k in (int,float,np.number)):
            year = str(int(year))
        elif not isinstance(year, str): raise TypeError(f"year must be a string or a number. Not {year}")
        
        sg_file = os.path.join(path, [f for f in os.listdir(path) if year in f][0])
        
    ### Import data
    col_selection = 'A:D,K:R'
    data = pd.read_excel(sg_file, sheet_name='Zeitreihen0h15', header=0, index_col=0,
                         parse_dates=False, usecols=col_selection).drop(index='Zeitstempel',errors='ignore')
    
    ### Clean data
    data.index = set_index(data.index)
    return data.rename(columns=rename_columns(data.columns)).astype("int32")