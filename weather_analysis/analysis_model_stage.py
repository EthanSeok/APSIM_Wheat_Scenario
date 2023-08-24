from datetime import datetime
import tqdm
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib import font_manager, rc
import seaborn as sns
import os


size = 11.5
params = {'legend.fontsize': size,
          'axes.labelsize': size * 1.5,
          'axes.titlesize': size * 1.2,
          'xtick.labelsize': size,
          'ytick.labelsize': size,
          'axes.titlepad': 12}
plt.rcParams.update(params)

def preprocess(df):
    df = df.reset_index()
    df['sim_year'] = df['year']
    df.loc[(df["year"] == 2023) & (df["day"] >= 60), 'sim_year'] = df['past_year']
    df['timestamp'] = pd.to_datetime(df['year'] * 1000 + df['day'],format='%Y%j')
    df['datetime'] = pd.to_datetime(df['timestamp']).dt.strftime('%Y%m%d')
    df['datetime'] = df['datetime'].astype(int)
    df['month_day'] = pd.to_datetime(df['timestamp']).dt.strftime('%m%d')
    return df


def cal_gdd_ndawn(df, year):
    df = preprocess(df)
    df = df[df['past_year'] == year]

    ### GDD 계산
    base_temp = 0
    df['gdd_ndawn'] = df['gdd'].apply(lambda x: max(x - base_temp, 0))
    df['GDD_ndawn'] = df['gdd_ndawn'].cumsum()

    return df

def ndawn_stage(row):
    if row['GDD_ndawn'] >= 0 and row['GDD_ndawn'] < 538:
        return 'Sowing'
    elif row['GDD_ndawn'] >= 538 and row['GDD_ndawn'] < 967:
        return 'Tillering'
    elif row['GDD_ndawn'] >= 967 and row['GDD_ndawn'] < 1255:
        return 'Booting'
    elif row['GDD_ndawn'] >= 1255 and row['GDD_ndawn'] < 1539:
        return 'Heading'
    elif row['GDD_ndawn'] >= 1539 and row['GDD_ndawn'] < 2000:
        return 'Ripening'
    elif row['GDD_ndawn'] >= 2000:
        return 'Harvest'

