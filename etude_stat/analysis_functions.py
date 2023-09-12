"""
Helper functions for notebooks in etude_stat
Partially moved to examples.mix_analysis.analysis_functions
"""

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from statsmodels.tsa.seasonal import seasonal_decompose

from examples.mix_analysis.analysis_functions import compute_per_country, get_metrics, plot_years, plot_typical_days


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


def plot_trend(ax, df, y, degree, label='Trendline'):
    """Function to plot a trendline on a dataframe"""
    x = np.arange(len(df))
    z = np.polyfit(x, y, degree)
    f = np.poly1d(z)
    ax.plot(df.index, f(x), label=label)


def plot_metrics(years, data, title, metrics, freq, ax=None, linestyle='-', legend=True, label=None, color=None):
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
