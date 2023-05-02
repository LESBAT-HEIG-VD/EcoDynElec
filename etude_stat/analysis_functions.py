import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import seaborn as seaborn
from statsmodels.tsa.seasonal import seasonal_decompose

from ecodynelec.pipelines import get_prod_mix_impacts
from ecodynelec.progress_info import ProgressInfo


def export_year(config, year, is_verbose=False, h=None):
    if is_verbose: print('Compute ', year)
    ## Change the starting date
    config.start = year + '-01-01 00:00'
    config.end = year + '-12-31 23:59'
    config.path.savedir = "./test_data/results_res_i_84g/" + year + "/"

    raw, mix, impact = get_prod_mix_impacts(config=config, is_verbose=is_verbose, progress_bar=h)
    return raw, mix, impact

def generate_data(config, years):
    raw_mixs = {}  # Raw mix per year
    mixs = {}  # Energetic mix per year
    impacts = {}  # Climate change impact per year

    f = ProgressInfo('Compute ' + years[0] + '...', len(years) + 1, width='90%')
    h = ProgressInfo('', 11, color='lightgreen', width='90%')

    for year in years:
        f.progress('Compute ' + year + '...', 0)
        raw, mix, imp = export_year(config, year, h=h)  # "mix" is the CH electrical mix
        f.progress()
        raw_mixs[year] = raw
        mixs[year] = mix
        if isinstance(mix, dict):  # multi target
            impacts[year] = {k: imp[k]['Climate Change'] for k in imp.keys()}
        else:  # single target
            impacts[year] = imp['Climate Change']
    f.progress('Done!')
    h.hide()
    return raw_mixs, mixs, impacts


def load_data(config, years):
    ### Formating the time extension (see ecodynelec.saving)
    tPass = {'15min': '15min', '30min': '30min', "H": "hour", "D": "day", 'd': 'day', 'W': "week",
             "w": "week", "MS": "month", "M": "month", "YS": "year", "Y": "year"}
    as_target = "" if config.target is None else f"_{config.target}"
    raw_mixs = {}  # Raw mix per year
    mixs = {}  # Energetic mix per year
    impacts = {}  # Climate change impact per year
    for year in years:
        base_savedir = "./test_data/results/" + year + "/"
        raw_mixs[year] = {}
        mixs[year] = {}
        impacts[year] = {}
        for country in config.target:
            savedir = base_savedir + country + "/"
            raw_mixs[year][country] = pd.read_csv(savedir + f"RawProdExch_{tPass[config.freq]}.csv", index_col=0,
                                              parse_dates=True)
            mixs[year][country] = pd.read_csv(savedir + f"Mix_{tPass[config.freq]}.csv", index_col=0,
                                              parse_dates=True)
            impacts[year][country] = pd.read_csv(savedir + f"Impact_Climate Change_{tPass[config.freq]}.csv",
                                                 index_col=0,
                                                 parse_dates=True)
    return raw_mixs, mixs, impacts


def format_data_0(dict_per_year):
    result = {}
    result['raw_df'] = pd.concat(dict_per_year.values())
    # Imported electricity mix from each country
    per_country = compute_per_country(result['raw_df'])
    result['df'] = pd.DataFrame.from_dict(per_country).astype('float64')
    result['df']['sum'] = result['df'].sum(axis=1)  # Add total production
    # Hydro pumped storage production
    # result['hydro_ch'] = result['raw_df']['Hydro_Pumped_Storage_CH']
    return result


def format_data(dict_per_year, group_by_country=True):
    result = {}
    result['raw_df'] = pd.concat(dict_per_year.values())
    # Imported electricity mix from each country
    if group_by_country:
        per_country = compute_per_country(result['raw_df'])
        result['df'] = pd.DataFrame.from_dict(per_country).astype('float64')
    else:
        result['df'] = result['raw_df']
    result['df']['sum'] = result['df'].sum(axis=1)  # Add total production
    # Hydro pumped storage production
    result['hydro_ch'] = result['raw_df']['Hydro_Pumped_Storage_CH']

    # Take daily average
    result['df_daily'] = result['df'].resample('D').mean()
    result['hydro_ch_daily'] = result['hydro_ch'].resample('D').mean()
    # Take monthly average
    result['df_monthly'] = result['df'].resample('M').mean()
    result['hydro_ch_monthly'] = result['hydro_ch'].resample('M').mean()
    return result


# Helper functions

def compute_per_country(results):
    """Function to group results per country"""
    countries = np.unique([c.split("_")[-1] for c in results.columns])  # List of countries
    per_country = []
    for c in countries:
        cols = [k for k in results.columns if k.endswith(f"_{c}")]
        per_country.append(pd.Series(results.loc[:, cols].sum(axis=1), name=c))

    return pd.concat(per_country, axis=1)


def plot_trend(ax, df, y, degree, label='Trendline'):
    """Function to plot a trendline on a dataframe"""
    x = np.arange(len(df))
    z = np.polyfit(x, y, degree)
    f = np.poly1d(z)
    ax.plot(df.index, f(x), label=label)


def plot_years():
    xcoords = pd.DatetimeIndex(['2017-01-01', '2018-01-01', '2019-01-01', '2020-01-01',
                                '2021-01-01'])
    for xc in xcoords:
        plt.axvline(x=xc, color='black', linestyle='--')


