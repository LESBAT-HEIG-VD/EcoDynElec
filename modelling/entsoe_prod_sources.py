import os
from time import time

import numpy as np
import pandas as pd

import ecodynelec.preprocessing.downloading as dl
from ecodynelec.parameter import Parameter
from ecodynelec.preprocessing.extracting import create_per_country, get_parameters, load_files, get_origin_unit
from ecodynelec.preprocessing.loading import _infer_paths
from ecodynelec.progress_info import ProgressInfo
from modelling.ch_prod_sources import export_ch_prod_sources, ch_capacities_to_entsoe_format


def download2(config, start, end, path, threshold_minutes=15, threshold_size=.9, is_verbose=False,
              progress_bar: ProgressInfo = None):
    """Downloads data from ENTSO-E servers and save it.

    Parameters
    ----------
        config: ecodynelec.Parameter
            collection of parameters for the execution of ecodynelec.
            The relevant information is the start and end date, as well
            as server information and path information to save raw_generation
            and raw_exchange.
        thershold_minutes: int, default to 15
            time in minutes. Maximum time between last download and
            last remote unpdate to not download the file.
        threshold_size: float, default to 0.9
            minimum ratio of size difference between local and remote file below
            which to download, if the last download is newer than `threshold_minutes`.
        is_verbose: bool, default to False
            to display information during the download

    Returns
    -------
    None
    """
    t0 = time()
    ### Get the start and end dates
    dates = dl._set_time(start, end)

    files_dict = {
        'capacities': {
            'ftp_file': 'InstalledGenerationCapacityAggregated_14.1.A',
            'date_format': 'Y'
        },
        'unavailabilities_gen': {
            'ftp_file': 'UnavailabilityOfGenerationUnits_15.1.A_B',
            'date_format': 'm'
        },
        'unavailabilities_prod': {
            'ftp_file': 'UnavailabilityOfProductionUnits_15.1.C_D',
            'date_format': 'm'
        }
    }
    for k in files_dict.keys():
        if not os.path.isdir(path + k):
            print("Creating directory: " + path + k)
            os.makedirs(path + k)
    years, _ = dates
    file_list = {}
    save_list = {}
    for k, v in files_dict.items():
        if v['date_format'] == 'Y':
            file_list[k] = [f"/TP_export/{v['ftp_file']}/{y}_01_{v['ftp_file']}.csv" for y in years]
            save_list[k] = [f"{path}{k}/{y}_01_{v['ftp_file']}.csv" for y in years]
        else:
            file_list[k] = [f"/TP_export/{v['ftp_file']}/{y}_{m:02d}_{v['ftp_file']}.csv" for y, m in zip(*dates)]
            save_list[k] = [f"{path}{k}/{y}_{m:02d}_{v['ftp_file']}.csv" for y, m in zip(*dates)]
    # file_list = {k: ([f"/TP_export/{v['ftp_file']}/{y}_01_{v['ftp_file']}.csv" for y in years] if v['date_format'] == 'Y' else [f"/TP_export/{v['ftp_file']}/{y}_{m}_{v['ftp_file']}.csv" for y, m in zip(dates)]) for k, v in files_dict.items()}
    # save_list = {k: ([f"{path}{k}/{y}_01_{v['ftp_file']}.csv" for y in years] if v['date_format'] == 'Y' else [f"{path}{k}/{y}_{m}_{v['ftp_file']}.csv" for y, m in zip(dates)]) for k, v in files_dict.items()}

    ### Clear directories
    if config.server.removeUnused:
        for k in files_dict.keys():
            dl._remove_olds(path + k, save_list[k])  # Remove unused folder

    ### Download files
    dl._reach_server(config.server, files=file_list, savepaths=save_list, is_verbose=is_verbose,
                     threshold_minutes=threshold_minutes, threshold_size=threshold_size, progress_bar=progress_bar)

    ### EOF
    if is_verbose: print(f"\tDownload from server: {time() - t0:.2f} sec" + " " * 40)
    return


