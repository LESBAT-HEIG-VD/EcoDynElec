"""
Collection of functions to perform a data autocomplete
"""

###############################
###############################
### IMPORTS
###
from itertools import groupby
import numpy as np
import pandas as pd


###############################
###############################
### PILOTE FUNCTION
###
def autocomplete(data:dict, n_hours:int=2, days_around:int=7, limit:float=.3,
                 ignore:bool=False, is_verbose:bool=False):
    """
    Main function to auto-complete the data. Works with generation and import.

    Parameters
    ----------
        data: dict
            the dict of data to auto-complete.
        n_hours: int, default to 2
            max number of hours missing in a row to consider a
            short gap and use linear interpolation.
        days_around: int, default to 7
            number of days before and after a long gap to be used
            when creating an average day to complete the gap.
        limit: float, default to 0.3
            max relative size of gap to allow an autocomplete. If a
            gap is longer than this fraction of the data, it will be
            filled with zeros.
        ignore: bool, default is False
            the missing data is flagged but not auto-completed. Displays
            a report if `is_verbose` is set to True.
        is_verbose: bool, default is False
            to display information during the process.

    Returns
    -------
    dict
        dict of data with autocompleted information
    pandas.DataFrame
        pandas DataFrame with resolutions
    """
    
    if is_verbose: print(f'Autocomplete...'+" "*15)
    
    ### ESTIMATE RESOLUTION
    resolution = infer_resolution(data)
    
    ### RESHAPE THE DATA
    new_data = {c: {field: to_original_series(data[c].loc[:,field],
                                              freq=resolution.loc[field,c])
                    for field in data[c].columns}
                for c in data}
    
    ### IDENTIFY DATA GAPS
    all_gaps = find_missing(new_data)
    
    if ignore:
        datasize = {c: {k: new_data[c][k].shape[0] for k in new_data[c]} for c in new_data}
        if is_verbose: report_missing(all_gaps, datasize)
    
        ### SET DATA BACK TO THEIR ORIGINAL FORMAT
        new_data = {c: pd.DataFrame({field: new_data[c][field]
                                     for field in new_data[c]})
                    for c in new_data}
        
        return new_data, resolution # return 'new_data'
    
    ### REDUCE SELECTION TO LONG GAPS
    long_thresholds = set_thresholds(new_data, resolution, n_hours=n_hours)
    lengths = set_lengths(new_data) # Compute lengths
    excess_thresholds = {c :{k: int(limit*lengths[c][k])
                             for k in lengths[c]}
                         for c in lengths}
    long_gaps = sort_gaps(all_gaps, lower=long_thresholds,
                          upper=excess_thresholds, lengths=lengths) # Sort gaps for long
    excess_gaps = sort_gaps(all_gaps, lower=excess_thresholds,
                            lengths=lengths) # Sort gaps for excess
    
    ### FILL LONG GAPS
    deltas = set_deltas(new_data, resolution, days_around=days_around)
    new_data = fill_all_periods(new_data, period_indexes=long_gaps,
                                deltas=deltas, is_verbose=is_verbose)
    
    ### FILL GAPS TO SKIP WITH ZEROS
    new_data = fill_all_excess(new_data, period_indexes=excess_gaps)
    
    ### SET DATA BACK TO THEIR ORIGINAL FORMAT
    new_data = {c: pd.DataFrame({field: new_data[c][field]
                                 for field in new_data[c]})
                for c in new_data}
    
    ### FILL SHORT GAPS AND RETURN
    new_data = fill_occasional(new_data)
    return new_data, resolution
    

###############################
###############################
### HELPER FUNCTIONS
###
def infer_resolution(data:dict):
    """Infers the resolution of all fields for all countries"""
    resolution = pd.DataFrame({c: {k: infer_one( data[c].loc[:,k].dropna(axis=0).index )
                                   for k in data[c].columns} # All still dataframes
                               for c in data})
    if not all(resolution.index.str.len()==2): # Generation
        return resolution.fillna(method='ffill').fillna(method='bfill')
    else: return resolution

def infer_one(obj):
    """Infer frequency for one single time Series"""
    freq = pd.infer_freq(obj) # Use built-in pandas
    if freq is not None: # but function is not robust
        return freq # at all...
    
    ### Back-up plan is to infer manually (smallest delta)
    components = {'15T':lambda x: getattr(x,'minutes')==15,
                  '30T':lambda x: getattr(x,'minutes')==30,
                  'H':lambda x: getattr(x,'hours')==1,
                  'D':lambda x: getattr(x,'days')==1,} # Possible frequencies
    tdelta = pd.Timedelta( np.diff(obj).min() ) # Shortest time delta between indexes
    # Identify the corresponding frequency (day, hour, 30min, 15min)
    freqs = pd.Series({k:components[k](tdelta.components) for k in components})
    return freqs.idxmax() # Get the index (frequency) of max (1st True or 15T)
        
    

