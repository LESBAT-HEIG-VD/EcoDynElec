# -*- coding: utf-8 -*-
import numpy as np
import pandas as pd
import os
import warnings

################# Local functions
from dynamical.checking import check_frequency


# +

###########################
# ##########################
# Load SwissGrid
# ##########################
# ##########################

# -

def load_swissGrid(path_sg, start=None, end=None, freq='H'):
    """
    Function to load production and cross-border flows information from Swiss Grid. Data used many times
    along the algorithm.
    Parameter:
        path_sg: path to the file with Swiss Grid information (str)
        start: starting date (datetime or str, default None)
        end: ending date (datetime or str, default None)
        freq: time step (str, default H)
    Return:
        pandas DataFrame with SwissGrid information in MWh and at the good time step.
    """
    ### Default path
    if path_sg is None:
        path_sg = get_default_file(name='SwissGrid_total.csv')
        
    ### Date safety
    if start is not None: start = pd.to_datetime(start)
    if end is not None: end = pd.to_datetime(end)
    
    ### Import SwissGrid data
    parser = lambda x: pd.to_datetime(x, format='%d.%m.%Y %H:%M')
    sg = pd.read_csv(path_sg, index_col=0, parse_dates=[0], date_parser=parser,dtype="float32")
    
    sg = sg.drop(columns=["Consommation_CH","Consommation_Brut_CH"]) # Remove unused columns
    # Clear ambiguous dates and set dates to utc
    sg = clear_ambiguous_dates(sg).tz_localize(tz='CET',ambiguous='infer').tz_convert(tz='UTC').tz_localize(None)
    sg.index -= pd.Timedelta("15min") # starts at 00:00 CET (not 00:15)
    
    ### Check info availability (/!\ if sg smaller, big problem not filled yet !!!)
    if 'Production_CH' not in sg.columns:
        raise KeyError("Missing information 'Production_CH' in SwissGrid Data.")
    if ((start is None) | (end is None)):
        warning = "  /!\ Some date limits are None. SwissGrid is on period {} - {}. It may not match the Generation and Exchange."
        warnings.warn(warning.format(sg.loc[start:end].index[0],sg.loc[start:end].index[-1]))
    elif ((start<sg.index[0])|(end>sg.index[-1])): # print information only
        warning = "  /!\ Resudual computed only during {} - {}. SwissGrid Data not available on the rest of the period."
        warnings.warn(warning.format(sg.loc[start:end].index[0],sg.loc[start:end].index[-1]))
        
    ### Rename the columns
    sg.columns = ["Production_CH","Mix_CH_AT","Mix_AT_CH","Mix_CH_DE","Mix_DE_CH",
                  "Mix_CH_FR","Mix_FR_CH","Mix_CH_IT","Mix_IT_CH"]

    ### Select the interesting data, resample to right frequency and convert kWh -> MWh
    return sg.loc[start:end,:].resample(freq).sum() / 1000


# +


###########################
# #########################
# Clear Ambiguous Dates
# #########################
###########################

# -

def clear_ambiguous_dates(sg):
    """Function to clear ambiguous dates in SwissGrid raw data"""
    # Gather ambiguous dates
    ambiguous = pd.Series(np.unique(sg.index,return_counts=True)[1], index=np.unique(sg.index),
                          name='Occurrence').reset_index()
    ambiguous = ambiguous[((ambiguous.loc[:,'Occurrence']==2)
                           &(ambiguous.loc[:,'index']==ambiguous.loc[:,'index'].round("H")))]

    # Create the new date for ambiguous dates
    ambiguous['replace'] = ambiguous.loc[:,'index'].apply(lambda x: x if x.hour==2 else x-pd.Timedelta("1H"))

    # Find the right index of first occurrence
    ambiguous.index = pd.Series(np.arange(sg.shape[0]),index=sg.index).loc[ambiguous.loc[:,'index']].values[::2]
    
    # Clear SG dates
    sg_cleared = sg.reset_index()
    sg_cleared.loc[ambiguous.index,"Date"] = ambiguous.loc[:,'replace']
    return sg_cleared.set_index("Date")


# +

###########################
# ##########################
# Load useful countries
# ##########################
# ##########################

# -

def load_useful_countries(path_neighbour, ctry):
    """
    Function to load a list of countries directly or indirectly involved in the computation.
    Countries directly involved are passed as arguments. Countries indirectly involved are their
    neighbours. These indirectly involved countries help building the import from 'other' countries.
    """
    ### Default path
    if path_neighbour is None:
        path_neighbour = get_default_file(name='Neighbourhood_EU.csv')
    
    ### For importing only the usefull data
    neighbouring = pd.read_csv(path_neighbour,index_col=0)
    useful = list(ctry) # List of countries considered + neighbours
    for c in ctry:
        useful += list(neighbouring.loc[c].dropna().values)
    useful = list(np.unique(useful)) # List of the useful countries, one time each.
    return useful


# +

###########################
# ##########################
# Load GridLosses
# ##########################
# ##########################

# -

def load_grid_losses(network_loss_path, start=None, end=None):
    """
    Function that loads network grid losses and returns a pandas DataFrame with the fraction of
    network loss in the transmitted electricity for each month.
    """
    ### Default path
    if network_loss_path is None:
        network_loss_path = get_default_file(name='Pertes_OFEN.csv')
    
    # Get and calculate new power demand for the FU vector
    losses = pd.read_csv(network_loss_path)
    losses['Rate'] = 1 + (losses.loc[:,'Pertes']/losses.loc[:,'Conso_CH'])

    if start is None:
        if end is None:
            output = losses.loc[:, ['annee','mois','Rate']].rename(columns={'annee':'year','mois':'month'})
            return output.reset_index(drop=True)
        else:
            end = pd.to_datetime(end) # Savety, redefine as datetime
            localize = (losses.annee<=end.year)
    else:
        start = pd.to_datetime(start) # Savety, redefine as datetime
        if end is None:
            localize = (losses.annee>=start.year)
        else:
            end = pd.to_datetime(end) # Savety, redefine as datetime
            localize = ((losses.annee>=start.year) & (losses.annee<=end.year))
    output = losses.loc[localize, ['annee','mois','Rate']].rename(columns={'annee':'year', 'mois':'month'})
    return output.reset_index(drop=True)


