import numpy as np
import pandas as pd
import os
from time import time


#
#
#
"""
#############################
# Compute impacts
#############################
#############################
"""


def compute_impacts(mix_data, impact_data, is_verbose=False):
    """Computes the impacts based on electric mix and production means impacts.
    Parameter:
        mix_data: information about the electric mix in the target country (pandas DataFrame)
        impact_data: impact matrix for all production units (pandas DataFrame)
        is_verbose: to display information (bool, default: False)
    Return:
        dict of pandas DataFrame containing the impacts."""
    
    t3 = time()
    
    impacts_matrix = adapt_impacts(impact_data, production_units=mix_data.columns)
    
    if is_verbose: print("Compute the electricity impacts...\n\tGlobal...")
    collect_impacts = {}
    collect_impacts['Global'] = compute_global_impacts(mix_data=mix_data, impact_data=impacts_matrix,)
    
    
    for i in impacts_matrix.columns:
        if is_verbose: print("\t{}...".format(i))
        collect_impacts[i] = compute_detailed_impacts(mix_data=mix_data, impact_data=impacts_matrix.loc[:,i],
                                                      indicator=i)
    
    if is_verbose: print("Impact computation: {} sec.".format(round(time()-t3,1))) # time report

    return collect_impacts


#
###############################################################################
# #############################
# # Adapt impacts
# #############################
# #############################

def adapt_impacts(impact_data, production_units):
    """Adapt the mix data if there is a residual to consider."""
    impact = impact_data.copy()

    # adapt the impact data to the production unit for Residual
    if "Residual_Other_CH" not in production_units:
        if "Residual_Other_CH" in impact.index:
            impact = impact.drop(index="Residual_Other_CH") # remove from the impacts if not existing in mix
    
    return equalize_impact_vector(impact, production_units)


#
###############################################################################
# #############################
# # Equalize impact matrix
# #############################
# #############################

def equalize_impact_vector(impact_data, production_units):
    """Make sure the impact vector is aligned with the suggested production values.
    Fill with zeros impacts for the missing capacities."""
    ### Identify missing
    units_from_mix = [u for u in production_units
                      if ((not u.startswith('Mix_'))|(u.endswith('_Other')))]
    
    ### Create new indexes
    new_impacts = pd.DataFrame( None, index=units_from_mix, columns=impact_data.columns, dtype='float32' )
    new_impacts.loc[impact_data.index, :] = impact_data # Fill already known
    return new_impacts.fillna(0) # Put zeros to units without impact for homogeneity


#
###############################################################################
# #############################
# # Compute global impacts
# #############################
# #############################

def compute_global_impacts(mix_data, impact_data):
    """Computes the overall impacts of electricity for each indicator"""
    ###############################################
    # Computation of global impact
    ###############################################

    # All production units and the "other countries" are considered
    mix = mix_data.drop(columns=[k for k in mix_data.columns
                                 if ((k.split("_")[0]=="Mix")&(k.find("Other")==-1))]) # delete "Mix"

    
    # Compute the impacts
    pollution = pd.DataFrame(np.dot(mix.values,impact_data.loc[mix.columns].values),
                             index=mix.index,columns=impact_data.columns)

    return pollution


#
###############################################################################
# #############################
# # Compute detailed impacts
# #############################
# #############################

def compute_detailed_impacts(mix_data, impact_data, indicator):
    """Computes the impacts of electricity per production unit for a given indicator"""
    #####################################################
    # Computation of detailed impacts per production unit
    #####################################################

    # All production units and the "other countries" are considered
    mix = mix_data.drop(columns=[k for k in mix_data.columns
                                 if ((k.split("_")[0]=="Mix")&(k.find("Other")==-1))]) # delete "Mix"
    
    # Impact data already charged & grid data already without useless "Mix" columns
    pollution = pd.DataFrame(np.dot(mix,np.diag(impact_data.loc[mix.columns])),
                             columns=mix.columns, index=mix.index) # Calculation & storage
    pollution.rename_axis("{}_source".format(indicator),
                          axis="columns",inplace=True) # Rename the main axis of the table
    
    return pollution