def get_metrics(years, data, metrics, freq, label=None):
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

        # plot
        pdf = pd.DataFrame.from_dict(metric_values[metric])
        pdf.index = pd.Series(x_axis)
        if label is not None:
            pdf.columns = label
        metric_values[metric] = pdf
    return metric_values


def plot_metrics(years, data, title, metrics, freq, ax=None, linestyle='-', legend=True, label=None, color=None):
    # todo use dataframe
    if ax is None:
        fig, ax = plt.subplots(len(metrics), 1, figsize=(18, 4 * len(metrics)))
    metric_values = get_metrics(years, data, metrics, freq, label=label)
    for i in range(len(metrics)):
        metric = metrics[i]
        pdf = metric_values[metric]
        if linestyle == 'bar':
            if metric == 'std':
                pdf.plot(ax=ax[i], legend=legend, linestyle='-', color=color)
            else:
                pdf.plot.bar(ax=ax[i], legend=legend, stacked=False, color=color)
        else:
            pdf.plot(ax=ax[i], legend=legend, linestyle=linestyle, color=color)
            # plot_trend(ax, pdf, pdf['CH'], 1, 'Trendline - CH')
        ax[i].legend(ax[i].get_legend_handles_labels()[1], loc='upper right', bbox_to_anchor=(1.2, 1.0))
        ax[i].set_title(f'{metric} of {title}')
        ax[i].set_label('date')


def plot_evolution(series_daily, series_montly, label, ylabel):
    # plot the five years (daily)
    fig, ax = plt.subplots(figsize=(18, 4))
    ax.plot(series_daily.index, series_daily, label=f'{label}-daily')
    ax.plot(series_montly.index, series_montly, label=f'{label}-montly')
    # plot_trend(ax, series_daily, series_daily, 2, label='Trendline')
    plot_years()
    plt.xlabel('Year')
    plt.ylabel(ylabel)
    plt.title(f'{label} - over all years')
    plt.show()


def plot_seasonal_decomposition(series, label):
    # Seasonal over one year
    decompose_result_mult = seasonal_decompose(series, model="multiplicative", period=12,
                                               extrapolate_trend='freq')
    fig = decompose_result_mult.plot()
    fig.set_figwidth(12)
    fig.suptitle(f'Yearly seasonal decomposition of {label}')
    fig.tight_layout()
    plt.show()


def plot_boxplot(seasonal_data, grouped_data, label, ylabel):
    fig, ax = plt.subplots(figsize=(12, 6))
    ax.boxplot(seasonal_data)
    ax.set_xticklabels(grouped_data.groups.keys())
    ax.set_xlabel('Season')
    ax.set_ylabel(ylabel)
    ax.set_title(f'Seasonal Boxplot of {label}')
    plt.show()


def plot_typical_days(seasonal_data, grouped_data, label, ylabel, fig=None, ax=None):
    season_labels = [*grouped_data.groups.keys()]
    if fig is None or ax is None:
        fig, ax = plt.subplots(1, len(season_labels), sharey=True, figsize=(12, 3))
    for i in range(len(season_labels)):
        a = ax[i]
        by_hour = seasonal_data[i].groupby(seasonal_data[i].index.hour).mean()
        a.plot(by_hour)
        a.set_title(f'{season_labels[i]}')
        a.set_xlabel('Hour of the day')
        a.set_ylabel(ylabel)
    fig.suptitle(f'{label} on average day per season')
    fig.tight_layout()


def plot_heatmap(df, xlabels, label, ylabel, index=0, val_max=1, fig=None, ax=None):
    if fig is None or ax is None:
        fig, ax = plt.subplots(figsize=(12, 4))
    # Reshape the dataframe to a pivot table
    df_pivot = df.pivot_table(index=df.index.date, columns=df.index.hour, values=df.columns[index])
    df_pivot.index = pd.DatetimeIndex(df_pivot.index)
    df_pivot = df_pivot.resample('D').mean()
    df_pivot = df_pivot.transpose()
    seaborn.heatmap(df_pivot, ax=ax, cmap='hot_r', cbar_kws={'label': ylabel}, vmin=0, vmax=val_max)
    xlabels.append('')  # Add an empty label for the last tick
    ax.set_xticks(np.linspace(0, len(df_pivot.columns), 7), labels=xlabels)
    ax.set_title(f'{label} per hour of the day')
    ax.set_xlabel('Time interval: day')
    ax.set_ylabel('Hour of the day')


# Main analysis function
def analyze_series(series, series_daily, series_montly, label, ylabel='Share in total mix (%)'):
    # plot the five years (daily)
    plot_evolution(series_daily, series_montly, label, ylabel)

    # Seasonal over one year
    plot_seasonal_decomposition(series_montly, label)

    # boxplot, to clean !!!!!
    season_names = {2: 'Spring', 3: 'Summer', 4: 'Fall', 1: 'Winter'}
    data = pd.DataFrame(series)
    data['Season'] = [date.month % 12 // 3 + 1 for date in data.index]
    data['Season'] = data['Season'].map(season_names)
    grouped_data = data.groupby('Season')
    seasonal_data = [grouped_data.get_group(season)[data.columns[0]] for season in grouped_data.groups]
    plot_boxplot(seasonal_data, grouped_data, label, ylabel)

    # daily plot per season
    plot_typical_days(seasonal_data, grouped_data, label, ylabel)
    plt.show()

    # Heatmap
    xlabels = list(series_montly.resample('Y').mean().index.map(lambda x: x.year).values)
    plot_heatmap(data, xlabels, label, ylabel)

    return seasonal_data, grouped_data, season_names
