"""
Helper methods for the swiss_mix_analysis notebook.
"""
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import seaborn as seaborn
from matplotlib import pyplot as plt

from ecodynelec.parameter import Parameter

from ecodynelec.pipelines import get_prod_mix_impacts
from ecodynelec.progress_info import ProgressInfo


def generate_data(config, years: list[str], savedir: str = './mix_analysis/results/', show_progress=True,
                  is_verbose: bool = False):
    """
    Generates the data required for the analysis. May take a while to execute.
    Saves the results in {savedir}/{year}/ for each year. They can then be loaded with load_data.
    Parameters
    ----------
    config: See ecodynelec.pipelines.get_prod_mix_impacts doc
    years: list of str
        List of the years to compute
        Overrides config.start and config.end
    savedir: str
        Directory where to save the results (a sub-directory will be created for each year)
        Overrides config.path.savedir
    show_progress: bool, optional
        to display progress bars, defaults to True
    is_verbose: bool, optional
        to display information, defaults to False

    Returns
    -------
    See ecodynelec.pipelines.get_prod_mix_impacts for explanations
    flows_dict: dict of dict of pandas.DataFrame
        Contains for each year a dict of the raw productions/imports/exports for each target country
    mixs: dict of dict of pandas.DataFrame
        Contains for each year a dict of the electric mix shares for each target country
    impacts: dict of dict of pandas.DataFrame
        Contains for each year a dict of the climate change (gwp) impacts for each target country
    """
    flows_dict = {}  # Productions/imports/exports in kwh per year
    prods = {}
    mixs = {}  # Energetic mixes per year
    prod_impacts = {}
    impacts = {}  # Climate change impacts per year
    if show_progress:
        progress_info_year = ProgressInfo('Compute ' + years[0] + '...', len(years) + 1, width='90%')
        progress_info_computation = ProgressInfo('', 11, color='lightgreen', width='90%')
    else:
        progress_info_computation = None
    for year in years:
        if is_verbose: print('Compute ', year)
        if show_progress:
            progress_info_year.progress('Compute ' + year + '...', 0)
        config.start = year + '-01-01 00:00'
        config.end = year + '-12-31 23:59'
        config.path.savedir = savedir + year + "/"
        raw, prod, mix, prodimp, imp = get_prod_mix_impacts(config=config, is_verbose=is_verbose,
                                             progress_bar=progress_info_computation)
        if show_progress:
            progress_info_year.progress()
        flows_dict[year] = raw
        prods[year] = prod
        mixs[year] = mix
        if isinstance(prodimp, dict):  # multi target
            prod_impacts[year] = {k: prodimp[k]['Climate Change'] for k in prodimp.keys()}
        else:  # single target
            prod_impacts[year] = prodimp['Climate Change']
        if isinstance(mix, dict):  # multi target
            impacts[year] = {k: imp[k]['Climate Change'] for k in imp.keys()}
        else:  # single target
            impacts[year] = imp['Climate Change']
    if show_progress:
        progress_info_year.progress('Done!')
        progress_info_computation.hide()
    return flows_dict, prods, mixs, prod_impacts, impacts


def load_data(config: Parameter, years: list[str], savedir: str = './mix_analysis/results/'):
    """
    Loads the data generated by generate_data.
    Parameters
    ----------
    config: ecodynelec.Parameter
        Configuration used to generate the data
    years: list of str
        List of the years to load
    savedir: str
        Directory where the data is saved
    Returns
    -------
        See generate_data
    """
    ### Formating the time extension (see ecodynelec.saving)
    tPass = {'15min': '15min', '30min': '30min', "H": "hour", "D": "day", 'd': 'day', 'W': "week",
             "w": "week", "MS": "month", "M": "month", "YS": "year", "Y": "year"}
    flows_dict = {}  # Productions/imports/exports in kwh per year
    prods = {}
    mixs = {}  # Energetic mix per year
    prod_impacts = {}
    impacts = {}  # Climate change impact per year
    for year in years:
        flows_dict[year] = {}
        prods[year] = {}
        mixs[year] = {}
        prod_impacts[year] = {}
        impacts[year] = {}
        for country in config.target:
            fsavedir = savedir + year + "/" + country + "/"
            flows_dict[year][country] = pd.read_csv(fsavedir + f"RawFlows_{tPass[config.freq]}.csv", index_col=0,
                                                  parse_dates=True)
            prods[year][country] = pd.read_csv(fsavedir + f"ProdMix_{tPass[config.freq]}.csv", index_col=0,
                                              parse_dates=True)
            mixs[year][country] = pd.read_csv(fsavedir + f"Mix_{tPass[config.freq]}.csv", index_col=0,
                                              parse_dates=True)
            prod_impacts[year][country] = pd.read_csv(fsavedir + f"ProdImpact_Climate Change_{tPass[config.freq]}.csv",
                                                 index_col=0,
                                                 parse_dates=True)
            impacts[year][country] = pd.read_csv(fsavedir + f"Impact_Climate Change_{tPass[config.freq]}.csv",
                                                 index_col=0,
                                                 parse_dates=True)
    return flows_dict, prods, mixs, prod_impacts, impacts