def get_steps_per_hour(freq, dtype=int):
    """Retrieve resolution for a specific country and field.
    
    Parameters
    ----------
        freq: str
            the base frequency of the time series
        dtype: data-type, default to `int`
            the type of return. Default behavior returns an integer,
            i.e. zero when the frequency is lower than an hour. It may
            be convenient to sometimes return a fraction instead, using float.

    Returns
    -------
    dtype
        the number of time steps per hour to expect in a time series.
    """
    ### Make sure it starts with a number
    if not np.any([freq.startswith(k) for k in '0123456789']): # If starts with a letter
        frequency = f"1{freq}"
    else: frequency = freq
    
    return dtype( pd.Timedelta('1H') / pd.Timedelta(frequency) ) # Return nb of steps per hour

def set_lengths(data:dict):
    """
    Compute the length of each subcategory for each country
    """
    return {c: {k: data[c][k].shape[0]
                for k in data[c]}
            for c in data}

def set_deltas(data:dict, resolution, days_around:int):
    """
    Compute the deltas of each subcategory for each country
    for the creation of typical days.
    """
    return {c: {k: (days_around*24)*get_steps_per_hour(freq=resolution.loc[k,c])
                for k in data[c]}
            for c in data}

def set_thresholds(data:dict, resolution, n_hours:int):
    """
    Compute the thresholds of each subcategory for each country
    for the flagging of long gaps.
    """
    return {c: {k: n_hours*get_steps_per_hour(freq=resolution.loc[k,c])
                for k in data[c]}
            for c in data}

def to_original_series(obj, freq):
    """
    Scale data back to original resolution. Applicable to pandas Series only.
    """
    if not isinstance(obj, pd.core.series.Series): # Test on type
        raise TypeError(f"Only series are expected. {type(obj)} object was passed.")
    
    ### CONVERT DATA MW -> MWH BEFORE AUTO-COMPLETING (as the frequency is infered)
    return obj.resample(freq).asfreq() # Resample with original frequency 


###############################
###############################
### IDENTIFICATION OF GAPS
###
    
def find_missing(data:dict):
    """
    Identifies the missing values for the entire set of data.

    Parameters
    -----------
        data: dict of pandas DataFrames

            the data to process
    Returns
    --------
        dict (keys are countries) of dicts (keys are former columns)
        of matrices. Final matrix has one identified gap per row and
        three columns (length of gap, first..., and last index of gap)
    """
    return {c: {k: find_missing_one( series=data[c][k] ) # Find missing values
                for k in data[c]} # Iterate for every sub-category
            for c in data} # Iterate for every country


