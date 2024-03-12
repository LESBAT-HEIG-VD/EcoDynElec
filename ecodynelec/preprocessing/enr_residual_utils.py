"""
Helper functions to load and preprocess the renewable electricity data from Pronovo and EnergyCharts.
"""

import os
from datetime import datetime

import pandas as pd

pronovo_types_map = {
    '*': {
        'Wind': 'Wind (kWh)',
        'Solar': 'Photovoltaik (kWh)',
        'Biogas': 'Biogas (kWh)',
        'Biomass_1_crops': 'Energiepflanze (kWh)',
        'Biomass_2_waste': 'Forst- und Landwirtschaftliche Abfälle (kWh)',
        'Waste_1': 'Kehrichtverbrennung (erneuerbar) (kWh)',
        'Sewage_gas': 'Klärgas (kWh)',
    },
    '5': {
        'Wind': 'Wind',
        'Solar': 'Photovoltaic',
        'Biomass_all': 'Biomasse'
    },
    '2': {
        'Wind': '-A.Windturbine [kWh]',
        'Solar': '-A.Photovoltaik [kWh]',
        'Biogas': '-A.Biogas [kWh]',
        'Biomass_1_crops': '-A.Energiepflanze [kWh]',
        'Biomass_2_waste': '-A.Forst- und Landwirtschaftliche Abfälle [kWh]',
        'Waste_1': '-A.Kehrichtverbrennung [kWh]',
        'Waste_2.50': '-A.Kehrichtverbrennung (erneuerbar).50 [kWh]',
        'Waste_3.100': '-A.Kehrichtverbrennung (erneuerbar).100 [kWh]',
        'Waste_4_no_enr': '-A.Kehrichtverbrennung (nicht erneuerbar) [kWh]',
        'Sewage_gas': '-A.Klärgas [kWh]',
        # 'Gas_1': '-A.Erdgas Dampfturbine [kWh]',
        # 'Gas_2': '-A.Gas- und Dampfkombikraftwerk [kWh]',
        # 'Gas_3': '-A.Gasturbine [kWh]',
        # 'Unknown': '-A.Leichtwasserreaktor [kWh]', #light water  -> matches nuclear production
        # 'Combustion_engine': '-A.Verbrennungsmotor [kWh]'
    }
}
"""
Mapping linking pronovo column names to the actual types of plants used in this project.
There is a different mapping for each pronovo file format (see load_pronovo_file).
"""

ec_types_to_types = {
    'Biogaz': 'Biogas',
    'Biomasse': 'Biomass_all',
    'Cultures énergétiques': 'Biomass_1_crops',
    'Déchets forestiers et agricoles': 'Biomass_2_waste',
    'Incinération': 'Waste_1',
    "Biogaz de station d'épuration": 'Sewage_gas',
    "Gaz d'égout": 'Sewage_gas'
}
"""
Mapping linking energy charts column names to the actual types of plants used in this project.
"""

data_mappings = {
    'Solar': [
        {
            'start': '2020-01-01',
            'end': 'last',
            'source': 'Pronovo',
            'series': 'Solar'
        }
    ],
    'Wind': [
        {
            'start': '2020-01-01',
            'end': 'last',
            'source': 'Pronovo',
            'series': 'Wind'
        }
    ],
    'Waste': [
        {
            'start': '2020-05-01',
            'end': '2022-09-30',
            'source': 'Pronovo',
            'series': 'Waste_1'
        },
        {
            'start': '2022-10-01',
            'end': '2022-11-30',
            'from_start': '2021-10-01',
            'from_end': '2021-11-30',
            'source': 'EC',
            'series': 'Waste_1'
        },
        {
            'start': '2022-12-01',
            'end': '2022-12-31',
            'source': 'Pronovo',
            'series': 'Waste_2.50'
        },
        {
            'start': '2023-01-01',
            'end': 'last',
            'source': 'Pronovo',
            'series': 'Waste_1'
        }
    ],
    'Biogas': [
        {
            'start': '2020-05-01',
            'end': 'last',
            'source': 'Pronovo',
            'series': 'Biogas'
        }
    ],
    'Sewage_gas': [
        {
            'start': '2020-05-01',
            'end': 'last',
            'source': 'Pronovo',
            'series': 'Sewage_gas'
        }
    ],
    'Biomass_1_crops': [
        {
            'start': '2020-05-01',
            'end': '2022-12-31',
            'source': 'Pronovo',
            'series': 'Biomass_1_crops'
        }
    ],
    'Biomass_2_waste': [
        {
            'start': '2020-05-01',
            'end': '2021-12-31',
            'source': 'Pronovo',
            'series': 'Biomass_2_waste'
        },
        {
            'start': '2022-01-01',
            'end': '2022-12-31',
            'from_start': '2021-01-01',
            'from_end': '2021-12-31',
            'source': 'Pronovo',
            'series': 'Biomass_2_waste'
        },
        {
            'start': '2023-01-01',
            'end': 'last',
            'source': 'Pronovo',
            'series': 'Biomass_2_waste'
        }
    ]
}
"""
**The reorganization rules are only valid for the 2020-2022 period.**
    
A dict giving the mapping between the columns of the final data (result) and the source data from Pronovo and EnergyCharts. 
Used by the reorganize_enr_data method. 

Should follow the structure :

.. code-block:: python

    'Category1': [
        {
            'start': 'start date', # start date in the result (and in source data if from_start isn't set)
            'end': 'end date', # end date in the result (and in source data if from_end isn't set) (use 'last' to get the real end of the source data)
            'from_start': '2021-01-01', # optional, start date in the source data (allows to copy data from one date to another)
            'from_end': '2021-12-31', # optional, end data in the source data
            'source': 'Pronovo' or 'EC', # source of the data
            'series': 'Series_Name_In_Source_Data' # name of the column to take in the source data
        },
        ...
    ],
    ...
"""


