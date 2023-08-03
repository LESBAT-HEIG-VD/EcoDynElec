"""
Module containing a collection of functions to load side-datasets
that may be required during the execution of `ecodynelec` proceses.
"""

import os
import warnings

import numpy as np
import pandas as pd

################# Local functions
from ecodynelec.checking import check_frequency


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

    Parameters
    ----------
        path_sg: str
            path to the file with Swiss Grid information
        start: str, default None
            starting date, as datetime or str
        end: str, default None
            ending date, as datetime or str
        freq: str, default to 'H'
            frequency to resample the SwissGrid data to

    Returns
    -------
    pandas.DataFrame
        table of SwissGrid information in MWh
    """
    ### Default path
    if path_sg is None:
        path_sg = get_default_file(name='SwissGrid_total.csv')

    ### Date safety
    if start is not None: start = pd.to_datetime(start)
    if end is not None: end = pd.to_datetime(end)

    ### Import SwissGrid data
    sg = pd.read_csv(path_sg, index_col=0, parse_dates=True, dtype="float32")

    sg = sg.drop(columns=["Consommation_CH", "Consommation_Brut_CH"])  # Remove unused columns

    ### Check info availability (/!\ if sg smaller, big problem not filled yet !!!)
    if 'Production_CH' not in sg.columns:
        raise KeyError("Missing information 'Production_CH' in SwissGrid Data.")
    if ((start is None) | (end is None)):
        msg = "  /!\ Some date limits are None. SwissGrid is on period {} - {}. It may not match the Generation and Exchange."
        warnings.warn(msg.format(sg.loc[start:end].index[0], sg.loc[start:end].index[-1]))
    elif ((start < sg.index[0]) | (end > sg.index[-1])):  # print information only
        msg = "  /!\ Resudual computed only during {} - {}. SwissGrid Data not available on the rest of the period."
        warnings.warn(msg.format(sg.loc[start:end].index[0], sg.loc[start:end].index[-1]))

    ### Rename the columns
    sg.columns = ["Production_CH", "Mix_CH_AT", "Mix_AT_CH", "Mix_CH_DE", "Mix_DE_CH",
                  "Mix_CH_FR", "Mix_FR_CH", "Mix_CH_IT", "Mix_IT_CH"]

    ### Select the interesting data, resample to right frequency and convert kWh -> MWh
    return sg.loc[start:end, :].resample(freq).sum() / 1000


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
    ambiguous = pd.Series(np.unique(sg.index, return_counts=True)[1], index=np.unique(sg.index),
                          name='Occurrence').reset_index()
    ambiguous = ambiguous[((ambiguous.loc[:, 'Occurrence'] == 2)
                           & (ambiguous.loc[:, 'index'] == ambiguous.loc[:, 'index'].round("H")))]

    # Create the new date for ambiguous dates
    ambiguous['replace'] = ambiguous.loc[:, 'index'].apply(lambda x: x if x.hour == 2 else x - pd.Timedelta("1H"))

    # Find the right index of first occurrence
    ambiguous.index = pd.Series(np.arange(sg.shape[0]), index=sg.index).loc[ambiguous.loc[:, 'index']].values[::2]

    # Clear SG dates
    sg_cleared = sg.reset_index()
    sg_cleared.loc[ambiguous.index, "Date"] = ambiguous.loc[:, 'replace']
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
    neighbouring = pd.read_csv(path_neighbour, index_col=0)
    useful = list(ctry)  # List of countries considered + neighbours
    for c in ctry:
        useful += list(neighbouring.loc[c].dropna().values)
    useful = list(np.unique(useful))  # List of the useful countries, one time each.
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
        network_loss_path = get_default_file(name='SFOE_data.csv')

    # Get and calculate new power demand for the FU vector
    losses = pd.read_csv(network_loss_path)
    losses['Rate'] = 1 + (losses.loc[:, 'Pertes'] / losses.loc[:, 'Conso_CH'])

    if start is None:
        if end is None:
            output = losses.loc[:, ['annee', 'mois', 'Rate']].rename(columns={'annee': 'year', 'mois': 'month'})
            return output.reset_index(drop=True)
        else:
            end = pd.to_datetime(end)  # Savety, redefine as datetime
            localize = (losses.annee <= end.year)
    else:
        start = pd.to_datetime(start)  # Savety, redefine as datetime
        if end is None:
            localize = (losses.annee >= start.year)
        else:
            end = pd.to_datetime(end)  # Savety, redefine as datetime
            localize = ((losses.annee >= start.year) & (losses.annee <= end.year))
    output = losses.loc[localize, ['annee', 'mois', 'Rate']].rename(columns={'annee': 'year', 'mois': 'month'})
    return output.reset_index(drop=True)


# +

###########################
# ##########################
# Load gap content
# ##########################
# ##########################

# -

def load_gap_content(path_gap, start=None, end=None, freq='H', enr_prod_residual_ch=None):
    """
    Function that defines the relative composition of the swiss residual production. The function is very
    file format specific.
    If enr_prod_residual_ch is not None, it will be subtracted from the "other" residual production before
    computing the relative composition of each category.

    Parameters
    ----------
        path_gap: str
            Path to the file containing residual content information.
            The file must contain absolute values for each category, for each time step (if not, use
            updating.update_residual_share to update the file).
        start: default to None
            starting date, as datetime or str
        end: default to None
            ending date, as datetime or str
        freq: str, default to "H"
            frequency to resample the data to
        enr_prod_residual_ch: default to None
            Delta between the renewable electricity production of EcoDynElec-EnrModel and the
            production given by the ENTSO-E data.
            If not None, the total will be subtracted from the "other" residual category.

    Returns
    -------
    pandas.DataFrame
        table with relative residual production composition for each time step.
    """
    ### Default path
    if path_gap is None:
        path_gap = get_default_file(name="Share_residual.csv")  # Change
        df = pd.read_csv(path_gap, index_col=0, parse_dates=True)  # Load default from software files
    elif not os.path.isfile(path_gap):
        path_gap = get_default_file(name="Share_residual.csv")  # Change
        df = pd.read_csv(path_gap, index_col=0, parse_dates=True)  # Load default from software files
    elif os.path.splitext(path_gap)[1] == '.csv':
        df = pd.read_csv(path_gap, index_col=0, parse_dates=True)  # Load csv file from user
    else:
        # cannot use the function in update, due to a circular import
        interest = {'Centrales au fil de l’eau': "Hydro_Run-of-river_and_poundage_Res",
                    'Centrales à accumulation': "Hydro_Water_Reservoir_Res",
                    'Centrales therm. classiques et renouvelables': "Other_Res"}
        df = pd.read_excel(path_gap, header=59, index_col=0).loc[interest.keys()].rename(index=interest)
        df = df.T
        df.index = pd.to_datetime(df.index, yearfirst=True)  # time data

    # Check if the file contains relative (old format) or absolute values
    if df.iloc[0].sum() < 2:
        raise ValueError(
            "You should update the residual share file with updating.update_residual_share. It must now contain absolute production values (not relatives)")

    ###########################
    ##### Adapt the time resolution of raw data
    #####
    # If year or month -> resample at start ('S') of month/year with average of info
    localFreq = freq  # copy frequency
    if freq[0] in ["M", "Y"]:
        localFreq = freq[0] + "S"  # specify at 'start'
        df = df.resample(localFreq).sum()
    # If in week -> resample with average
    elif freq in ['W', 'w']:
        localFreq = 'd'  # set local freq to day (to later sum in weeks)

    ###############################
    ##### Select information
    #####
    res_start, res_end = None, None
    if start is not None:
        start = pd.to_datetime(start)  # Savety, redefine as datetime
        res_start = start + pd.offsets.MonthBegin(-1)  # Round at 1 month before start
    if end is not None:
        end = pd.to_datetime(end)  # Savety, redefine as datetime
        res_end = end + pd.offsets.MonthEnd(0)  # Round at the end of the last month
    df = df.loc[res_start:res_end, ['Hydro_Run-of-river_and_poundage_Res', 'Hydro_Water_Reservoir_Res',
                                    'Other_Res']]  # Select information only for good duration
    if start is None: res_start = df.index[0]
    if end is None: res_end = df.index[-1]

    ################################
    ##### Build the adapted time series with right time step
    #####
    gap = pd.DataFrame(None, columns=df.columns,
                       index=pd.date_range(start=res_start,
                                           end=max(res_end, df.index[-1]), freq=localFreq))

    def remove_enr_prod_residual(dt):
        values = df.loc[dt, :]
        if enr_prod_residual_ch is not None and dt in enr_prod_residual_ch.index:
            enr = enr_prod_residual_ch.loc[dt, :].sum(axis=0)
            delta = values['Other_Res'] - enr.sum()
            delta = delta.clip(min=0)
        return values.values

    if localFreq[0] == 'Y':
        for dt in df.index:
            localize = (gap.index.year == dt.year)
            gap.loc[localize, :] = remove_enr_prod_residual(dt)
    elif localFreq[0] == "M":
        for dt in df.index:
            localize = ((gap.index.year == dt.year) & (gap.index.month == dt.month))
            gap.loc[localize, :] = remove_enr_prod_residual(dt)
    else:
        for dt in df.index:  # everything from (week, ) day to 15 minutes
            if dt.dayofweek <= 4:  # week day
                localize = ((gap.index.year == dt.year) & (gap.index.month == dt.month)
                            & (gap.index.dayofweek <= 4))
            else:
                localize = ((gap.index.year == dt.year) & (gap.index.month == dt.month)
                            & (gap.index.dayofweek == dt.dayofweek))
            gap.loc[localize, :] = remove_enr_prod_residual(dt)
        gap = gap.dropna(axis=0)
        if freq in ["W", "w"]:  # Aggregate into weeks
            gap = gap.fillna(method='ffill').resample(freq).mean()

    # get the relative shares of each technology from the total gap in kWh
    gap = (gap.divide(gap.sum(axis=1), axis=0))
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
    if type(mix_data) == str:  # Import from file
        check_frequency(freq)  # Check the frequency
        tPass = {'15min': '15min', '30min': '30min', "H": "hour", "D": "day", 'd': 'day', 'W': "week",
                 "w": "week", "MS": "month", "M": "month", "YS": "year", "Y": "year"}

        data = pd.read_csv(mix_data + f"ProdExchange_{tPass[freq]}.csv",
                           index_col=0, parse_dates=True)
    elif type(mix_data) == pd.core.frame.DataFrame:  # import from the DataFrame passed as argument
        data = mix_data
    else:
        raise KeyError(f"Data type {type(mix_data)} for raw_prodExch is not supported.")
    return data


# +

###########################
# ##########################
# Get default file
# ##########################
# ##########################

# -

def get_default_file(name, level=0, max_level=3):
    """Function to return the absolute path of default files. The function uses the location
    of the current auxiliary.py file but assumes no structure in EcoDynElec. It only searches
    the structure upward"""
    ### Limit
    if level >= max_level:
        raise FileNotFoundError(f"Default support file {name} not found.")

    ### Function to find parent dir
    parent = lambda path, n: os.path.dirname(path) if n == 0 else os.path.dirname(parent(path, n - 1))

    current_dir = parent(os.path.abspath(__file__), level)

    ### Check for file in current directory
    search = os.path.join(current_dir, name)
    if os.path.isfile(search):
        return search

    ### Otherwise, search 1 level in sub-directory
    for f in os.listdir(current_dir):
        if os.path.isdir(os.path.join(current_dir, f)):
            search = os.path.join(current_dir, f, name)
            if os.path.isfile(search):
                return search

    ### Otherwise, search recursively above (until limit reached)
    return get_default_file(name, level=level + 1)


# +

###########################
# ##########################
# Load CH Enr Model data
# ##########################
# ##########################

# -

def load_ch_enr_model(ch_enr_model_path, start, end, freq):
    """
    Load the CH energy production data from the given path and returns a dataframe with the same format as the
    processed ENTSO-E production and exchange data.

    Parameters
    ----------
    ch_enr_model_path : str
        Path to the CH energy production data, generated with EcoDynElec-EnrModel
    start: str
        Start date of the data to load
    end: str
        End date of the data to load
    freq: str
        Frequency of the data to return (from H to Y)

    Returns
    -------
    pd.DataFrame
        A dataframe with the same format as the processed ENTSO-E production and exchange data,
        containing the CH energy production data for the given period
    """

    enr_prod_ch = pd.read_csv(ch_enr_model_path, index_col=0, parse_dates=[0]).astype(float)
    # Verify that the dataframe contains the right columns
    assert np.all([c in enr_prod_ch.columns for c in
                   ['Wind', 'Solar', 'Waste', 'Biogas', 'Sewage_gas', 'Biomass_1_crops', 'Biomass_2_waste']])
    # Adapt the dataframe to the right format
    enr_prod_ch = enr_prod_ch.loc[start + pd.Timedelta('1H'):end + pd.Timedelta('1H')] / 1000  # Convert from kWh to MWh
    name_map = {
        'Wind': 'Wind_Onshore_CH',
        'Solar': 'Solar_CH',
        'Waste': 'Waste_CH'
    }
    enr_prod_ch['Biomass_CH'] = enr_prod_ch['Biomass_1_crops'] + enr_prod_ch['Biomass_2_waste'] + enr_prod_ch[
        'Biogas'] + enr_prod_ch['Sewage_gas']
    enr_prod_ch.drop(columns=['Biomass_1_crops', 'Biomass_2_waste', 'Biogas', 'Sewage_gas'], inplace=True)
    enr_prod_ch.rename(columns=name_map, inplace=True)
    enr_prod_ch.index = enr_prod_ch.index - pd.Timedelta('1H')  # Shift the index to the left
    # Resample the dataframe to the right frequency (and sum the production values)
    enr_prod_ch = enr_prod_ch.resample(freq).sum()
    return enr_prod_ch
