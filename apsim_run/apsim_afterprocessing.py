import pandas as pd
from weather_analysis import analysis_model_stage
import os

def afterprocess(out, weather, start, end):
    weather = analysis_model_stage.preprocess(weather)
    weather['datetime'] = weather['datetime'].astype(int)
    weather = weather[(weather['datetime'] >= start) & (weather['datetime'] <= end)]
    weather = weather.drop(columns=['wind', 'evap'])
    out = out.sort_values(by='Date')
    result = pd.merge(weather, out, on=['past_year', 'day', 'year'], how='right')
    result = result.sort_values(by='timestamp')

    output_dir_txt = "../output/apsim_run"
    if not os.path.exists(output_dir_txt):
        os.makedirs(output_dir_txt)
    result.to_csv(f'{output_dir_txt}/weather_yield.csv')
    # print(result.info())

    return result

def main():
    start = 20221019
    end = 20230620

    met_list = [f'C:\Apsim_scenario_GUI\output\preprocess_weather\each\weather_met\{x}' for x in os.listdir("../output/preprocess_weather/each/weather_met/") if x.endswith(".met")]
    filenames = [x for x in os.listdir("../output/preprocess_weather/each/csv_file/") if x.endswith(".csv")]

    result = []
    for i in range(len(met_list)):
        out_list = met_list[i][65:-4]
        out_file = pd.read_csv(f'./out/{out_list}.out', sep="\\s+", skiprows=[0, 1, 3],
                               infer_datetime_format=True)
        out_file['Date'] = pd.to_datetime(out_file['Date']).dt.strftime('%d/%m/%Y')
        out_file['Date'] = pd.to_datetime(out_file['Date']).dt.strftime('%Y-%m-%d')
        out_file['Date'] = pd.to_datetime(out_file['Date'])
        out_file['year'] = out_file['Date'].dt.year
        out_file['past_year'] = out_list[-4:]
        out_file['past_year'] = out_file['past_year'].astype(int)
        result.append(out_file)

    year_list = []
    for filename in filenames:
        df = pd.read_csv(f'../output/preprocess_weather/each/csv_file/{filename}', index_col='year', header=0)
        df['past_year'] = filename[-8:-4]
        df['past_year'] = df['past_year'].astype(int)
        df.drop(columns=['timestamp'], inplace=True)
        year_list.append(df)

    year_list = pd.concat(year_list, axis=0, ignore_index=False)
    result = pd.concat(result, axis=0, ignore_index=False)
    afterprocess(result, year_list, start, end)


if __name__=='__main__':
    main()