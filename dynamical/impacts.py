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


def compute_impacts(mix_data, impact_data, strategy='error', is_verbose=False):
    """Computes the impacts based on electric mix and production means impacts.
    Parameter:
        mix_data: information about the electric mix in the target country (pandas DataFrame)
        impact_data: impact matrix for all production units (pandas DataFrame)
        is_verbose: to display information (bool, default: False)
    Return:
        dict of pandas DataFrame containing the impacts."""
    
    t3 = time()
    
    impacts_matrix = adapt_impacts(impact_data, mix=mix_data, strategy=strategy)
    
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

def adapt_impacts(impact_data, mix, strategy='error'):
    """Adapt the mix data if there is a residual to consider."""
    impact = impact_data.copy()

    # adapt the impact data to the production unit for Residual
    if "Residual_Other_CH" not in mix.columns:
        if "Residual_Other_CH" in impact.index:
            impact = impact.drop(index="Residual_Other_CH") # remove from the impacts if not existing in mix
    
    return equalize_impact_vector(impact, mix, strategy=strategy)


#
###############################################################################
# #############################
# # Equalize impact matrix
# #############################
# #############################

def equalize_impact_vector(impact_data, mix, strategy='error'):
    """Make sure the impact vector is aligned with the suggested production values.
    Fill with zeros impacts for the missing capacities."""
    ### Identify missing
    units_from_mix = [((not u.startswith('Mix_'))|(u.endswith('_Other')))
                      for u in mix.columns]
    
    ### Create new indexes
    new_impacts = pd.DataFrame( None, index=mix.columns[units_from_mix], columns=impact_data.columns, dtype='float32' )
    new_impacts.loc[impact_data.index, :] = impact_data # Fill already known
    
    ### Fill the missing values
    if new_impacts.isna().to_numpy().sum()>0: # If some data still missing
        ### Identify all units with no mapping
        missing_mapping = new_impacts.index[new_impacts.isna().sum(axis=1)>0]
        ### Identify all units with no production
        locate = np.logical_and( units_from_mix, mix.sum()==0 )
        missing_prod = mix.columns[locate]
        ### Cross the information: problematic units
        problem_units = missing_mapping[~missing_mapping.str.contains("|".join(missing_prod))]

        ### TARGET THE PROBLEMATIC UNITS FIRST (not completing the zeros before)
        if len(problem_units)>0:
            if strategy.lower() in ['raise', 'error']:
                raise ValueError(f"The following units have no mapping: {problem_units}")
            elif strategy.lower()=='worst':
                new_impacts.loc[problem_units,:] = strategy_worst(problem_units, new_impacts)
            elif strategy.lower()=='unit':
                new_impacts.loc[problem_units,:] = strategy_unit(problem_units, new_impacts)
            else:
                raise ValueError(f"Strategy `{strategy}` to infer missing impacts is unknown. Use 'error','worst' or 'unit'.")

    return new_impacts.fillna(0.).astype('float32') # Complete the missing non-producing units with zeros


#
###############################################################################
# #############################
# # Strategies to infer impacts
# #############################
# #############################

def strategy_worst(units, mapping):
    section = mapping.loc[units,:].copy() # Copy the whole empty part
    section.loc[units,:] = mapping.max().values # Set the worst impacts
    return section

def strategy_unit(units, mapping):
    ### WORST CASE PER UNIT TYPE, then worst case if no similar units in mapping
    worst_units = pd.DataFrame({unit: mapping.loc[ (mapping.index.str
                                                    .startswith(unit)) ].max()
                                for unit in np.unique(units.str[:-3])}).T
    worst_units.loc[worst_units.isna().sum(axis=1)!=0] = mapping.max().values
    
    ### CREATE A TABLE WITH INFERED IMPACTS
    section = mapping.loc[units,:].copy() # Copy the whole empty part
    for unit in units:
        section.loc[unit,:] = worst_units.loc[unit[:-3],:].to_numpy()
    return section


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
