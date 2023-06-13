"""The module `residual` handles the inclusion of additional local production
not considered in ENTSO-E utility-level data.
"""
import numpy as np
import pandas as pd

########### Local functions
from ecodynelec.checking import check_residual_availability


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

def import_residual(prod, sg_data, gap):
    """
    Function to insert the residue as a swiss production high voltage. Two residues are considered: hydro run off and the rest.
    
    Parameters
    ----------
        prod: `pandas.DataFrame`
            the production mix of Swizerland. Rquires indexes to be datetime.
        sg_data: `pandas.DataFrame`
            information from SwissGrid
        gap: `pandas.DataFrame`
            information about the nature of the residual
    
    Returns
    -------
    `pandas.DataFrame`
        production mix with the Residue
    """

    ### Calculation of global resudual
    all_prod = prod.copy()
    init_cols = list(prod.columns)

    # Create residual
    residual_energy = np.maximum(0, sg_data.loc[:, 'Production_CH'] - prod.sum(axis=1))  # all in "Residue_other"

    # Split residual into its nature
    all_prod["Residual_Hydro_Water_Reservoir_CH"] = residual_energy * gap.loc[prod.index, "Hydro_Water_Reservoir_Res"]
    all_prod["Residual_Hydro_Run-of-river_and_poundage_CH"] = residual_energy * gap.loc[
        prod.index, "Hydro_Run-of-river_and_poundage_Res"]
    all_prod["Residual_Other_CH"] = residual_energy * gap.loc[prod.index, "Other_Res"]

    # Reorder columns: residual as first production sources of Swizerland
    cols = ["Residual_Hydro_Water_Reservoir_CH", "Residual_Hydro_Run-of-river_and_poundage_CH",
            "Residual_Other_CH"] + init_cols
    return all_prod.loc[:, cols]


# +
#####################
# # Include Global residual
# -

def include_global_residual(Gen=None, freq='H', sg_data=None, prod_gap=None, is_verbose=False):
    """Function to add the residual swiss production

    Parameters
    ----------
        Gen: dict
            information about all production and cross-border flows
        freq: str, default to 'H'
            the frequency of time step
        sg_data: pandas.DataFrame, default to None
            information from SwissGrid
        prod_gap: pandas.DataFrame, default to None
            information about the nature of the residual
        is_verbose: bool, default to None
            to display information
    Returns
    -------
    dict
        dict tables containing the modified generation and cross-border flows
    """
    #######################
    ###### Add Residue data
    #######################
    if is_verbose: print("\t5/5 - Add Residual...")

    # Set all residual prod.
    for f in Gen.keys():
        if f == "CH":
            # Check the availability of residual data
            check_residual_availability(prod=Gen[f], residual=prod_gap, freq=freq)

            # set the two residual kinds as CH prod
            Gen[f] = import_residual(Gen[f], sg_data=sg_data, gap=prod_gap)

        else:  # for all other countries
            Gen[f]["Residual_Hydro_Water_Reservoir_{}".format(f)] = np.zeros((Gen[f].shape[0], 1))
            Gen[f]["Residual_Hydro_Run-of-river_and_poundage_{}".format(f)] = np.zeros((Gen[f].shape[0], 1))
            Gen[f]["Residual_Other_{}".format(f)] = np.zeros((Gen[f].shape[0], 1))
            Gen[f] = Gen[f][list(Gen[f].columns[-2:]) + list(Gen[f].columns[:-2])]  # Move empty residual

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
    """Function to include a local residual directly into the electric mix information.

    Parameters
    ----------
        mix_data: pandas.DataFrame
            the electric mix table
        sg_data: pandas.DataFrame
            information from SwissGrid
        local_prod: pandas.DataFrame
            the production and exchanges in MWh of the target country
        gap: pandas.DataFrame
            information about the nature of the residual
        freq: str, default to 'H'
            the frequency of time step
        target: str, default to 'CH'
            the target country

    Returns
    -------
    pandas.DataFrame
        mix table enhanced with local residual information
    """
    # Check the availability
    check_residual_availability(prod=local_prod, residual=gap, freq=freq)

    # Relative part of the residual production in the elec produced & entering the target country
    residual = define_local_gap(local_prod=local_prod, sg_data=sg_data, freq=freq, gap=gap)

    # Adapt the mix to relative residual production
    new_mix = adjust_mix_local(mix_data=mix_data, local_residual=residual, target=target)

    return new_mix


# +

########################
# ## Define local gap
# -

def define_local_gap(local_prod, sg_data, gap=None):
    """Function to define the relative part of residual in the electricity in the target country.

    Parameters
    ----------
        local_prod: pandas.DataFrame
            production data for a single country
        sg_data: pandas.DataFrame, default to None
            information from SwissGrid
        gap: pandas.DataFrame, default to None
            information about the nature of the residual

    Returns
    -------
    pandas.DataFrame
        the relative residual information.
    """
    production = [k for k in local_prod.columns if k[:3] != 'Mix']
    local_mix = [k for k in local_prod.columns if k[:3] == 'Mix']

    # Residual prod in MWh
    d = import_residual(local_prod.loc[:, production], sg_data=sg_data, gap=gap)

    ## Add the mix -> Total produced + imported on the teritory
    d = pd.concat([d, local_prod.loc[:, local_mix]], axis=1)  # set back the imports

    ## Compute relative amount of residual column(s)
    residual_col = [k for k in d.columns if k.split("_")[0] == "Residual"]
    total = d.sum(axis=1)
    for k in residual_col:
        d.loc[:, k] /= total

    return d.loc[:, residual_col]


# +
########################
# ## Adjust mix local
# -

def adjust_mix_local(mix_data, local_residual, target='CH'):
    """Function to modify the mix and integrate a local residual.

    Parameters
    ----------
        mix_data: pandas.DataFrame
            the electric mix table
        local_prod: pandas.DataFrame
            the production and exchanges in MWh of a country
        target: str, default to 'CH'
            the target country

    Returns
    -------
    pandas.DataFrame
        the modified mix data including low-voltage production mix.
    """
    new_mix = mix_data.copy()

    ### Adjust the productions directly into electricity mix matrix
    new_mix.loc[:, f'Mix_{target}'] -= 1  # Not consider the part produced and directly consummed in Swizerland
    for c in new_mix.columns:
        new_mix.loc[:, c] *= (1 - local_residual.sum(axis=1))  # Reduce the actual part of the kWh

    # put all the residual
    new_mix = pd.concat([new_mix, local_residual], axis=1)  # Add the part of Residue

    # Locate first column for producers of target country
    lim = list(new_mix.columns).index([k for k in new_mix.columns
                                       if ((k[:3] != "Mix") & (k[-3:] == f"_{target}"))][0])

    # set back residual as first producer(s) of the target country
    new_col = (list(new_mix.columns)[:lim] + list(local_residual.columns)
               + list(new_mix.columns)[lim:-local_residual.shape[1]])
    new_mix = new_mix.loc[:, new_col]  # Reorder the columns
    new_mix.loc[:,
    f'Mix_{target}'] += 1  # Bring back the part of electricity produced and directly consummed in Swizerland

    return new_mix