def dashboard(df, date_today_month, date_today_day):
    df['ndawn_stage'] = df.apply(ndawn_stage, axis=1)
    df['cumrain'] = df.groupby(['past_year'])['rain'].cumsum()
    rainfall = df.drop_duplicates(subset='past_year', keep='last').sort_values(by='cumrain', ascending=False)
    rainfall['rainfall_rank'] = range(1, len(rainfall) + 1)

    ### stage
    df = df[~((df['ndawn_stage'] == 'Ripening') & (df['yield'] <= 0))]
    df = df[~((df['ndawn_stage'] == 'Harvest') & (df['yield'] <= 0))]
    current = df[df['past_year'] == 2023]
    if date_today_month < 10:
        current = current[current['timestamp'] <= datetime(2023, date_today_month, date_today_day)]
    else:
        current = current[current['timestamp'] <= datetime(2022, date_today_month, date_today_day)]

    Sowing_count = current[current['ndawn_stage'] == 'Sowing']['timestamp'].count()
    Tillering_count = current[current['ndawn_stage'] == 'Tillering']['timestamp'].count()
    Booting_count = current[current['ndawn_stage'] == 'Booting']['timestamp'].count()
    Heading_count = current[current['ndawn_stage'] == 'Heading']['timestamp'].count()
    Ripening_count = current[current['ndawn_stage'] == 'Ripening']['timestamp'].count()
    Harvest_count = current[current['ndawn_stage'] == 'Harvest']['timestamp'].count()


    max_yield_per_year = df.groupby('past_year')['yield'].max().reset_index()
    top10_year = max_yield_per_year.sort_values(by='yield', ascending=False)['past_year'][:5].tolist()
    low10_year = max_yield_per_year.sort_values(by='yield', ascending=True)['past_year'][:5].tolist()

    yieldtop = df[df['past_year'] == top10_year[0]]
    yieldlow = df[df['past_year'] == low10_year[0]]


    max_yield = max(yieldtop['yield'].max(), current['yield'].max())
    annotations = []
    if Sowing_count > 0:
        sowing_datetime = current[current['ndawn_stage'] == 'Sowing']['datetime'].iloc[0]
        best_sowing_datetime = yieldtop[yieldtop['ndawn_stage'] == 'Sowing']['datetime'].iloc[0]
        worst_sowing_datetime = yieldlow[yieldlow['ndawn_stage'] == 'Sowing']['datetime'].iloc[0] if len(
            yieldlow[yieldlow['ndawn_stage'] == 'Sowing']) > 0 else 'yet'
        annotations.append(
            (current[current['ndawn_stage'] == 'Sowing']['timestamp'].iloc[0], max_yield,
             f"Sowing\ncurrent: {sowing_datetime}\nBest: {best_sowing_datetime}\nWorst: {worst_sowing_datetime}")
        )
    if Tillering_count > 0:
        Tillering_datetime = current[current['ndawn_stage'] == 'Tillering']['datetime'].iloc[0]
        best_Tillering_datetime = yieldtop[yieldtop['ndawn_stage'] == 'Tillering']['datetime'].iloc[0]
        worst_Tillering_datetime = yieldlow[yieldlow['ndawn_stage'] == 'Tillering']['datetime'].iloc[0] if len(
            yieldlow[yieldlow['ndawn_stage'] == 'Tillering']) > 0 else 'yet'
        annotations.append(
            (current[current['ndawn_stage'] == 'Tillering']['timestamp'].iloc[0], max_yield,
             f"Tillering\ncurrent: {Tillering_datetime}\nBest: {best_Tillering_datetime}\nWorst: {worst_Tillering_datetime}")
        )
    if Booting_count > 0:
        Booting_datetime = current[current['ndawn_stage'] == 'Booting']['datetime'].iloc[0]
        best_Booting_datetime = yieldtop[yieldtop['ndawn_stage'] == 'Booting']['datetime'].iloc[0]
        worst_Booting_datetime = yieldlow[yieldlow['ndawn_stage'] == 'Booting']['datetime'].iloc[0] if len(
            yieldlow[yieldlow['ndawn_stage'] == 'Booting']) > 0 else 'yet'
        annotations.append(
            (current[current['ndawn_stage'] == 'Booting']['timestamp'].iloc[0], max_yield,
             f"Booting\ncurrent: {Booting_datetime}\nBest: {best_Booting_datetime}\nWorst: {worst_Booting_datetime}")
        )
    if Heading_count > 0:
        Heading_datetime = current[current['ndawn_stage'] == 'Heading']['datetime'].iloc[0]
        best_Heading_datetime = yieldtop[yieldtop['ndawn_stage'] == 'Heading']['datetime'].iloc[0]
        worst_Heading_datetime = yieldlow[yieldlow['ndawn_stage'] == 'Heading']['datetime'].iloc[0] if len(
            yieldlow[yieldlow['ndawn_stage'] == 'Heading']) > 0 else 'yet'
        annotations.append(
            (current[current['ndawn_stage'] == 'Heading']['timestamp'].iloc[0], max_yield * 0.1,
             f"Heading\ncurrent: {Heading_datetime}\nBest: {best_Heading_datetime}\nWorst: {worst_Heading_datetime}")
        )
    if Ripening_count > 0:
        Ripening_datetime = current[current['ndawn_stage'] == 'Ripening']['datetime'].iloc[0]
        best_Ripening_datetime = yieldtop[yieldtop['ndawn_stage'] == 'Ripening']['datetime'].iloc[0]
        worst_Ripening_datetime = yieldlow[yieldlow['ndawn_stage'] == 'Ripening']['datetime'].iloc[0] if len(
            yieldlow[yieldlow['ndawn_stage'] == 'Ripening']) > 0 else 'yet'
        annotations.append(
            (current[current['ndawn_stage'] == 'Ripening']['timestamp'].iloc[0], max_yield * 0.3,
             f"Ripening\ncurrent: {Ripening_datetime}\nBest: {best_Ripening_datetime}\nWorst: {worst_Ripening_datetime}")
        )
    if Harvest_count > 0:
        Harvest_datetime = current[current['ndawn_stage'] == 'Harvest']['datetime'].iloc[0]
        best_Harvest_datetime = yieldtop[yieldtop['ndawn_stage'] == 'Harvest']['datetime'].iloc[0]
        worst_Harvest_datetime = yieldlow[yieldlow['ndawn_stage'] == 'Harvest']['datetime'].iloc[0] if len(
            yieldlow[yieldlow['ndawn_stage'] == 'Harvest']) > 0 else 'yet'
        annotations.append(
            (current[current['ndawn_stage'] == 'Harvest']['timestamp'].iloc[0], max_yield * 0.1,
             f"Harvest\ncurrent: {Harvest_datetime}\nBest: {best_Harvest_datetime}\nWorst: {worst_Harvest_datetime}")
        )

    max_yield_annotation = max([annotation[1] for annotation in annotations])


    ### figure
    fig, ax = plt.subplots(figsize=(10, 4.7), dpi=150, facecolor="w")
    sns.lineplot(x='timestamp', y='yield', data=yieldtop, color='firebrick', linestyle='dashed', lw=2, label='best') #, label=f'Best Year: {top10_year[0]}')
    sns.lineplot(x='timestamp', y='yield', data=yieldlow, color='blue', linestyle='dashed', lw=2, label='worst') #, label=f'Worst Year: {low10_year[0]}')
    sns.lineplot(x='timestamp', y='yield', data=current, color='saddlebrown', linestyle='dashed', lw=2.5, label='current') #, label='Current Year')

    ax.axhline(current['yield'].max(), color='black', linestyle='--')

    if date_today_month < 10:
        ax.text(datetime(2023, date_today_month, date_today_day), current['yield'].max() + 200, "Current", ha='center', fontsize=10,
            bbox=dict(boxstyle='round,pad=0.3', facecolor='white',lw=0.5)) #, edgecolor='black', ))
    else:
        ax.text(datetime(2022, date_today_month, date_today_day), current['yield'].max() + 200, "Current", ha='center', fontsize=10,
            bbox=dict(boxstyle='round,pad=0.3', facecolor='white',lw=0.5)) #, edgecolor='black', ))

    max_yield_top = yieldtop['yield'].max()
    max_yield_low = yieldlow['yield'].max()
    max_yield_current = current['yield'].max()
    ax.text(yieldtop['timestamp'].iloc[-1], max_yield_top, f"{top10_year[0]}\n{max_yield_top}", ha='right', va='bottom', fontsize=11)
    ax.text(yieldlow['timestamp'].iloc[-1], max_yield_low, f" {low10_year[0]}\n{max_yield_low}", ha='right', va='top', fontsize=11)
    ax.text(yieldlow['timestamp'].iloc[-1], max_yield_current, f" {2023}\n{max_yield_current}", ha='right', va='top', fontsize=11)

    toprain = rainfall[rainfall['past_year'] == top10_year[0]]['cumrain'].iloc[0]
    lowrain = rainfall[rainfall['past_year'] == low10_year[0]]['cumrain'].iloc[0]
    currentrain = df[df['past_year'] == 2023]
    currentrain = currentrain[currentrain['timestamp']<= datetime(2023, date_today_month, date_today_day)]['cumrain'].iloc[-1]
    ax.text(datetime(2022, 10, 21), max_yield/2, f"Precipitation\n{top10_year[0]}: {toprain:.1f}$mm$\n{low10_year[0]}: {lowrain:.1f}$mm$\ncurrent: {currentrain:.1f}$mm$",
            ha='left', va='center', fontsize=12 ,fontweight='bold',
            bbox=dict(boxstyle='round,pad=0.3', facecolor='white', edgecolor='black', lw=0.5))


    for date, y_pos, label in annotations:
        ax.axvline(date, color='black', linestyle='--', linewidth=1)
        ax.annotate(label, xy=(date, y_pos), xytext=(5, 0), textcoords='offset points',
                    ha='left', va='center', fontsize=8.5, fontweight='bold',
                    bbox=dict(boxstyle='round,pad=0.3', facecolor='white', edgecolor='black', lw=0.5, alpha=0.5),
                    arrowprops=dict(arrowstyle='->', connectionstyle='angle3,angleA=0,angleB=-90', lw=2.0))


    ax.grid(axis="y", which='major', linestyle='--', linewidth=0.5)
    for s in ["left", "right", "top"]:
        ax.spines[s].set_visible(False)
    ax.set_ylim(bottom=0, top=max_yield_annotation + 200)
    ax.set_xlabel('')
    ax.set_ylabel('Yield ($kg/ha$)')
    ax.legend(loc='lower left')
    fig.tight_layout()

    output_dir_txt = "../output/weather_analysis/figure/dashboard_v2"
    if not os.path.exists(output_dir_txt):
        os.makedirs(output_dir_txt)
    plt.savefig(f'{output_dir_txt}/dashboard_v2.png')
    plt.close()