def get_enr_data_from_pronovo_ec(path_dir, verbose=False):
    """
    Reads the pronovo and energy charts data from the given directory, and returns a dataframe containing the
    reorganized data. The reorganized data is the best estimation of the real renewable electricity productions (solar, wind,
    waste...), from what is available.

    **The reorganization rules are only valid for the 2020-2022 period.**

    Parameters
    ----------
    path_dir : str
        The path of the directory containing the pronovo and energy charts data.

        The directory should contain two subdirectories:

        - pronovo_data: containing the pronovo data (a 'prod_year' directory for each input)

        - ec_data: containing the energy charts data (annual files)

        See the documentation below for more details.
    verbose : bool, optional
        Whether to print debug information. The default is False.

    Returns
    -------
    mapped_data : pd.DataFrame
        A dataframe containing the reorganized data, indexed by date.
    """
    pronovo_data = read_enr_data_from_pronovo(path_dir, verbose=verbose)
    ec_data = read_enr_data_from_energy_charts(path_dir, verbose=verbose)
    mapped_data = reorganize_enr_data(pronovo_data, ec_data)
    return mapped_data


def read_enr_data_from_pronovo(path_dir, verbose=False):
    """
    Reads all the pronovo data from the given directory, and returns a dataframe containing the data.

    Parameters
    ----------
    path_dir : str
        The path of the directory containing the pronovo data.
        The directory should contain a subdirectory for each year, named 'prod_year' (e.g. 'prod_2020').
        Each subdirectory should contain the pronovo data files of this year (.csv files).
        See the documentation below for more details.
    verbose : bool, optional
        Whether to print debug information. The default is False.

    Returns
    -------
    pronovo_data : pd.DataFrame
        A dataframe containing the pronovo data, indexed by date.
    """
    pronovo_dir = os.path.join(path_dir, 'pronovo_data')
    if not os.path.isdir(pronovo_dir):
        raise FileNotFoundError(
            f"Directory {pronovo_dir} doesn't exist. Please create it and add actual pronovo data directories (follow the procedure explain in the documentation).")
    # Read pronovo data
    years = []
    for file in os.listdir(pronovo_dir):
        if file.startswith('prod_') and os.path.isdir(os.path.join(pronovo_dir, file)):
            years.append(file)
    if verbose:
        print(f'Reading pronovo directories: {years}')
    types = list(pronovo_types_map['2'].keys())
    types.append('Biomass_all')
    pronovo_data = load_all_pronovo_files(pronovo_dir + '/', years, types=types, verbose=verbose)
    return pronovo_data


def read_enr_data_from_energy_charts(path_dir, verbose=False):
    """
    Reads all the energy charts data from the given directory, and returns a dataframe containing the data.

    Parameters
    ----------
    path_dir : str
        The path of the directory containing the energy charts data.
        The directory should contain a subdirectory named 'ec_data'.
        The 'ec_data' directory should contain the yearly energy charts data files (.csv files).
        See the documentation below for more details.
    verbose : bool, optional
        Whether to print debug information. The default is False.

    Returns
    -------
    df_ec_data : pd.DataFrame
        A dataframe containing the energy charts data, indexed by date.
    """
    ec_dir = os.path.join(path_dir, 'ec_data')
    if not os.path.isdir(ec_dir):
        raise FileNotFoundError(
            f"Directory {ec_dir} doesn't exist. Please create it and add actual energy charts data files (follow the procedure explain in the documentation).")
    # Read EnergyCharts data
    ec_data = []
    for f in os.listdir(ec_dir):
        if f.endswith('.csv'):
            if verbose: print('Reading ' + f)
            data = pd.read_csv(ec_dir + '/' + f, index_col=0)
            data = data.drop(index=data.index[0], columns=[col for col in data.columns if col.startswith('Unnamed')])
            data = data.rename(columns=ec_types_to_types)
            ec_data.append(data)
    df_ec_data = pd.concat(ec_data, axis=0).fillna(0).astype(float)
    # create DatetimeIndex from D.M.Y format to match pronovo data
    df_ec_data.index = pd.to_datetime(df_ec_data.index, format='%d.%m.%Y')
    return df_ec_data