def create_unavailability(path_dir: dict, case: str, start, end, ctry: list,
                          ignore_types=['Wind Offshore ', 'Wind Onshore ', 'Solar '], is_verbose=False,
                          progress_bar: ProgressInfo = None):
    # Obtain parameter set for the specific case
    destination, origin, data, area = get_parameters(case)

    # Import content of raw files
    df = load_files(path_dir, start, end, destination, origin, data, area, is_verbose=is_verbose,
                    progress_bar=progress_bar)

    # Get auxiliary information
    prod_units = get_origin_unit(df, origin)  # list of prod units or origin countries
    time_line = pd.date_range(start=start, end=end, freq='15min')  # time line of the data

    # Rename columns (DE, IT...)
    df.loc[:, destination] = df.loc[:, destination].map(lambda c: c.split('_')[0].split('-')[0])

    # Format and save files for every country
    Data = {}  # Data storage object
    t0 = time()
    for i, c in enumerate(ctry):  # for all countries
        if is_verbose: print(f"Extracting {case} for {c} ({i + 1}/{len(ctry)})...", end="\r")
        if progress_bar: progress_bar.set_sub_label(f"Extracting {case} for {c} ({i + 1}/{len(ctry)})...")
        # Get data from the country and sort by date
        country_data = df[df.loc[:, destination] == c].drop_duplicates()

        # print('Removing duplicate outages...')
        country_data = country_data.sort_values([data['id'], data['start']])
        new_df = pd.DataFrame(columns=country_data.columns)
        # group by power resource (plant)
        j = 0
        grp = country_data.groupby(data['id'])
        for res_id, power_res_df in grp:
            # take the latest version of each outage event (identified by their mrid)
            if progress_bar: progress_bar.set_sub_label(
                f"{c} ({i + 1}/{len(ctry)}) - unit {j}/{len(grp)} - {res_id} - get evt")
            if power_res_df.iloc[0][origin] in ignore_types:
                continue
            maxs = power_res_df.groupby(data['mrid'])[data['version']].idxmax()
            if progress_bar: progress_bar.set_sub_label(
                f"{c} ({i + 1}/{len(ctry)}) - unit {j}/{len(grp)} - {res_id} - loc {len(maxs)} evt")
            lasts = power_res_df.loc[maxs]
            lasts = lasts.drop_duplicates(subset=[data['start'], data['end']])
            ln = len(lasts)
            if ln == 1:
                new_df = pd.concat([new_df, lasts.copy()], ignore_index=True)
                continue
            if is_verbose and ln > 200: print('Removing overlapping outages... ', ln, 'events on unit', res_id, '(',
                                              power_res_df.iloc[0][origin], ')', end='\r')
            dt_ranges = [pd.date_range(start, end, freq='H') for start, end in
                         zip(lasts[data['start']], lasts[data['end']])]

            # remove overlapping outages (some outages are reported twice as,
            # apparently, one is sometimes cancelled but not reported in entsoe data)
            if progress_bar: progress_bar.set_sub_label(
                f"{c} ({i + 1}/{len(ctry)}) - unit {j}/{len(grp)} - {res_id} ({power_res_df.iloc[0][origin]}) - iter {len(dt_ranges)} evt")
            for k in range(len(dt_ranges)):
                cur = dt_ranges[k]
                if np.all([cur.intersection(x).empty for x in dt_ranges[k + 1:]]):
                    # doesn't overlap with any other outage period placed after in the list
                    new_df = pd.concat([new_df, lasts.iloc[k].to_frame().T], ignore_index=True)
            j += 1

        del country_data  # free memory space

        # print('Formatting data...')
        new_df['Unavailable'] = new_df[data['nominal']] - new_df[data['available']]
        Data[c] = new_df.groupby([data['start'], data['end'], data['id']]).agg(
            {'Unavailable': 'sum', origin: 'first', data['type']: 'first'})

        # We want to have a detailed view of the unavailability of each unit (separated planned and forced outages)
        prod_units_2 = np.concatenate([[prod_unit + 'Planned' for prod_unit in prod_units], [prod_unit + 'Forced' for prod_unit in prod_units]])
        country_detailed = pd.DataFrame(None, columns=prod_units_2, index=time_line,
                                        dtype='float32').resample('15min').asfreq()  # init. with NaNs
        for st, end, id in Data[c].index:
            dtr = pd.date_range(st.round('15min'), end.round('15min'), freq='15min')
            dtr = dtr.intersection(time_line)
            entry = Data[c].loc[(st, end, id)]
            prod_unit = entry[origin] + entry[data['type']]
            country_detailed.loc[dtr, prod_unit] = country_detailed.loc[dtr, prod_unit].add(
                entry['Unavailable'], fill_value=0)
        Data[c] = country_detailed.copy()  # Store information in variables (with non-missing NaNs)

        del country_detailed  # free memory space
        del new_df  # free memory space

    if progress_bar:
        progress_bar.progress()
        progress_bar.reset_sub_label()
    if is_verbose: print(f"Extraction raw {case}: {time() - t0:.2f} sec.             ")
    return Data


