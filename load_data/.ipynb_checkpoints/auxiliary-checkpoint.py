# -*- coding: utf-8 -*-
import numpy as np
import pandas as pd
import os

################# Local functions
from checking import check_frequency


# +

###########################
# ##########################
# Load SwissGrid
# ##########################
# ##########################

# -

def load_swissGrid(path_sg, start, end, freq='H'):
    """
    Function to load production and cross-border flows information from Swiss Grid. Data used many times
    along the algorithm.
    Parameter:
        path_sg: path to the file with Swiss Grid information (str)
        start: starting date (datetime or str)
        end: ending date (datetime or str)
        freq: time step (str, default H)
    Return:
        pandas DataFrame with SwissGrid information in MWh and at the good time step.
    """
    ### Default path
    if path_sg is None:
        path_sg = get_default_file(name='SwissGrid_total.csv')
    
    ### Import SwissGrid data
    parser = lambda x: (pd.to_datetime(x, format='%d.%m.%Y %H:%M')
                        - pd.Timedelta("15min")) # starts at 00:00 (not 00:15)
    sg = pd.read_csv(path_sg, sep=";",index_col=0, parse_dates=[0], date_parser=parser)
    sg = sg.drop(columns=["Consommation_CH","Consommation_Brut_CH"]) # Remove unused columns

    ### Check info availability (/!\ if sg smaller, big problem not filled yet !!!)
    if 'Production_CH' not in sg.columns:
        raise KeyError("Missing information 'Production_CH' in SwissGrid Data.")
    if ((start<sg.index[0])|(end>sg.index[-1])): # print information only
        warning = "Resudual computed only during {} - {}. SwissGrid Data not available on the rest of the period."
        print(warning.format(sg.loc[start:end].index[0],sg.loc[start:end].index[-1]))
        
    ### Rename the columns
    sg.columns = ["Production_CH","Mix_CH_AT","Mix_AT_CH","Mix_CH_DE","Mix_DE_CH",
                  "Mix_CH_FR","Mix_FR_CH","Mix_CH_IT","Mix_IT_CH"]

    ### Select the interesting data, resample to right frequency and convert kWh -> MWh
    return sg.loc[start:end,:].resample(freq).sum() / 1000


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
    neighbouring = pd.read_csv(path_neighbour,sep=";",index_col=0)
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

def load_grid_losses(network_loss_path, start, end):
    """
    Function that loads network grid losses and returns a pandas DataFrame with the fraction of
    network loss in the transmitted electricity for each month.
    """
    ### Default path
    if network_loss_path is None:
        network_loss_path = get_default_file(name='Pertes_OFEN.csv')
    
    # Get and calculate new power demand for the FU vector
    losses = pd.read_csv(network_loss_path, sep=";")
    losses['Rate'] = 1 + (losses.loc[:,'Pertes']/losses.loc[:,'Conso_CH'])

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

def load_gap_content(path_gap, start, end, freq='H', header=59):
    """
    Function that defines the relative composition of the swiss residual production. The function is very
    file format specific.
    Parameter:
        path_gap: path to the file containing residual content information (str)
        start: starting date (datetime or str)
        end: ending date (datetime or str)
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
    res_start = start + pd.offsets.MonthBegin(-1) # Round at 1 month before start
    res_end = end + pd.offsets.MonthEnd(0) # Round at the end of the last month
    
    df = df.loc[res_start:res_end, ['Hydro_Res','Other_Res']] # Select information only for good duration
    
    
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
        
        data = pd.read_csv(mix_data+f"ProdExchange_{tPass[freq]}.csv",sep=";",
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

def get_default_file(name):
    """Function to load a default file form directory 'support_file'"""
    ### Default RELATIVE path (indepenently of the file structure)
    path = os.path.abspath(__file__).split("/")[:-2] # List to main directory of EcoDyn
    path = path + ['support_files',name] # add the default SwissGrid file
    return "/".join(path) # Recreate the file address