def reorganize_enr_data(pronovo_data: pd.DataFrame, ec_data: pd.DataFrame) -> pd.DataFrame:
    """
    | Reorganizes the pronovo and energy charts data to match the final data format.
    | The reorganized data is the best estimation of the real renewable electricity productions, from what is available.
    | **The reorganization rules are only valid for the 2020-2022 period.**

    Parameters
    ----------
    pronovo_data : pd.DataFrame
        The pronovo data, indexed by date.
    ec_data : pd.DataFrame
        The energy charts data, indexed by date.

    Returns
    -------
    mapped_data : pd.DataFrame
        A dataframe containing the reorganized data, indexed by date.
    """
    mapped_data = pd.DataFrame(index=pronovo_data.index, columns=data_mappings.keys())
    real_end = ec_data.index[-1]
    if pronovo_data.index[-1] < real_end:
        real_end = pronovo_data.index[-1]
    real_end = str(real_end.date())
    for col in data_mappings.keys():
        maps = data_mappings[col]
        for mapping in maps:
            from_ec = mapping['source'] == 'EC'
            src_df = ec_data.copy() if from_ec else pronovo_data
            if mapping['end'] == 'last':
                mapping['end'] = real_end  # Use the real end of the data
            start = datetime.strptime(mapping['start'], '%Y-%m-%d')
            end = datetime.strptime(mapping['end'], '%Y-%m-%d') + pd.Timedelta(hours=23)
            if 'from_start' in mapping:  # copy data [from_start to from_end] at [start to end]
                from_start = datetime.strptime(mapping['from_start'], '%Y-%m-%d')
                from_end = datetime.strptime(mapping['from_end'], '%Y-%m-%d') + pd.Timedelta(hours=23)
                if from_ec:
                    # Scale past pronovo hours to actual energy charts daily production
                    prod_ec = src_df.loc[start:end, mapping['series']]
                    prod_pronovo = pronovo_data.loc[from_start:from_end, mapping['series']].copy()
                    prod_pronovo.index = mapped_data.loc[start:end, col].index
                    daily_y = prod_pronovo.resample('D').sum()
                    daily_y.index = prod_ec.index
                    prod_ec = prod_ec * 1000000  # Convert to kWh
                    factors = prod_ec / daily_y
                    # Adjust the index to include the hours of the last day
                    adjusted_dates = pd.date_range(start=factors.index[0],
                                                   end=factors.index[-1] + pd.Timedelta(hours=23),
                                                   freq='H')
                    resampled_dates = factors.reindex(adjusted_dates, method='ffill')
                    prod_pronovo = prod_pronovo.multiply(resampled_dates)
                else:
                    # Directly copy from one date to another date, from Pronovo data
                    prod_pronovo = src_df.loc[from_start:from_end, mapping['series']].copy()
                    prod_pronovo.index = mapped_data.loc[start:end, col].index
                mapped_data.loc[start:end, col] = prod_pronovo
            else:
                if mapping['source'] == 'EC':
                    # Convert daily EnergyCharts data to hourly data
                    src_df = src_df * 1000000  # Convert to kWh
                    src_df = src_df.resample(
                        'H').ffill() / 24  # Convert to hourly data (with a uniform repartition over the day in first approximation)
                    print('Warning: uniform daily distribution of EC data was used for column', col)
                # simple copy
                mapped_data.loc[start:end, col] = src_df.loc[start:end, mapping['series']]
    return mapped_data


