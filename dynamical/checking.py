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
# # Custom Errors and Warnings
# ############################
# ############################
class IncompleteError(ValueError):
    """Error if NaNs are found in the mapping"""
    def __init__(self, message):
        super().__init__(message)

class MissingError(ValueError):
    """Error if units are missing in the mapping"""
    def __init__(self, message=''):
        super().__init__(message)
    
class IncompleteWarning(UserWarning):
    """Warning if NaNs are found in the mapping"""
    def __init__(self, message):
        super().__init__(message)

class MissingWarning(UserWarning):
    """Warning if units are missing in the mapping"""
    def __init__(self, message):
        super().__init__(message)


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
    """Verifies if the requested frequency is supported

    Parameters
    ----------
        freq: str
            the frequency to test

    Raises
    ------
    KeyError
        Error if the frequency is no allowed.
    """
    allowed = ["Y","YS","M","MS","W","w","D","d","H","30min","30T","15min","15T"]
    if freq not in allowed:
        raise ValueError(f'the specified timestep must be in {allowed}')
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
    """Verifies if the requested frequency is regular for pandas.
    The set of accepted frequencies is smaller in pandas, up to weeks.

    Parameters
    ----------
        freq: str
            the frequency to test
    
    Returns
    -------
    bool
        True if the frequency is valid for `Pandas`, false otherwise."""
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
    """Verifies if a producing unit has no associated impacts.
    Depending on the strategy, an error or a warning is raised.

    Parameters
    ----------
        mapping: pandas.DataFrame
            the table of impacts
        mix: pandas.DataFrame
            the table containing electricity mix. Valid before
            and after electricity tracking.
        strategy: str, default to 'error'
            the way to treat missing impacts for producing units.
            
    Raises
    ------
    ValueError
        if the strategy is 'raise' or 'error', a missing value raises
        a `ValueError`.
    """
    ### Production Units with non-null production
    locate = np.logical_and(~mix.columns.str.startswith('Mix_'), mix.sum()!=0)
    with_prod = mix.columns[locate]

    ### Active production units with no mapping
    in_mapping = with_prod.str.contains("|".join(mapping.index))
    
    ### Identifies the issues
    
    if not all(in_mapping): # I.e. if some producing units are not referenced in mapping
        units = list(with_prod[~in_mapping])
        if strategy.lower() in ['raise','error']:
            raise MissingError(f"The following units do produce and have no mapping: {units} ({strategy})")
        else:
            warning_msg = f"The following units do produce and have no mapping: {units}."
            warning_msg += f" Impact values will be inferred following the strategy `{strategy}`."
            warn(warning_msg, MissingWarning)
            sys.stderr.flush()
    
    else: # i.e. all producing units have a reference in mapping
        locNaN = np.where(mapping.loc[with_prod[in_mapping]].isna()) # Prod units with NaN in Mapping
        withNaN = {with_prod[i]: list(mapping.columns[locNaN[1][locNaN[0]==i]])
                   for i in np.unique(locNaN[0])} # List of tech with NaN for some indexes
        if withNaN: # If not empty
            if strategy.lower() in ['raise','error']:
                raise IncompleteError(f"Missing impact values for the following active producers: {withNaN}({strategy})")
            else:
                warning_msg = f"The following active producers are missing some impact values: {withNaN}"
                warning_msg += f" Impact values will be inferred following the strategy `{strategy}`."
                warn(warning_msg, IncompleteWarning)
                sys.stderr.flush()
    
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

def check_residual_availability(prod, residual, freq='H'):
    """Verifies if the residual information are available for the whole duration.

    Parameters
    ----------
        prod: pandas.DataFrame
            the production data where to add the residual
        residual: pandas.DataFrame
            the residual data to check the availability of.
        freq: str, default to 'H'
            the frequency to consider

    Returns
    -------
    bool
        True, if no exception is raised.

    Raises
    ------
    IndexError
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