def find_missing_one(series):
    """
    Identifies all missing values for one single series.

    Parameters
    -----------
        series: pandas Series
            the data to process

    Returns
    --------
        Matrix (n x 3). Final matrix has one identified gap
        per row (n rows) and three columns (length of gap,
        first..., and last index of gap)
    """
    ### Identify if data point is NaN or not
    vecNan = np.isnan(series.to_numpy())
    
    ### Count the isna() similar values in a row (either False or True)
    count_series = np.array([(x,len(list(y))) for x,y in groupby(vecNan)])

    if count_series[0][0]==1: # Correction if first data is missing
        count_series = np.concatenate([[[0,0]],count_series])

    if count_series[-1][0]==0: # Correcti0n if last data is available
        count_series = count_series[:-1]
        
    ### Accumulating the sum gives you pairs of
    ### (1st idx - last idx) for missing values
    cum_series = count_series[:,1].cumsum()
        
    ### Compute the length of each gap   
    len_gaps = cum_series[1::2] - cum_series[::2]
    
    ### Gather results in a table (col1: length, col2: start index, col3: end index)
    return np.concatenate([[len_gaps], cum_series.reshape(cum_series.shape[0]//2,2).T, ], axis=0).T.astype('int32')



###############################
###############################
### SORTING OF GAPS
###

def sort_gaps(gaps:dict, lower:dict, lengths:dict, upper:dict=None):
    """
    Identify long gaps (above threshold).
    Needs the length of data for specific processes
    """
    if upper is None:
        upper = {c: {k: None for k in gaps[c]} for c in gaps}
        
    return {c: {k: select_long_gaps(gaps[c][k], name=k,
                                    lower=lower[c][k],
                                    upper=upper[c][k],
                                    length=lengths[c][k])
                for k in gaps[c]}
            for c in gaps}

def select_long_gaps(gaps, name, lower, upper, length):
    """
    Identify long gaps for one subcategory of one country
    with one unique threshold. Can make exception with
    some cases, e.g. solar at the extremes of dataset.
    """
    ### Select all longer than threshold
    if upper is not None:
        long_gaps = gaps[np.logical_and(upper>gaps[:,0], gaps[:,0]>lower)] 
    else:
        long_gaps = gaps[gaps[:,0]>lower] 
    
    ### Handle specific gaps
    if ((gaps.shape[0]>0)&(upper is None)):
        long_gaps = add_specific_gaps(gaps, name, length, long_gaps)
    
    return long_gaps

def add_specific_gaps(all_gaps, name, length, long_gaps):
    ### Specific to solar data
    # At the start
    if np.logical_and.reduce([name == 'Solar', # If solar
                              all_gaps[0,1]==0, # If gap at the start
                              all_gaps[0] not in long_gaps]): # If not already long gap
        long_gaps = np.concatenate( [all_gaps[[0]],long_gaps], axis=0 )
    # At the end
    if np.logical_and.reduce([name == 'Solar', # If solar
                              all_gaps[-1,2]==length, # If gap at the end
                              all_gaps[-1] not in long_gaps]): # If not already long gap
        long_gaps = np.concatenate( [long_gaps, all_gaps[[-1]] ], axis=0 )
    
    return long_gaps


###############################
###############################
### COMPLETE GAPS
###
def fill_all_periods(data:dict, period_indexes:np.ndarray, deltas:dict, is_verbose:bool=False):
    """Fills all long gaps.

    Parameters
    ----------
        data: dict
            collection of data, with structure being `{country: { unit: pandas.Series } }`
        period_indexes: numpy.ndarray
            matrix indicating the location and length of long gaps
        deltas: dict
            collection of number of time steps to create the average days around gaps.
            Structure is `{country: {unit: {gap_id: int} } }`.
        is_verbose: bool, default to False
            to display information.
    """
    
    for i,c in enumerate(data): # For all countries
        ### Fill the periods
        for j,k in enumerate(data[c]): # For all elements of each country
            if is_verbose: print(f"\t{c} ({i+1:02d}/{len(data):02d}); field {j+1:02d}/{len(data[c]):02d})"+" "*10, end='\r')
            data[c][k] = fill_one_series(data[c][k], period_indexes[c][k], delta=deltas[c][k]) # Fill the data
    
    if is_verbose: print("\tCompleted."+" "*30)
    return data
    
def fill_one_series(data, period_indexes, delta):
    """Fills all long gaps for one single series in one country"""
    filled = data.copy()
    for gap in period_indexes:
        ### Create Average Day
        avg_day = filled.iloc[gap[1]-delta : gap[2]+delta].groupby(lambda x: x.strftime('%H:%M')).mean()
        ### Fill the period
        filled.iloc[gap[1]:gap[2]] = fill_one_period(avg_day, to_fill=filled.iloc[gap[1]:gap[2]])
    return filled

def fill_one_period(avg_day, to_fill):
    """Fills one single long gap using one average day."""
    filled = pd.Series(None, index=to_fill.index, name=to_fill.name, dtype='float32')
    for t in avg_day.index:
        filled.loc[filled.index.strftime('%H:%M')==t] = avg_day.loc[t]
    return filled

def fill_all_excess(data:dict, period_indexes:dict):
    """Fills with zeros the fields that were skipped"""
    
    for i,c in enumerate(data): # For all countries
        ### Fill the periods
        for j,k in enumerate(data[c]): # For all elements of each country
            for gap in period_indexes[c][k]:
                data[c][k].iloc[gap[1]:gap[2]] = data[c][k].iloc[gap[1]:gap[2]].fillna(0) # Write 0 where gaps
    
    return data

def fill_occasional(data:dict):
    """Fills short gaps of data with linear interpolation."""
    return {c: data[c].interpolate(method='linear', limit_direction='both') for c in data}


##########################
### SKIP AUTO-COMPLETE
###
def report_missing(gaps:dict, datasizes:dict):
    """Count and display missings"""
    displaying = {}
    for c in gaps:
        displaying[c] = {}
        for k in gaps[c]:
            if 0 in gaps[c][k].shape: # empty
                displaying[c][k]=0
            else:
                displaying[c][k]=gaps[c][k][:,0].sum()
                
    displaying = pd.DataFrame.from_dict(displaying).fillna(0).astype(int)
    miss,size = displaying.values.sum(), pd.DataFrame(datasizes).fillna(0).values.sum()
    print("="*25)
    print(f"Missing data identified: {miss} ({100*miss/size:.2f}%)")
    print(displaying.replace(0,'-'))
    print("="*25)
    return