def dashboard_rain_sws(df, date_today_month, date_today_day):
    df['ndawn_stage'] = df.apply(ndawn_stage, axis=1)
    df['cumrain'] = df.groupby(['past_year'])['rain'].cumsum()
    df = df[~((df['ndawn_stage'] == 'Ripening') & (df['yield'] <= 0))]
    df = df[~((df['ndawn_stage'] == 'Harvest') & (df['yield'] <= 0))]
    current = df[df['past_year'] == 2023]
    current = current[current['timestamp'] <= datetime(2023, date_today_month , date_today_day)]

    Sowing_count = current[current['ndawn_stage'] == 'Sowing']['timestamp'].count()
    Tillering_count = current[current['ndawn_stage'] == 'Tillering']['timestamp'].count()
    Booting_count = current[current['ndawn_stage'] == 'Booting']['timestamp'].count()
    Heading_count = current[current['ndawn_stage'] == 'Heading']['timestamp'].count()
    Ripening_count = current[current['ndawn_stage'] == 'Ripening']['timestamp'].count()
    Harvest_count = current[current['ndawn_stage'] == 'Harvest']['timestamp'].count()


    max_yield_per_year = df.groupby('past_year')['yield'].max().reset_index()
    top10_year = max_yield_per_year.sort_values(by='yield', ascending=False)['past_year'][:5].tolist()
    low10_year = max_yield_per_year.sort_values(by='yield', ascending=True)['past_year'][:5].tolist()

    yieldtop = df[df['past_year'] == top10_year[0]]
    yieldlow = df[df['past_year'] == low10_year[0]]

    swsbest = df[df['past_year'].isin(top10_year)]
    swsworst = df[df['past_year'].isin(low10_year)]


    swstop = yieldtop.groupby(['past_year', 'timestamp'])['sws(1)'].mean().reset_index()
    swslow = yieldlow.groupby(['past_year', 'timestamp'])['sws(1)'].mean().reset_index()

    max_sws = max(swstop['sws(1)'].max(), current['sws(1)'].max(), swslow['sws(1)'].max())
    annotations = []
    if Sowing_count > 0:
        sowing_datetime = current[current['ndawn_stage'] == 'Sowing']['datetime'].iloc[0]
        best_sowing_datetime = yieldtop[yieldtop['ndawn_stage'] == 'Sowing']['datetime'].iloc[0]
        worst_sowing_datetime = yieldlow[yieldlow['ndawn_stage'] == 'Sowing']['datetime'].iloc[0] if len(
            yieldlow[yieldlow['ndawn_stage'] == 'Sowing']) > 0 else 'yet'
        annotations.append(
            (current[current['ndawn_stage'] == 'Sowing']['timestamp'].iloc[0], max_sws,
             f"Sowing\ncurrent: {sowing_datetime}\nBest: {best_sowing_datetime}\nWorst: {worst_sowing_datetime}")
        )
    if Tillering_count > 0:
        Tillering_datetime = current[current['ndawn_stage'] == 'Tillering']['datetime'].iloc[0]
        best_Tillering_datetime = yieldtop[yieldtop['ndawn_stage'] == 'Tillering']['datetime'].iloc[0]
        worst_Tillering_datetime = yieldlow[yieldlow['ndawn_stage'] == 'Tillering']['datetime'].iloc[0] if len(
            yieldlow[yieldlow['ndawn_stage'] == 'Tillering']) > 0 else 'yet'
        annotations.append(
            (current[current['ndawn_stage'] == 'Tillering']['timestamp'].iloc[0], max_sws,
             f"Tillering\ncurrent: {Tillering_datetime}\nBest: {best_Tillering_datetime}\nWorst: {worst_Tillering_datetime}")
        )
    if Booting_count > 0:
        Booting_datetime = current[current['ndawn_stage'] == 'Booting']['datetime'].iloc[0]
        best_Booting_datetime = yieldtop[yieldtop['ndawn_stage'] == 'Booting']['datetime'].iloc[0]
        worst_Booting_datetime = yieldlow[yieldlow['ndawn_stage'] == 'Booting']['datetime'].iloc[0] if len(
            yieldlow[yieldlow['ndawn_stage'] == 'Booting']) > 0 else 'yet'
        annotations.append(
            (current[current['ndawn_stage'] == 'Booting']['timestamp'].iloc[0], max_sws,
             f"Booting\ncurrent: {Booting_datetime}\nBest: {best_Booting_datetime}\nWorst: {worst_Booting_datetime}")
        )
    if Heading_count > 0:
        Heading_datetime = current[current['ndawn_stage'] == 'Heading']['datetime'].iloc[0]
        best_Heading_datetime = yieldtop[yieldtop['ndawn_stage'] == 'Heading']['datetime'].iloc[0]
        worst_Heading_datetime = yieldlow[yieldlow['ndawn_stage'] == 'Heading']['datetime'].iloc[0] if len(
            yieldlow[yieldlow['ndawn_stage'] == 'Heading']) > 0 else 'yet'
        annotations.append(
            (current[current['ndawn_stage'] == 'Heading']['timestamp'].iloc[0], max_sws * 0.85,
             f"Heading\ncurrent: {Heading_datetime}\nBest: {best_Heading_datetime}\nWorst: {worst_Heading_datetime}")
        )
    if Ripening_count > 0:
        Ripening_datetime = current[current['ndawn_stage'] == 'Ripening']['datetime'].iloc[0]
        best_Ripening_datetime = yieldtop[yieldtop['ndawn_stage'] == 'Ripening']['datetime'].iloc[0]
        worst_Ripening_datetime = yieldlow[yieldlow['ndawn_stage'] == 'Ripening']['datetime'].iloc[0] if len(
            yieldlow[yieldlow['ndawn_stage'] == 'Ripening']) > 0 else 'yet'
        annotations.append(
            (current[current['ndawn_stage'] == 'Ripening']['timestamp'].iloc[0], 0.15,
             f"Ripening\ncurrent: {Ripening_datetime}\nBest: {best_Ripening_datetime}\nWorst: {worst_Ripening_datetime}")
        )
    if Harvest_count > 0:
        Harvest_datetime = current[current['ndawn_stage'] == 'Harvest']['datetime'].iloc[0]
        best_Harvest_datetime = yieldtop[yieldtop['ndawn_stage'] == 'Harvest']['datetime'].iloc[0]
        worst_Harvest_datetime = yieldlow[yieldlow['ndawn_stage'] == 'Harvest']['datetime'].iloc[0] if len(
            yieldlow[yieldlow['ndawn_stage'] == 'Harvest']) > 0 else 'yet'
        annotations.append(
            (current[current['ndawn_stage'] == 'Harvest']['timestamp'].iloc[0], max_sws,
             f"Harvest\ncurrent: {Harvest_datetime}\nBest: {best_Harvest_datetime}\nWorst: {worst_Harvest_datetime}")
        )

    fig, ax = plt.subplots(figsize=(10, 4.7), dpi=150, facecolor="w")
    sns.lineplot(x='timestamp', y='sws(1)', data=swsbest, color='orange')
    sns.lineplot(x='timestamp', y='sws(1)', data=swsworst, color='skyblue')
    sns.lineplot(x='timestamp', y='sws(1)', data=current, color='gray')

    for date, y_pos, label in annotations:
        ax.axvline(date, color='black', linestyle='--', linewidth=1)
        ax.annotate(label, xy=(date, y_pos), xytext=(5, 10), textcoords='offset points',
                    ha='left', va='center', fontsize=8.5, fontweight='bold',
                    bbox=dict(boxstyle='round,pad=0.3', facecolor='white', edgecolor='black', lw=0.5, alpha=0.7),
                    arrowprops=dict(arrowstyle='->', connectionstyle='angle3,angleA=0,angleB=-90', lw=2.0))


    ax.grid(axis="y", which='major', linestyle='--', linewidth=0.5)
    for s in ["left", "right", "top"]:
        ax.spines[s].set_visible(False)
    x_axis_limit = datetime(2023, 7, 1)
    y_axis_limit = 0.65
    ax.set_xlim(left=None, right=x_axis_limit)
    ax.set_ylim(bottom=None, top=y_axis_limit)
    ax.set_xlabel('')
    ax.set_ylabel('Soil Water Storage ($mm/mm$)')
    fig.tight_layout()

    output_dir_txt = "../output/weather_analysis/figure/dashboard_rain_sws_v2"
    if not os.path.exists(output_dir_txt):
        os.makedirs(output_dir_txt)
    plt.savefig(f'{output_dir_txt}/dashboard_rain_sws_v2.png')
    plt.close()