def export_entsoe_capacities(config: Parameter, padded_start, padded_end, path, case, is_verbose=False,
                             progress_bar: ProgressInfo = None):
    """
    Export the capacities/outages of the power plants in the given countries in the given time range, from the entsoe data.

    Parameters
    ----------
    config: Parameter
        Configuration of the start/end dates, frequency and target countries
    padded_start: str
        For outages, we should use data from before the start date of the analysis, to include outages that started before
        (and were added to the entsoe database before).
    padded_end: str
        For outages, we should use data from after the end date of the analysis, to include outages that ended after
        (and were added to the entsoe database after).
    path: str
        Path to the entsoe data
    case: str
        'capacities', 'unvavailabilities_gen' or 'unvavailabilities_prod'
    is_verbose: bool
        To print information about the extraction
    progress_bar: ProgressInfo
        To display a progress bar

    Returns
    -------
        A dictionary with the data of each country (in dataframes)
    """
    path2, savegen = _infer_paths(None, path, case=case)
    if case == 'capacities':
        oof = create_per_country(path_dir=path2, case=case, start=config.start, end=config.end,
                                 ctry=config.ctry,
                                 savedir=savegen,
                                 savedir_resolution=config.path.savedir, is_verbose=is_verbose,
                                 n_hours=24 * 365, days_around=7, limit=.99, correct_data=False,
                                 progress_bar=progress_bar)
        for c in config.ctry:
            oof[c].loc[config.end] = oof[c].loc[oof[c].index[-1]]
        # Interpolate the data to get a weekly resolution (from a yearly one)
        oof = {c: oof[c].resample(config.freq).mean() for c in oof.keys()}
        linear_interp = ['Biomass', 'Marine', 'Other', 'Solar', 'Waste', 'Wind Offshore', 'Wind Onshore']
        cc = oof.copy()
        for c in config.ctry:
            for col in cc[c].columns:
                cc[c][col] = cc[c][col].interpolate(method=('linear' if col in linear_interp else 'pad'),
                                                    limit_direction='forward')
            # Resample to the desired frequency (to match the frequency of outages data)
            #cc[c] = cc[c].resample(config.freq).mean()
            cc[c] = cc[c].fillna(0)
    else:  # unavailability
        oof = create_unavailability(path_dir=path2, case=case, start=padded_start, end=padded_end,
                                    ctry=config.ctry,
                                    is_verbose=is_verbose, progress_bar=progress_bar)
        cc = {c: oof[c].resample(config.freq).mean().fillna(0) for c in oof.keys()}
        # cut on the period of interest
        cc = {c: cc[c].loc[config.start:config.end] for c in cc.keys()}

    Gen = cc.copy()
    for c in config.ctry:  # Preprocess all files / data per country
        # Extract the generation data file
        # if path == path_prep:  # Load preprocessed files
        #   Gen[c] = pd.read_csv(os.path.join(path, files[c]), index_col=0)  # Extraction of preprocessed files

        # Check and modify labels if needed
        Gen[c].columns = Gen[
                             c].columns.str.rstrip() + " "  # (first remove if any, then) set additional ' ' at the end

        # Set indexes to time data
        Gen[c].index = pd.to_datetime(Gen[c].index, yearfirst=True)  # Convert index into datetime

        # Only select the required piece of information
        Gen[c] = Gen[c].loc[config.start:config.end]

        source = list(Gen[c].columns)  # production plants types
        if "Other " in source:  # Expected this label for "Other fossil" from ENTSO-E data
            source[source.index("Other ")] = "Other fossil "  # rename one specific column

        Gen[c].columns = [s.replace(" ", "_") + c for s in source]  # rename columns

    return Gen