def format_data_0(dict_per_year: dict):
    """
    Concat all years contained in the given dict and computes the sum of values per country
    Parameters
    ----------
    dict_per_year: dict of dataframe
        Dictionary containing for each year a dataframe with the values for each production mean for each country
    Returns
    -------
    dict
        Dictionary of:
            - raw_df: dataframe containing the concatenation of all years
            - df: dataframe containing the sum of values per country, and the total production in the 'sum' column
    """
    result = {'raw_df': pd.concat(dict_per_year.values())}
    # Imported electricity mix from each country
    per_country = compute_per_country(result['raw_df'])
    result['df'] = pd.DataFrame.from_dict(per_country).astype('float64')
    result['df']['sum'] = result['df'].sum(axis=1)  # Add total consumption
    return result


def compute_per_country(results: pd.DataFrame):
    """Function to group results per country"""
    countries = np.unique([c.split("_")[-1] for c in results.columns])  # List of countries
    per_country = []
    for c in countries:
        cols = [k for k in results.columns if k.endswith(f"_{c}")]
        per_country.append(pd.Series(results.loc[:, cols].sum(axis=1), name=c))
    return pd.concat(per_country, axis=1)


def plot_years():
    """Plots vertical lines for each year between 2017 and 2021"""
    xcoords = pd.DatetimeIndex(['2017-01-01', '2018-01-01', '2019-01-01', '2020-01-01',
                                '2021-01-01'])
    for xc in xcoords:
        plt.axvline(x=xc, color='black', linestyle='--')


def get_metrics(years, data, metrics, freq, label=None):
    """
    Compute some metrics, yearly or monthly
    Parameters
    ----------
    years: list of str
        The years to compute
    data: pd.DataFrame
        The data to compute the metrics on
    metrics: list of str
        The metrics to compute (see pd.DataFrame.describe)
    freq: str
        'Y' for yearly, 'M' for monthly metrics
    label: list of str, optional
        Columns of the returned dataframes
    Returns
    -------
    A dict containing for each metric, a dataframe of the values for each year/month
    """
    metric_values = {}
    for i in range(len(metrics)):
        metric = metrics[i]
        # compute
        x_axis = []
        metric_values[metric] = []
        if freq == 'Y':
            for y in years:
                year_data = data.loc[[date.year == int(y) for date in data.index]]
                desc = year_data.describe()
                metric_values[metric].append(desc.loc[metric])
                x_axis.append(y)
        elif freq == 'M':
            for y in years:
                year_data = data.loc[[date.year == int(y) for date in data.index]]
                for m in range(1, 13):
                    month_data = year_data.loc[[date.month == m for date in year_data.index]]
                    desc = month_data.describe()
                    metric_values[metric].append(desc.loc[metric])
                    x_axis.append(f'{y}-{m}')
        pdf = pd.DataFrame.from_dict(metric_values[metric])
        pdf.index = pd.Series(x_axis)
        if label is not None:
            pdf.columns = label
        metric_values[metric] = pdf
    return metric_values