def rain_toplow(df, date_today_month, date_today_day):
    df['ndawn_stage'] = df.apply(ndawn_stage, axis=1)
    df['cumrain'] = df.groupby(['past_year'])['rain'].cumsum()

    max_yield_per_year = df.groupby('past_year')['yield'].max().reset_index()
    top10_year = max_yield_per_year.sort_values(by='yield', ascending=False)['past_year'][:5].tolist()
    low10_year = max_yield_per_year.sort_values(by='yield', ascending=True)['past_year'][:5].tolist()

    yieldbest = df[df['past_year'] == top10_year[0]]
    yieldworst = df[df['past_year'] == low10_year[0]]

    yieldtop = df[df['past_year'].isin(top10_year)]
    yieldlow = df[df['past_year'].isin(low10_year)]

    ### stage
    df = df[~((df['ndawn_stage'] == 'Ripening') & (df['yield'] <= 0))]
    df = df[~((df['ndawn_stage'] == 'Harvest') & (df['yield'] <= 0))]
    current = df[df['past_year'] == 2023]
    current = current[current['timestamp'] <= datetime(2023, date_today_month , date_today_day)]

    Sowing_count = current[current['ndawn_stage'] == 'Sowing']['timestamp'].count()
    Tillering_count = current[current['ndawn_stage'] == 'Tillering']['timestamp'].count()
    Booting_count = current[current['ndawn_stage'] == 'Booting']['timestamp'].count()
    Heading_count = current[current['ndawn_stage'] == 'Heading']['timestamp'].count()
    Ripening_count = current[current['ndawn_stage'] == 'Ripening']['timestamp'].count()
    Harvest_count = current[current['ndawn_stage'] == 'Harvest']['timestamp'].count()

    max_rain = max(yieldbest['cumrain'].max(), yieldworst['cumrain'].max(),current['cumrain'].max())
    annotations = []
    if Sowing_count > 0:
        sowing_datetime = current[current['ndawn_stage'] == 'Sowing']['datetime'].iloc[0]
        best_sowing_datetime = yieldtop[yieldtop['ndawn_stage'] == 'Sowing']['datetime'].iloc[0]
        worst_sowing_datetime = yieldlow[yieldlow['ndawn_stage'] == 'Sowing']['datetime'].iloc[0] if len(
            yieldlow[yieldlow['ndawn_stage'] == 'Sowing']) > 0 else 'yet'
        annotations.append(
            (current[current['ndawn_stage'] == 'Sowing']['timestamp'].iloc[0], max_rain,
             f"Sowing\ncurrent: {sowing_datetime}\nBest: {best_sowing_datetime}\nWorst: {worst_sowing_datetime}")
        )
    if Tillering_count > 0:
        Tillering_datetime = current[current['ndawn_stage'] == 'Tillering']['datetime'].iloc[0]
        best_Tillering_datetime = yieldtop[yieldtop['ndawn_stage'] == 'Tillering']['datetime'].iloc[0]
        worst_Tillering_datetime = yieldlow[yieldlow['ndawn_stage'] == 'Tillering']['datetime'].iloc[0] if len(
            yieldlow[yieldlow['ndawn_stage'] == 'Tillering']) > 0 else 'yet'
        annotations.append(
            (current[current['ndawn_stage'] == 'Tillering']['timestamp'].iloc[0], max_rain,
             f"Tillering\ncurrent: {Tillering_datetime}\nBest: {best_Tillering_datetime}\nWorst: {worst_Tillering_datetime}")
        )
    if Booting_count > 0:
        Booting_datetime = current[current['ndawn_stage'] == 'Booting']['datetime'].iloc[0]
        best_Booting_datetime = yieldtop[yieldtop['ndawn_stage'] == 'Booting']['datetime'].iloc[0]
        worst_Booting_datetime = yieldlow[yieldlow['ndawn_stage'] == 'Booting']['datetime'].iloc[0] if len(
            yieldlow[yieldlow['ndawn_stage'] == 'Booting']) > 0 else 'yet'
        annotations.append(
            (current[current['ndawn_stage'] == 'Booting']['timestamp'].iloc[0], max_rain,
             f"Booting\ncurrent: {Booting_datetime}\nBest: {best_Booting_datetime}\nWorst: {worst_Booting_datetime}")
        )
    if Heading_count > 0:
        Heading_datetime = current[current['ndawn_stage'] == 'Heading']['datetime'].iloc[0]
        best_Heading_datetime = yieldtop[yieldtop['ndawn_stage'] == 'Heading']['datetime'].iloc[0]
        worst_Heading_datetime = yieldlow[yieldlow['ndawn_stage'] == 'Heading']['datetime'].iloc[0] if len(
            yieldlow[yieldlow['ndawn_stage'] == 'Heading']) > 0 else 'yet'
        annotations.append(
            (current[current['ndawn_stage'] == 'Heading']['timestamp'].iloc[0], 5,
             f"Heading\ncurrent: {Heading_datetime}\nBest: {best_Heading_datetime}\nWorst: {worst_Heading_datetime}")
        )
    if Ripening_count > 0:
        Ripening_datetime = current[current['ndawn_stage'] == 'Ripening']['datetime'].iloc[0]
        best_Ripening_datetime = yieldtop[yieldtop['ndawn_stage'] == 'Ripening']['datetime'].iloc[0]
        worst_Ripening_datetime = yieldlow[yieldlow['ndawn_stage'] == 'Ripening']['datetime'].iloc[0] if len(
            yieldlow[yieldlow['ndawn_stage'] == 'Ripening']) > 0 else 'yet'
        annotations.append(
            (current[current['ndawn_stage'] == 'Ripening']['timestamp'].iloc[0], 115,
             f"Ripening\ncurrent: {Ripening_datetime}\nBest: {best_Ripening_datetime}\nWorst: {worst_Ripening_datetime}")
        )
    if Harvest_count > 0:
        Harvest_datetime = current[current['ndawn_stage'] == 'Harvest']['datetime'].iloc[0]
        best_Harvest_datetime = yieldtop[yieldtop['ndawn_stage'] == 'Harvest']['datetime'].iloc[0]
        worst_Harvest_datetime = yieldlow[yieldlow['ndawn_stage'] == 'Harvest']['datetime'].iloc[0] if len(
            yieldlow[yieldlow['ndawn_stage'] == 'Harvest']) > 0 else 'yet'
        annotations.append(
            (current[current['ndawn_stage'] == 'Harvest']['timestamp'].iloc[0], max_rain,
             f"Harvest\ncurrent: {Harvest_datetime}\nBest: {best_Harvest_datetime}\nWorst: {worst_Harvest_datetime}")
        )

    ### figure
    fig, ax = plt.subplots(figsize=(10, 4.7), dpi=150, facecolor="w")
    # custom_palette = sns.color_palette(['gray'] * 30)
    top_palette = sns.color_palette('YlOrBr', 5)
    low_palette = sns.color_palette('Blues', 5)

    # sns.lineplot(x='timestamp', y='cumrain', data=df, hue=df['past_year'], palette=custom_palette, legend=False)
    sns.lineplot(x='timestamp', y='cumrain', data=yieldtop, hue=yieldtop['past_year'], palette=top_palette, legend=False)
    sns.lineplot(x='timestamp', y='cumrain', data=yieldlow, hue=yieldlow['past_year'], palette=low_palette, legend=False)
    sns.lineplot(x='timestamp', y='cumrain', data=current, color='black', legend=False)

    for date, y_pos, label in annotations:
        ax.axvline(date, color='black', linestyle='--', linewidth=1)
        ax.annotate(label, xy=(date, y_pos), xytext=(5, 10), textcoords='offset points',
                    ha='left', va='center', fontsize=8.5, fontweight='bold',
                    bbox=dict(boxstyle='round,pad=0.3', facecolor='white', edgecolor='black', lw=0.5, alpha=0.5),
                    arrowprops=dict(arrowstyle='->', connectionstyle='angle3,angleA=0,angleB=-90', lw=2.0))

    ax.grid(axis="y", which='major', linestyle='--', linewidth=0.5)
    for s in ["left", "right", "top"]:
        ax.spines[s].set_visible(False)
    ax.set_xlabel('')
    ax.set_ylabel('Precipitation ($mm$)')
    fig.tight_layout()

    output_dir_txt = "../output/weather_analysis/figure/dashboard_rain_toplow_v2"
    if not os.path.exists(output_dir_txt):
        os.makedirs(output_dir_txt)
    plt.savefig(f'{output_dir_txt}/dashboard_rain_toplow_v2.png')
    plt.close()

