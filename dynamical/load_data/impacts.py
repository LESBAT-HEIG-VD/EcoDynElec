import numpy as np
import pandas as pd
import os
from time import time
from dynamical.load_data.auxiliary import get_default_file


# +
# This module of function extracts the impact information from the files

# +

#################################
# ################################
# EXTRACT FUNCTIONAL UNIT VECTOR
# ################################
# ################################

# -

def extract_FU(path_fu, ctry:list=None, target:str='CH', residual:bool=False, cst_imports:bool=False):
    """Function to extract and modify the FU vector"""
    ### Get default file if None
    if path_fu is None:
        path_fu = get_default_file(name='Functional_Unit_Vector.csv')
    
    ### Import the FU
    fu = pd.read_csv(path_fu, index_col=[0])
    
    ### Selection of countries
    fu = select_fu_indexes(fu, ctry=ctry, residual=residual)
    
    ### Create constant import impacts
    if cst_imports:
        fu = set_constant_imports(fu, target=target)
    
    return fu

# +

#################################
# ################################
# SET CONSTANT IMPORTS FROM FU
# ################################
# ################################

# -

def set_constant_imports(fu, target:str='CH'):
    """Set the impacts of non-target countries to average Entsoe"""
    
    ### Selection of unique countries
    countries = np.unique( [i.split("_")[-1] for i in fu.index] )
    
    # The indexes to systematically exclude
    exclude = ['Mix_Other'] + [i for i in fu.index if str(i).endswith(f'_{target}')]
    # The value to turn all but target into
    how = fu.loc['Mix_Other',:]
    
    ### Change the information
    new_fu = fu.copy()
    new_fu.loc[~new_fu.index.isin(exclude),:] = how.values
    return new_fu

# +

#################################
# ################################
# SET CONSTANT IMPORTS FROM FU
# ################################
# ################################

# -

def select_fu_indexes(fu, ctry:list=None, residual:bool=False):
    """Selects relevant rows from complete FU vector"""
    if ctry is not None:
        # Consider the "Mix Other"
        places = list(ctry) + ['Other']

        # Copy the indexes
        idx = pd.Series(fu.index)

        # Production units per country
        selection = np.logical_or.reduce( [idx.apply(lambda x:str(x).endswith(f'_{p}')).values
                                            for p in places] )
    
    else: # Select for all countries
        selection = np.full((fu.shape[0],), True) # Vector of TRUE
    
    # Deal with residual
    if not residual:
        selection = np.logical_and(selection,
                                   ~(idx.apply(lambda x:str(x).startswith('Residual'))).values)
    
    return fu.loc[selection,:]

# +

#################################
# ################################
# EXTRACT MAPPING
# ################################
# ################################

# -

def extract_mapping(ctry, mapping_path=None, cst_import=False, residual=False, target='CH', is_verbose=False):
    """
    Function to build the impact matrix from mapping stored in files.
    Parameter:
        ctry: list of countries to load the impacts of (list)
        mapping_path: excel file where to find the mapping data (str, default: None)
        cst_import: whether to consider all impacts of non-traget countres 
                    as the impact of 'Other' (bool, default: False)
        residual: whether to consider production residual for the target country (bool, default: False)
        target: the target country (str, default: CH)
        is_verbose: to display information (bool, default: False)
    """
    ### Check the country list
    if is_verbose: print("Extraction of impact vector...")
    # Test the type of country
    if type(ctry)==str:
        ctry = [ctry]
    elif '__iter__' not in dir(ctry):
        raise TypeError("Parameter ctry should be a list, tuple or str")
    
    ### Verify mapping file OR FU file
    if mapping_path is None:
        mapping_path = get_default_file(name='Mapping_default.xlsx')
    
    ### Extract the impact information
    impacts = {}
    
    if is_verbose: print("\t. Mix_Other ",end="") # Mix from other countries
    impacts['Other'] = other_from_excel(mapping=mapping_path)
    
    for c in ctry:
        if is_verbose: print(f"/ {c} ",end="")
        if np.logical_and( cst_import, (c!=target) ): # Constant imports for other countries
            impacts[c] = set_constant_impacts( country_from_excel(mapping=mapping_path, place=c),
                                              constant=impacts['Other'].loc['Mix_Other'] )
        else:
            impacts[c] = country_from_excel(mapping=mapping_path, place=c)
            
    ### Add impact of residual
    if residual: # Mix from the residual part -> direct after "Mix_Other" (residual only in CH)
        if is_verbose: print("+ Residual ",end="")
        if 'CH' not in impacts:
            raise ValueError("Including residual only available for CH. Please include CH in the list of countries")
        impacts['CH'] = pd.concat([impacts['CH'],
                                   residual_from_excel(mapping=mapping_path, place='CH')])
        
    ### Gather impacts in one table
    if is_verbose: print(".")
    impact_matrix = pd.concat([impacts[c] for c in impacts.keys()])
    
    
    return impact_matrix