# +

###########################
# ##########################
# Load gap content
# ##########################
# ##########################

# -

def load_gap_content(path_gap, start=None, end=None, freq='H', header=59):
    """
    Function that defines the relative composition of the swiss residual production. The function is very
    file format specific.
    Parameter:
        path_gap: path to the file containing residual content information (str)
        start: starting date (datetime or str, default None)
        end: ending date (datetime or str, default None)
        freq: time step (str, default H)
        header: row in the file to use as header (int, default 59)
    Return:
        pandas DataFrame with relative residual production composition for each time step.
    """
    ### Default path
    if path_gap is None:
        path_gap = get_default_file(name='Repartition_Residus.xlsx')
    
    interest = ['Centrales au fil de l’eau','Centrales therm. classiques et renouvelables']
    df = pd.read_excel(path_gap, header=header, index_col=0).loc[interest].T
    df["Hydro_Res"] = df['Centrales au fil de l’eau']/df.sum(axis=1) # calculate the % part of each potential source
    df["Other_Res"] = 1-df.loc[:,'Hydro_Res']
    
    df.index = pd.to_datetime(df.index,yearfirst=True) # time data
    
    ###########################
    ##### Adapt the time resolution of raw data
    #####
    # If year or month -> resample at start ('S') of month/year with average of info
    localFreq = freq # copy frequency
    if freq[0] in ["M","Y"]:
        localFreq = freq[0]+"S" # specify at 'start'
        df = df.resample(localFreq).mean()
    # If in week -> resample with average
    elif freq in ['W','w']:
        localFreq = 'd' # set local freq to day (to later sum in weeks)

    ###############################
    ##### Select information
    #####
    res_start, res_end = None,None
    if start is not None:
        start = pd.to_datetime(start) # Savety, redefine as datetime
        res_start = start + pd.offsets.MonthBegin(-1) # Round at 1 month before start
    if end is not None:
        end = pd.to_datetime(end) # Savety, redefine as datetime
        res_end = end + pd.offsets.MonthEnd(0) # Round at the end of the last month
    df = df.loc[res_start:res_end, ['Hydro_Res','Other_Res']] # Select information only for good duration
    if start is None: res_start = df.index[0]
    if end is None: res_end = df.index[-1]
    
    
    ################################
    ##### Build the adapted time series with right time step
    #####
    gap = pd.DataFrame(None, columns=df.columns,
                       index = pd.date_range(start=res_start,
                                             end=max(res_end, df.index[-1]), freq=localFreq))

    if localFreq[0]=='Y':
        for dt in df.index:
            localize = (gap.index.year==dt.year)
            gap.loc[localize,:] = df.loc[dt,:].values

    elif localFreq[0]=="M":
        for dt in df.index:
            localize = ((gap.index.year==dt.year)&(gap.index.month==dt.month))
            gap.loc[localize,:] = df.loc[dt,:].values

    else:
        for dt in df.index: # everything from (week, ) day to 15 minutes
            if dt.dayofweek<=4: # week day
                localize = ((gap.index.year==dt.year)&(gap.index.month==dt.month)
                            &(gap.index.dayofweek<=4))
            else:
                localize = ((gap.index.year==dt.year)&(gap.index.month==dt.month)
                            &(gap.index.dayofweek==dt.dayofweek))
            gap.loc[localize,:] = df.loc[dt,:].values
        gap = gap.dropna(axis=0)
        
        if freq in ["W","w"]: # Aggregate into weeks
            gap = gap.fillna(method='ffill').resample(freq).mean()

    return gap.dropna(axis=0)


# +

###########################
# ##########################
# Load raw Entso
# ##########################
# ##########################

# -

def load_rawEntso(mix_data, freq='H'):
    """
    Function that can load an existing production and exchange matrix in a CSV file
    """
    ################################################
    # Labeling of data matrix and import of data
    ################################################
    if type(mix_data)==str: # Import from file
        check_frequency(freq) # Check the frequency
        tPass = {'15min':'15min','30min':'30min',"H":"hour","D":"day",'d':'day','W':"week",
                 "w":"week","MS":"month","M":"month","YS":"year","Y":"year"}
        
        data = pd.read_csv(mix_data+f"ProdExchange_{tPass[freq]}.csv",
                               index_col=0, parse_dates=[0])
            
    elif type(mix_data)==pd.core.frame.DataFrame: # import from the DataFrame passed as argument
        data = mix_data
        
    else: raise KeyError(f"Data type {type(mix_data)} for raw_prodExch is not supported.")

    return data


# +

###########################
# ##########################
# Get default file
# ##########################
# ##########################

# -

def get_default_file(name,level=3):
    """Function to load a default file form directory 'support_file'"""
    ### Default RELATIVE path (indepenently of the file structure)
    path = os.path.abspath(r"{}".format(__file__)).replace("\\","/").split("/")[:-level] # List to main directory of EcoDyn
    path = path + ['support_files',name] # add the default SwissGrid file
    if os.path.isfile(r"{}".format("/".join(path))):
        return r"{}".format("/".join(path)) # Recreate the file address
    elif level<=2:
        return get_default_file(name,level=level-1)
    else:
        raise KeyError(f"Default support file {name} not found.")