def main():
    date_today_month = 5
    date_today_day = 1

    df = pd.read_csv('../output/apsim_run/weather_yield.csv')
    df['timestamp'] = pd.to_datetime(df['timestamp'])
    df['gdd'] = (df['maxt'] + df['mint']) / 2
    filenames = [x for x in os.listdir("../output/preprocess_weather/each/csv_file/") if x.endswith(".csv")]

    year_list = []
    for filename in filenames:
        df1 = pd.read_csv(f'../output/preprocess_weather/each/csv_file/{filename}', index_col='year', header=0)
        df1['past_year'] = filename[-8:-4]
        df1['past_year'] = df1['past_year'].astype(int)
        df1.drop(columns=['timestamp'], inplace=True)
        year_list.append(df1)

    year_list = pd.concat(year_list, axis=0, ignore_index=False)
    gdd_ndawn = []
    for year in tqdm.tqdm(year_list['past_year'].unique()):
        gdd_ndawn.append(cal_gdd_ndawn(df, year))

    gdd_ndawn = pd.concat(gdd_ndawn, axis=0, ignore_index=False)
    dashboard(gdd_ndawn, date_today_month, date_today_day) #
    dashboard_rain_sws(gdd_ndawn, date_today_month, date_today_day)
    rain_toplow(gdd_ndawn, date_today_month, date_today_day)


if __name__=='__main__':
    main()