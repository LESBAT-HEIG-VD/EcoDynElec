import numpy as np
import pandas as pd
import os

########### Local functions
from checking import check_residual_avaliability


# +
#############################
# ############################
# Handle Residual
# ############################
# ############################

# +
#####################
# # Import Residual
# -

def import_residual(prod, sg_data, gap=None):
    """
    Function to insert the residue as a swiss production high voltage. Two residues are considered: hydro run off and the rest.
    
    Parameter:
        - prod: the production mix of Swizerland [pandas DataFrame] (Date should be as index)
        - sg_data: information from SwissGrid (pandas DataFrame)
        - gap: information about the nature of the residual (pandas DataFrame)
    
    Return:
        production mix with the Residue [pandas DataFrame]
    """
    ### Calculation of global resudual
    all_prod = prod.copy()
    init_cols = list(prod.columns)
    
    # Create residual
    residual_energy = sg_data.loc[:,'Production_CH'] - prod.sum(axis=1) # everything in "Residue_other"
    
    # Split residual into its nature
    all_prod["Residual_Hydro_CH"] = residual_energy * gap.loc[prod.index, "Hydro_Res"]
    all_prod["Residual_Other_CH"] = residual_energy * gap.loc[prod.index, "Other_Res"]
    
    # Reorder columns: residual as first production sources of Swizerland
    cols = ["Residual_Hydro_CH","Residual_Other_CH"] + init_cols
    return all_prod.loc[:,cols]


# +
#####################
# # Include Global residual
# -

def include_global_residual(Gen=None, freq='H', sg_data=None, prod_gap=None, is_verbose=False):
    """Function to add the residual swiss production
    Parameter:
        Gen: Gen: information about all production and cross-border flows (dict of pandas DataFrames)
        freq: the frequence (granularity)
        sg_data: information from SwissGrid (pandas DataFrame)
        prod_gap: information about the nature of the residual (pandas DataFrame)
        is_verbose: to display information
    Return:
        dict of modified generation and cross-border flows
    """
    #######################
    ###### Add Residue data
    #######################
    if is_verbose: print("\t5/5 - Add Residual...")
    
    
        
    # Set all residual prod.
    for f in Gen.keys():
        if f=="CH":
            # Check the availability of residual data
            check_residual_avaliability(prod=Gen[f], residual=prod_gap, freq=freq)
            
            # set the two residual kinds as CH prod
            Gen[f] = import_residual(Gen[f], sg_data=sg_data, gap=prod_gap)
            
        else: # for all other countries
            Gen[f]["Residual_Hydro_{}".format(f)] = np.zeros((Gen[f].shape[0],1))
            Gen[f]["Residual_Other_{}".format(f)] = np.zeros((Gen[f].shape[0],1))
            Gen[f] = Gen[f][list(Gen[f].columns[-2:])+list(Gen[f].columns[:-2])] # Move empty residual
            
    return Gen

# +







#########################
# ########################
# # LOCAL RESIDUAL
# ########################
# ########################

# +
########################
# ## Include local residual
# -

def include_local_residual(mix_data=None, sg_data=None, local_prod=None, gap=None, freq='H', target='CH'):
    """Funcion to include a local residual directly into the electric mix information.
    Parameter:
        mix_data: the electric mix table (pandas DataFrame)
        sg_data: information from SwissGrid (pandas DataFrame)
        local_prod: the production and exchanges in MWh of the target country (pandas DataFrame)
        gap: information about the nature of the residual (pandas DataFrame)
        freq: the time step
        target: the target country
    Return:
        modified mix table
    """
    # Check the availability
    check_residual_avaliability(prod=local_prod, residual=gap, freq=freq)
    
    # Relative part of the residual production in the elec produced & entering the target country
    residual = define_local_gap(local_prod=local_prod, sg_data=sg_data, freq=freq, gap=gap)
    
    # Adapt the mix to relative residual production
    new_mix = adjust_mix_local(mix_data=mix_data, local_residual=residual, target=target)
    
    return new_mix


# +

########################
# ## Define local gap
# -

def define_local_gap(local_prod, sg_data, freq='H', gap=None):
    """Function to define the relative part of residual in the electricity in the target country.
    Returns the relative residual information."""
    production = [k for k in local_prod.columns if k[:3]!='Mix']
    local_mix = [k for k in local_prod.columns if k[:3]=='Mix']
    
    # Residual prod in MWh
    d = import_residual(local_prod.loc[:,production], sg_data=sg_data, gap=gap)

    ## Add the mix -> Total produced + imported on the teritory
    d = pd.concat( [d, local_prod.loc[:,local_mix]], axis=1) # set back the imports

    ## Compute relative amount of residual column(s)
    residual_col = [k for k in d.columns if k.split("_")[0]=="Residual"]
    for k in residual_col:
        d.loc[:,k] /= d.sum(axis=1)

    return d.loc[:,residual_col]


# +
########################
# ## Adjust mix local
# -

def adjust_mix_local(mix_data, local_residual, target='CH'):
    """Function to modify the mix and integrate a local residual. Returns the modified mix data."""
    new_mix = mix_data.copy()

    ### Adjust the productions directly into electricity mix matrix
    new_mix.loc[:,f'Mix_{target}'] -=1 # Not consider the part produced and directly consummed in Swizerland
    for c in new_mix.columns:
        new_mix.loc[:,c] *= (1-local_residual.sum(axis=1)) # Reduce the actual part of the kWh
    for c in local_residual.columns: # put all the residual
        new_mix[c] = local_residual.loc[:,c] # Add the part of Residue
    
    # Locate first column for producers of target country
    lim = list(new_mix.columns).index([k for k in new_mix.columns
                                       if ((k[:3]!="Mix")&(k[-3:]==f"_{target}"))][0])
    
    # set back residual as first producer(s) of the target country
    new_col = (list(new_mix.columns)[:lim] + list(local_residual.columns)
               + list(new_mix.columns)[lim:-local_residual.shape[1]] )
    new_mix = new_mix.loc[:,new_col] # Reorder the columns
    new_mix.loc[:,f'Mix_{target}'] += 1 # Bring back the part of electricity produced and directly consummed in Swizerland

    return new_mix
