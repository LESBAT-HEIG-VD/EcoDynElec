import sys
import numpy as np
import pandas as pd
from warnings import warn


#
#
#
#
#
#
#
# ############################
# ############################
# # Check frequency
# ############################
# ############################

def check_frequency(freq):
    """Verifies if the requested frequency is supported"""
    allowed = ["Y","YS","M","MS","W","w","D","d","H","30min","30T","15min","15T"]
    if freq not in allowed:
        raise KeyError(f'the specified timestep must be in {allowed}')
    return True


#
#
#
#
#
#
#
# ############################
# ############################
# # Check regular frequency
# ############################
# ############################

def check_regularity_frequency(freq):
    """Verifies if the requested frequency is regular for pandas"""
    acceptable = ['15T','15min','30T','30min','H','d','D','w','W']
    return freq in acceptable


#
#
#
#
#
#
#
# ############################
# ############################
# # Check mapping availability
# ############################
# ############################

def check_mapping(mapping, mix, strategy='error'):
    ### Production Units with non-null production
    locate = np.logical_and(~mix.columns.str.startswith('Mix_'), mix.sum()!=0)
    with_prod = mix.columns[locate]

    ### Active production units with no mapping
    in_mapping = with_prod.str.contains("|".join(mapping.index))
    
    if not all(in_mapping):
        units = list(with_prod[~in_mapping])
        if strategy.lower() in ['raise','error']:
            raise ValueError(f"The following units do produce and have no mapping: {units}")
        else:
            warning_msg = f"The following units do produce and have no mapping: {units}."
            warning_msg += f" Impact values will be inferred following the strategy `{strategy}`."
            warn(warning_msg); sys.stderr.flush()
    
    return True


#
#
#
#
#
# ############################
# ############################
# # Check residual availability
# ############################
# ############################

def check_residual_avaliability(prod, residual, freq='H'):
    """Verifies if the residual information are available for the whole duration.
    Parameter:
        prod: the production data where to add the residual
        residual: the residual data to check the availability of.
    Return:
        True, if no exception is raised.
    """
    available=True
    text=""
    if freq!="Y": # NOT yearly step of time
        if (( (prod.index.month[0]<residual.index.month[0])
              &(prod.index.year[0]==residual.index.year[0]))
            |(prod.index.year[0]<residual.index.year[0])):
            text+="\nResidual data only avaliable for {}-{}. ".format(residual.index.year[0],
                                                                      residual.index.month[0])
            text+="Data from {}-{} required.\n".format(prod.index.year[0],prod.index.month[0])
            available=False
        if (( (prod.index.month[-1]>residual.index.month[-1])
              &(prod.index.year[-1]==residual.index.year[-1]))
            |(prod.index.year[-1]>residual.index.year[-1])):
            text+="\nResidual data only available until {}-{}. ".format(residual.index.year[-1],
                                                                        residual.index.month[-1])
            text+="Data until {}-{} required.".format(prod.index.year[-1],prod.index.month[-1])
            available=False
    else: # yearly step of time
        if (prod.index.year[0]<residual.index.year[0]):
            text+="\nResidual data only starting at {}. ".format(residual.index.year[0])
            text+="Data starting at {} required.\n".format(prod.index.year[0])
            available=False
        if prod.index.year[-1]>residual.index.year[-1]:
            text+="\nResidual data only until {}. ".format(residual.index.year[-1])
            text+="Data until {} required.".format(prod.index.year[-1])
            available=False
            
    if not available:
        raise IndexError(text)
    return True
