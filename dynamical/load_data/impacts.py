import numpy as np
import pandas as pd
import os
from time import time
from ecodyn.load_data.auxiliary import get_default_file


# +
# This module of function extracts the impact information from the excels

# +

#################################
# ################################
# EXTRACT IMPACTS
# ################################
# ################################

# -

def extract_impacts(ctry, mapping_path, cst_import=False, residual=False, target='CH', is_verbose=False):
    """
    Function to build the impact matrix from mapping stored in files.
    Parameter:
        ctry: list of countries to load the impacts of (list)
        mapping_path: excel file where to find the mapping data (str)
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
    
    ### Lists for some formating
    old = ["AT","CH","DE","IT","FR","CZ"] # countries writen differently in the mapping file
    # Wished soure impacts (same order than production data)
    expected = pd.Index(["Other_fossil","Fossil_Gas","Fossil_Peat","Biomass",
                            "Hydro_Run-of-river_and_poundage","Solar","Waste","Wind_Onshore",
                            "Other_renewable","Fossil_Oil_shale","Hydro_Water_Reservoir",
                            "Fossil_Brown_coal/Lignite","Nuclear","Fossil_Oil","Hydro_Pumped_Storage",
                            "Wind_Offshore","Fossil_Hard_coal","Geothermal",
                            "Fossil_Coal-derived_gas","Marine"])
    ### Verify mapping file
    if mapping_path is None:
        mapping_path = get_default_file(name='Mapping_default.xlsx')
    
    ### Extract the impact information
    impacts = {}
    
    if is_verbose: print("\t. Mix_Other ",end="") # Mix from other countries
    impacts['Other'] = other_from_excel(mapping=mapping_path)
    
    for c in ctry:
        if is_verbose: print(f"/ {c} ",end="")
        imp = country_from_excel(mapping=mapping_path, place=c, is_old=(c in old))
        if imp is not None:
            impacts[c] = shape_country(imp, place=c, is_old=(c in old), imp_other=impacts['Other'],
                                       cst_import=((cst_import)&(c!=target)), expected=expected)
            
    ### Add impact of residual
    if residual: # Mix from the residual part -> direct after "Mix_Other" (residual only in CH)
        if is_verbose: print("+ Residual ",end="")
        impacts['CH'] = residual_from_excel(impact_ch=impacts['CH'],mapping=mapping_path)
        
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
    indicators = ["GWP","CED_renewable","CED_non-renewable","ES2013"]
    d = pd.read_excel(mapping,sheet_name="ENTSOE_avg",
                         header=1, usecols=np.arange(2,7), index_col=[0]) # extract
    return pd.DataFrame(d.loc['ENTSOE',:].values,index=indicators, columns=["Mix_Other"]).T # format


# +

#################################
# ################################
# Country form excel
# ################################
# ################################

# -

def country_from_excel(mapping, place, is_old=True):
    """Load the mapping of a given country (place) from an excel file (mapping)."""
    try: # test if the country is available in the mapping file
        if is_old: 
            d = pd.read_excel(mapping,sheet_name=place, index_col=[0,1,2]) # import
        else:
            d = pd.read_excel(mapping,sheet_name=place) # import
    except Exception as e:
        raise ValueError(f"Mapping for {place} not available: {e} ")
    
    return d


# +

#################################
# ################################
# Shape country
# ################################
# ################################

# -

def shape_country(d, place, expected, is_old=True, imp_other=None, cst_import=False):
    """
    Bring some changes in the index and column namings and order for the impact matrix.
    Parameter:
        d: the impact matrix for one given country (pandas DataFrame)
        place: the country (str)
        expected: list of expected labels for the production means
        is_old: if the country belongs to the ones with an old formating (bool, default True)
        imp_other: the impact matrix for 'Other' countries (pandas DataFrame, default None)
        cst_import: whether to consider all impacts as the impact of 'Other' (bool, default: False)
    """
    col_id = len(d.loc[:,:"Environmental impacts of ENTSO-E sources"].columns)-1 # columns to consider

    # Select corresponding data & rename columns
    imp_ctry = pd.DataFrame(d.iloc[:,col_id:col_id+4].dropna().values)
    imp_ctry.drop(index=[0,1,2],inplace=True)
    imp_ctry.columns = ["GWP","CED_renewable","CED_non-renewable","ES2013"]

    # Prepare index labels
    if is_old: # find right index labels
        ind = list(d.index.get_level_values(0)[1:].dropna().drop_duplicates() + " " + place)
    else:
        ind = list(d.iloc[:,[0,col_id]].dropna().iloc[:,0] + " " + place)

    for i in range(len(ind)): # Precise the country and change writing details
        ind[i] = ind[i].replace(")","").replace("(","").split(" ")
        if "" in ind[i]:
            ind[i].remove("")
        ind[i] = "_".join(ind[i]).replace("_Fossil","_fossil")

    if is_old: # remove some lines if needed
        ind = ind[:ind.index("Solar_{}".format(place))+1]
        imp_ctry.index = ind[1:] # write the indexes in the table

    else:
        imp_ctry.index = ind # write the indexes in the table
    imp_ctry.replace("-",0,inplace=True) # replace missing datas for computer understanding

    if cst_import: # put every value to constant like "Other"
        for k in imp_ctry.columns:
            imp_ctry.loc[:,k] = imp_other[k].values[0]

    return imp_ctry.reindex(expected+"_"+place,fill_value=0) # Set data in the right order + fill missing lines


# +

#################################
# ################################
# Residual from excel
# ################################
# ################################

# -

def residual_from_excel(impact_ch, mapping):
    """
    Load impact data of the production residual and add it to the impact matrix.
    Parameter:
        impact_ch: impact matrix of production means of Swizerland (pandas DataFrame)
        mapping: path to file with the mapping (str)
    Return:
        pandas DataFrame with the impact_ch, where the impact of residual production is added.
    """
    ### Addition of the residual data
    imp = impact_ch.copy()
    try: # test if the "country" is available in the mapping file
        d = pd.read_excel(mapping,sheet_name="Residue",index_col=0) # import
        # select
        d = pd.DataFrame(d.loc[["Residue_Hydro","Residue_Other"],
                               "Environmental impacts of ENTSO-E sources":].values,
                         columns=impact_ch.columns,
                         index=["Residual_Hydro_CH","Residual_Other_CH"])
        
        imp = pd.concat([d, imp],axis=0)
        
    except Exception as e:
        raise ValueError(f" Residual not available: {e}")
    
    return imp
