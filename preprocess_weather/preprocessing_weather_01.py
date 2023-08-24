import pandas as pd
import os
from datetime import datetime

def check_doy(year, month, day):
    date_string = f'{year}-{month}-{day}'
    date = datetime.strptime(date_string, '%Y-%m-%d')
    doy = date.timetuple().tm_yday
    # print(f"DOY: {doy}")
    return doy

def is_leap_year(year):
    if year % 4 != 0:
        return False
    elif year % 100 != 0:
        return True
    elif year % 400 != 0:
        return False
    else:
        return True

def interpolation(df):
    df.drop_duplicates(subset='timestamp', keep='first', inplace=True)
    df.set_index('timestamp', inplace=True)
    df = df.resample('D').interpolate().reset_index()
    return df

def preprocess( current_year, check_month, check_day, past_year, site):
    df = pd.read_csv('../output/download_weather/preprocessed_all_weather.csv')

    dfs_by_year = {}
    for year, group in df.groupby('year'):
        dfs_by_year[year] = group

    for i in range(past_year, current_year + 1):
        dfs_by_year[i]['timestamp'] = pd.to_datetime(dfs_by_year[i]['year'] * 1000 + dfs_by_year[i]['day'],format='%Y%j')
        dfs_by_year[i]['month_day'] = dfs_by_year[i]['timestamp'].dt.strftime("%m%d")
        is_leap_day = (dfs_by_year[i]['timestamp'].dt.month == 2) & (dfs_by_year[i]['timestamp'].dt.day == 29)
        dfs_by_year[i] = dfs_by_year[i][~is_leap_day]
        check = dfs_by_year[i][(dfs_by_year[i]['day'] == 61) & (dfs_by_year[i]['month_day'] == '0301')]

        if not check.empty:
            dfs_by_year[i].loc[dfs_by_year[i]['day'] >= 61, 'day'] -= 1
        # print(dfs_by_year[i][(dfs_by_year[i]['year'] == 1980)])

    for i in range(past_year, current_year + 1):
        current = dfs_by_year[current_year]
        current = current[current['day'] <= check_doy(current_year, check_month, check_day)]
        current_date = pd.concat([dfs_by_year[current_year - 1], current])
        current_date = interpolation(current_date)

        ### 확인 작기 이후 기상 처리
        past = dfs_by_year[i]
        if not is_leap_year(past['year'].iloc[0]):
            past = past[past['day'] > check_doy(i, check_month, check_day)].copy()
        else:
            past = past[past['day'] >= check_doy(i, check_month, check_day)].copy()
        past = interpolation(past)
        past.loc[:, 'year'] = current_year
        result = pd.concat([current_date, past])

        output_path = '../output/preprocess_weather/each/csv_file'
        if not os.path.exists(output_path):
            os.makedirs(output_path)
        result.to_csv(f'{output_path}/{site}_{i}.csv', index=False)


def main():
    current_year = 2023
    check_month = 5
    check_day = 1
    past_year = 1983
    site = 'Namwon'

    preprocess(current_year, check_month, check_day, past_year, site)

if __name__=='__main__':
    main()