def load_all_pronovo_files(root_dir: str, dirs: [str], types: [str], verbose: bool = False) -> pd.DataFrame:
    """
    Loads all pronovo files in the given directories, applying daily scaling with energy charts ecd_enr_model (the hourly variation
    comes from the pronovo ecd_enr_model, and the daily total from energy charts ecd_enr_model, if available).
    The scaling is done with csv files starting by "EC". All other csv files are considered as pronovo files.

    :param root_dir: The root directory containing the pronovo 'prod_year' directories
    :param dirs: The directories to load the ecd_enr_model from
    :param types:  The types of plants to extract (in ['Wind', 'Solar'])
    :param verbose:  Whether to print debug information
    :return:  A dataframe containing the pronovo ecd_enr_model for all 'types', indexed by date
    """

    final_data = []
    for dir in dirs:
        Ys = []
        scalers = []
        for f in os.listdir(f'{root_dir}{dir}'):
            if f.endswith('.csv'):
                if f.startswith('EC'):
                    if any([tpe in f for tpe in types]):
                        if verbose: print('Found scaler', f)
                        scalers.append(f)
                    continue
                f_y = load_pronovo_file(f'{root_dir}{dir}/{f}', types, verbose=verbose)
                Ys.append(f_y)
        pronovo_data = pd.concat(Ys).sort_index()
        for i in range(len(scalers)):
            scaler = scalers[i]
            col = [tpe for tpe in types if tpe in scaler][0]
            if verbose: print('Applying scaler', scaler)
            ec_data = pd.read_csv(f'{root_dir}{dir}/{scaler}', skiprows=1, index_col=0)['Énergie (GWh)']
            daily_y = pronovo_data[col].resample('D').sum()
            ec_data.index = daily_y.index
            ec_data = ec_data * 1000000
            factors = ec_data / daily_y
            # Ajuster l'index pour inclure l'heure 23:00 du dernier jour
            adjusted_dates = pd.date_range(start=factors.index[0], end=factors.index[-1] + pd.Timedelta(hours=23),
                                           freq='H')
            # Réindexer la série resamplée avec l'index ajusté
            resampled_dates = factors.reindex(adjusted_dates, method='ffill')
            pronovo_data[col] = pronovo_data[col].multiply(resampled_dates)
        final_data.append(pronovo_data)
    if verbose: print('Done!                   ')
    return pd.concat(final_data).sort_index()


def load_pronovo_file(file: str, types: [str], verbose: bool = False) -> pd.DataFrame:
    """
    Load pronovo ecd_enr_model from a csv file.
    Supports years from 2020 to 2022 (historically the format of the files changes every semester).

    :param file: the path of the file to load
    :param types:  The types of plants to extract (in ['Wind', 'Solar'])
    :param verbose:  Whether to print debug information
    :return:  A dataframe containing the pronovo ecd_enr_model for all 'types', indexed by date
    """

    if file.endswith('2020.csv'):
        format = 5 if int(file[-11:-9]) < 5 else 6
    elif file.endswith('2021.csv'):
        format = 3 if int(file[-11:-9]) < 8 else 4
    elif file.endswith('2022.csv'):
        format = 1
    else:
        format = 2
    if verbose: print(f'Load fmt {format} {file}', end='\n')
    if format == 5:
        pronovo_data = pd.read_csv(f'{file}', index_col=0, skiprows=2,
                                   encoding='windows-1252', sep=';')
        pronovo_types = pronovo_types_map['5']
    elif format == 6:
        pronovo_data = pd.read_csv(f'{file}', index_col=0, skiprows=10,
                                   encoding='windows-1252', sep=';')
        pronovo_types = pronovo_types_map['*']
    elif format == 3:
        pronovo_data = pd.read_csv(f'{file}', index_col=0, skiprows=16,
                                   encoding='windows-1252', sep=';')
        pronovo_types = pronovo_types_map['*']
    elif format == 4:
        pronovo_data = pd.read_csv(f'{file}', index_col=0, skiprows=18,
                                   encoding='windows-1252', sep=';')
        pronovo_types = pronovo_types_map['*']
    elif format == 1:
        pronovo_data = pd.read_csv(f'{file}', index_col=0, skiprows=17,
                                   encoding='windows-1252', sep=';')
        pronovo_types = pronovo_types_map['*']
    elif format == 2 or format == 7:
        pronovo_data = pd.read_csv(f'{file}', index_col=1, skiprows=1,
                                   encoding='windows-1252', sep=';')
        pronovo_types = pronovo_types_map[str(format)]
    else:
        raise Exception('Unknown format')
    pronovo_data.index = pd.to_datetime(pronovo_data.index, format='%d.%m.%Y %H:%M')
    pronovo_types_a = [pronovo_types[tpe] for tpe in types if
                       tpe in pronovo_types and pronovo_types[tpe] in pronovo_data.columns]
    pronovo_data = pronovo_data[pronovo_types_a]
    pronovo_types_inv = {v: k for k, v in pronovo_types.items()}
    for i in range(len(types)):
        pronovo_data.rename(columns=pronovo_types_inv, inplace=True)
    pronovo_data = pronovo_data.applymap(
        lambda x: float(x) if type(x) != str else float(x.replace('\'', '').replace('’', '')))
    pronovo_data = pronovo_data.resample('H').sum()
    pronovo_data = pronovo_data.iloc[:-1]  # last value is first hour if the next month
    return pronovo_data