def plot_hourly_heatmap(dataframe: pd.DataFrame, column: str, xlabels: list[str], label: str, ylabel: str,
                        val_min: float = 0, val_max: float = 1, fig=None, ax=None, cmap: str = 'hot_r',
                        x_scale: str = 'D'):
    """
    Plots the hourly heatmap of the given dataframe (y-axis: hours, x-axis: days or chosen x_scale)
    Parameters
    ----------
    dataframe: pd.DataFrame
        Dataframe containing the data to plot, with a DatetimeIndex
    column: str
        Name of the column to plot
    xlabels: list of str
        List of labels for the x-axis
    label: str
        Label for the title of the heatmap
    ylabel: str
        Label for the colorbar
    val_min: float, optional
        Minimum value for the colorbar
    val_max: float, optional
        Maximum value for the colorbar
    fig: matplotlib.figure.Figure, optional
        Figure to plot on
    ax: matplotlib.axes.Axes, optional
        Axes to plot on
    cmap: str, optional
        Colormap to use
    x_scale: str, optional
        Resampling frequency for the x-axis
    """
    if fig is None or ax is None:
        fig, ax = plt.subplots(figsize=(12, 4))
    # Reshape the dataframe to a pivot table
    df_pivot = dataframe.pivot_table(index=dataframe.index.date, columns=dataframe.index.hour, values=column)
    df_pivot.index = pd.DatetimeIndex(df_pivot.index)
    df_pivot = df_pivot.resample(x_scale).mean()
    df_pivot = df_pivot.transpose()
    seaborn.heatmap(df_pivot, ax=ax, cmap=cmap, cbar_kws={'label': ylabel}, vmin=val_min, vmax=val_max)
    xlabels.append('')  # Add an empty label for the last tick
    ax.set_xticks(np.linspace(0, len(df_pivot.columns), len(xlabels)), labels=xlabels)
    ax.set_title(f'{label} per hour of the day')
    ax.set_xlabel('Time interval: day')
    ax.set_ylabel('Hour of the day')


def plot_typical_days(seasonal_data, season_labels, label, ylabel, fig=None, ax=None):
    if fig is None or ax is None:
        fig, ax = plt.subplots(1, len(season_labels), sharey=True, figsize=(12, 3))
    for i in range(len(season_labels)):
        a = ax[i]
        by_hour = seasonal_data[i].groupby(seasonal_data[i].index.hour).mean()
        a.plot(by_hour)
        a.set_title(f'{season_labels[i]}')
        a.set_xlabel('Hour of the day')
        a.set_ylabel(ylabel)
    fig.suptitle(f'{label} per season')
    fig.tight_layout()






def mix_to_kwh(parameters: Parameter, flows_df: pd.DataFrame, mix_df: pd.DataFrame, target: str, return_data: str):
    """
    DEPRECATED
    Converts a relative mix to absolute values (in kWh) for the target country. According to the total_kwh values, it will return:
     - the producing mix in kWh if total_kwh is the local electricity production (Prod) at parameters.freq frequency.
     - the consumption mix in kWh if total_kwh is the local electricity consumption (Prod+Imports-Exports) at parameters.freq frequency.
    Parameters
    ----------
    parameters: ecodynelec.Parameter
        Parameters returned by load_config.
    flows_df: pandas.DataFrame
        The raw productions/imports/exports (in kWh) for the target country.
        Returned by get_flows_kwh.
    mix_df: pandas.DataFrame
        The electricity mix for the target country.
        Returned by get_mix.
    target: str
        The target country (should be included in parameters.target).
    return_data: str
        A string indicating what to return. Can be:
            - '+P': the production mix in kWh
            - '+I': the import mix in kWh
            - '+I-E': the import - export mix in kWh
            - '+P+I': the production + import mix in kWh
            - '+P+I-E': the production + import - export mix in kWh

    Returns
    -------
    power_df: pandas.DataFrame
        A dataframe with the production or consumption mix in kWh for the target country.

    """
    total_kwh = flows_df['production'] if '+P' in return_data else None
    if '+I' in return_data:
        total_kwh = total_kwh.add(flows_df['imports'], axis=0) if total_kwh is not None else flows_df['imports']
        if '-E' in return_data:
            total_kwh = total_kwh.subtract(flows_df['exports'], axis=0)
    if total_kwh is None:
        raise ValueError('You must specify at least one of the following return_data: P, +I')
    prod_df = mix_df.multiply(total_kwh, axis=0)
    if '+I' in return_data:
        power_df = prod_df.copy()
    else:  # Ignore import sources
        power_df = prod_df[[col for col in prod_df.columns if col.endswith(f'_{target}')]].copy()
    # Rescale to the desired total_kwh
    print('tt kwh', total_kwh)
    print('power df', power_df.sum(axis=1))
    print('tt kwh y', total_kwh.sum(axis=0))
    print('power df y', power_df.sum(axis=1).sum(axis=0))
    power_df = power_df.multiply((total_kwh.divide(power_df.sum(axis=1), axis=0)), axis=0)
    return power_df