# +

#################################
# ################################
# Other from excel
# ################################
# ################################

# -

def other_from_excel(mapping):
    """Load the mapping for 'Other' from an excel file (mapping)."""
    ### Impact for production mix of 'other countries'
    d = pd.read_excel(mapping,sheet_name="ENTSOE_avg",
                      header=1, usecols=np.arange(2,7),
                      index_col=[0]) # extract
    return d.loc[['ENTSOE'],:].rename(index={'ENTSOE':'Mix_Other'}) # format


# +

#################################
# ################################
# Country form excel
# ################################
# ################################

# -

def country_from_excel(mapping, place):
    """Load the mapping of a given country (place) from an excel file (mapping)."""
    try: # test if the country is available in the mapping file
        d = pd.read_excel(mapping,sheet_name=place, index_col=[0]) # Read and get index col
        columns = d.loc[:,'Environmental impacts of ENTSO-E sources':].iloc[0]
        columns = columns[ columns.apply(lambda x: not str(x).endswith('KBOB')) ] # Strike out KBOB... Do your own mapping man!

        # Get only important data
        d = d.loc[:,columns.index].dropna(axis=0).rename(columns=columns.to_dict())
        d = d.loc[d.index.notnull()].drop(index=['Energy sources ENTSO-E'], errors='ignore') # Select the correct indexes

        # Replace "-" with zeros.
        d = d.replace("-",0).astype('float32')

        # Change indexes
        return d.rename({i: (i.replace('(','').replace(')','').replace(" Fos",' fos')
                             + f" {place}").replace(' ','_').replace('__','_')
                         for i in d.index}, axis=0).rename_axis("")
    except Exception as e:
        raise ValueError(f"Mapping for {place} not available: {e} ")


# +

#################################
# ################################
# Residual from excel
# ################################
# ################################

# -

def residual_from_excel(mapping, place):
    """
    Load impact data of the production residual and add it to the impact matrix.
    Parameter:
        mapping: path to file with the mapping (str)
        place: country tag of the country (str)
    Return:
        pandas DataFrame with the impact_ch, where the impact of residual production is added.
    """
    try: # test if the "country" is available in the mapping file
        d = pd.read_excel(mapping,sheet_name="Residue",index_col=0)
        columns = d.loc[:,'Environmental impacts of ENTSO-E sources':].iloc[0]

        # Select the righ column
        d = d.loc[:,columns.index].rename(columns=columns.to_dict()).rename_axis('')

        # Select the right indexes
        idx = pd.Series(d.index).apply(lambda x:str(x).startswith('Resid')).values
        d = d.loc[idx].astype('float32')

        # Rename indexes with the place & formatting
        return d.rename(index={i: (i.replace('Residue','Residual').replace(" ","_")
                                   +f"_{place}")
                               for i in d.index})
        
    except Exception as e:
        raise ValueError(f" Residual not available: {e}")


# +

#################################
# ################################
# Set constant impacts
# ################################
# ################################

# -

def set_constant_impacts(impacts, constant):
    """Set the impacts to a constant value"""
    return impacts.apply(lambda x: constant,axis=1)