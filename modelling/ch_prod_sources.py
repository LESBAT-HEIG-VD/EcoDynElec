import numpy as np
import pandas as pd


def export_ch_prod_sources(input_file, output_file=None, is_verbose=False):
    if is_verbose: print('Reading data...')
    data = pd.read_csv(input_file, parse_dates=['BeginningOfOperation'])

    if is_verbose: print('Formatting data...')
    data = data.drop(['Address', 'PostCode', 'Municipality', 'MainCategory'], axis=1)
    # Map with dataset's categories
    # written by copilot <3
    subcat_map = {
        'subcat_1': 'Energie hydraulique',
        'subcat_2': 'Photovoltaique',
        'subcat_3': 'Energie eolienne',
        'subcat_4': 'Biomasse',
        'subcat_5': 'Geothermie',
        'subcat_6': 'Energie nucleaire',
        'subcat_7': 'Petrole',
        'subcat_8': 'Gaz naturel',
        'subcat_9': 'Charbon',
        'subcat_10': 'Dechets'
    }
    plantcat_map = {
        'plantcat_1': 'Centrale sur les eaux usees',
        'plantcat_2': 'Centrale de derivation',
        'plantcat_3': 'Centrale de dotation',
        'plantcat_4': 'Centrale au fil de l\'eau',
        'plantcat_5': 'Centrale sur l\'eau potable',
        'plantcat_6': 'Centrale de pompage-turbinage',
        'plantcat_7': 'Centrale a accumulation',
        'plantcat_8': 'Ajoutee',
        'plantcat_9': 'Integree',
        'plantcat_10': 'Isolee',
        'plantcat_11': 'Utilisation de biomasse',
        'plantcat_12': 'Incineration des ordures menageres',
        'plantcat_13': 'Epuration des eaux',
        np.nan: ''
    }
    data['SubCategory'] = data['SubCategory'].map(subcat_map)
    data['PlantCategory'] = data['PlantCategory'].map(plantcat_map, na_action=None)

    # Map with EcoDynElec categories
    mapping_ecodynelec = {
        'Energie hydraulique': 'Hydro_All_CH',
        'Photovoltaique': 'Solar_CH',
        'Energie eolienne': 'Wind_Onshore_CH',
        'Biomasse': 'Biomass_CH',
        'Energie nucleaire': 'Nuclear_CH',
        'Petrole': 'Residual_Other_CH',
        'Gaz naturel': 'Fossil_Gas_CH',
        'Dechets': 'Waste_CH'
    }
    mapping_hydraulic = {
        'Centrale sur les eaux usees': 'Hydro_Run-of-river_and_poundage_CH',
        'Centrale de derivation': 'Hydro_Run-of-river_and_poundage_CH',
        'Centrale de dotation': 'Hydro_Run-of-river_and_poundage_CH',
        'Centrale au fil de l\'eau': 'Hydro_Run-of-river_and_poundage_CH',
        'Centrale sur l\'eau potable': 'Hydro_Run-of-river_and_poundage_CH',
        'Centrale de pompage-turbinage': 'Hydro_Pumped_Storage_CH',
        'Centrale a accumulation': 'Hydro_Water_Reservoir_CH',
        'Non renseigne': 'Hydro_Run-of-river_and_poundage_CH'
    }
    # and separate hydraulic sources
    data['SubCategory'] = data['SubCategory'].map(mapping_ecodynelec)
    hydraulic = data[data['SubCategory'] == 'Hydro_All_CH'].copy()
    data = data.drop(data[data['SubCategory'] == 'Hydro_All_CH'].index, axis=0)

    hydraulic['SubCategory'] = hydraulic['PlantCategory'].map(mapping_hydraulic, na_action=None)
    hydraulic['PlantCategory'] = ''
    grouped = pd.concat([data, hydraulic])
    grouped = grouped.sort_values(['BeginningOfOperation'])
    grouped['CumulativePower'] = grouped.groupby(['SubCategory'])['TotalPower'].cumsum()

    # Export
    if output_file is not None:
        if is_verbose: print('Exporting data...')
        grouped.to_csv(output_file)
    return grouped

def get_prod_capacities_at_date(prod_sources, date):
    prod_sources = prod_sources[prod_sources['BeginningOfOperation'] <= date]
    prod_sources = prod_sources.groupby(['SubCategory'])['CumulativePower'].max()
    return prod_sources


def ch_capacities_to_entsoe_format(prod_sources, start, end):
    dtrange = pd.date_range(start=start, end=end, freq='D')
    #dtrange = dtrange.intersection(prod_sources['BeginningOfOperation'])
    df = pd.DataFrame(index=dtrange, columns=prod_sources['SubCategory'].unique())
    init = get_prod_capacities_at_date(prod_sources, dtrange[0])
    df.loc[dtrange[0]] = init
    for date in dtrange[1:]:
        at_date = prod_sources[prod_sources['BeginningOfOperation'] == date]
        init = init.add(at_date.groupby(['SubCategory'])['TotalPower'].max(), fill_value=0)
        df.loc[date] = init
    df = df.drop(np.nan, axis=1) # drop empty column
    return df