def export_entsoe_real_prod_capacities(config, path, padding_prev='365d', padding_after='30d', ch_data_file=None,
                                       is_verbose=False,
                                       progress_bar: ProgressInfo = None):
    """
    Download and extract the ENTSO-E data for the real production and capacities.

    Padding is used to consider the outages that may have started before the period of interest
    (and are therefore declared in previous entsoe files)

    Parameters
    ----------
    config
    path
    padding_prev
    padding_after
    ch_data_file
    is_verbose
    progress_bar

    Returns
    -------

    """
    if progress_bar:
        progress_bar.set_max_value(9 if ch_data_file else 8)
        progress_bar.progress('Download from ENTSO-E...', 0)

    ### Verify the configuration
    if isinstance(config, str):
        if any([config.endswith(k) for k in ('.xlsx', '.xls', '.ods')]):
            config = Parameter(excel=config)
        else:
            raise NotImplementedError(f"File extension for {config} is not supported.")

    padded_start = config.start - pd.Timedelta(padding_prev)
    padded_end = config.end + pd.Timedelta(padding_after)

    if config.server.useServer:
        if is_verbose: print('Downloading required ENTSO-E data...')
        download2(config=config, start=padded_start, end=padded_end, path=path, is_verbose=is_verbose,
                  progress_bar=progress_bar)

    if is_verbose: print('Extracting nominal capacities...')
    if progress_bar: progress_bar.progress('Extract nominal capacities...')
    gen_capacities = export_entsoe_capacities(config, None, None, path + 'capacities/', case='capacities',
                                              progress_bar=progress_bar)

    if ch_data_file is not None:
        if is_verbose: print('Extracting CH capacities...')
        if progress_bar:
            progress_bar.progress('Extract CH capacities...')
            progress_bar.set_sub_label('Reading file...')
        ch_data = export_ch_prod_sources(input_file=ch_data_file, output_file=None, is_verbose=is_verbose)
        if progress_bar: progress_bar.set_sub_label('Formatting data...')
        gen_capacities['CH'] = ch_capacities_to_entsoe_format(ch_data, config.start, config.end) / 1000
    else:
        print('Warning: No CH capacities file provided. CH capacities will be incomplete.')

    if is_verbose: print('Extracting unavailability...')
    if progress_bar: progress_bar.progress('Extract generation unavailability...')
    unavailable_gen = export_entsoe_capacities(config, padded_start, padded_end, path + 'unavailabilities_gen/',
                                               case='unavailabilities_gen',
                                               is_verbose=is_verbose, progress_bar=progress_bar)
    if progress_bar: progress_bar.progress('Extract production unavailability...')
    unavailable_prod = export_entsoe_capacities(config, padded_start, padded_end, path + 'unavailabilities_prod/',
                                                case='unavailabilities_prod',
                                                is_verbose=is_verbose, progress_bar=progress_bar)
    broken_detailed = {c: unavailable_gen[c].add(unavailable_prod[c], fill_value=0) for c in gen_capacities}
    broken_entsoe = {}
    for c in gen_capacities:
        broken_entsoe[c] = pd.DataFrame(index=gen_capacities[c].index, columns=gen_capacities[c].columns)
        keys = []
        for prod_type in gen_capacities[c].columns:
            prod_type = prod_type[:-3] # remove country suffix
            planned = prod_type + '_Planned_' + c
            forced = prod_type + '_Forced_' + c
            if planned not in broken_detailed[c].columns or forced not in broken_detailed[c].columns:
                continue
            broken_entsoe[c][prod_type+'_'+c] = broken_detailed[c][planned] + broken_detailed[c][forced]
            keys.append(planned)
            keys.append(forced)
       #broken_entsoe[c].drop(columns=keys, inplace=True)

    if is_verbose: print('Sum real capacities...')
    if progress_bar: progress_bar.progress('Sum real capacities...')

    print('-- NOTE: Columns in generation but not in unavailable capacities --')
    not_in_capacity = {c: gen_capacities[c].columns.difference(broken_entsoe[c].columns) for c in gen_capacities}
    print(not_in_capacity)

    real_capacity = {c: gen_capacities[c].add(-broken_entsoe[c], fill_value=0) for c in gen_capacities}

    if is_verbose: print('Done!')
    if progress_bar: progress_bar.progress("Done!")
    return gen_capacities, broken_entsoe, broken_detailed, real_capacity


def save_to_csvs(dataset, path, name):
    for c in dataset:
        dataset[c].to_csv(f'{path}/{name}_{c}.csv')


def read_from_csvs(ctry, path, name):
    dataset = {}
    for c in ctry:
        dataset[c] = pd.read_csv(f'{path}/{name}_{c}.csv', index_col=0, parse_dates=True)
    return dataset