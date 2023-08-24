import pandas as pd
import os
import csv


def preprocess(df, site, latitude, longitude, filename):
    start = df['year'].unique()[0]
    end = df['year'].unique()[-1]
    df['site'] = site

    tav = round(df.groupby('year').mean()['tavg'].mean(), 2)
    amp = round((df.groupby('month').max()['tavg'] - df.groupby('month').min()['tavg']).mean(), 2)

    df.drop(columns=['month', 'tavg', 'humid', 'wind', 'sumradn', 'timestamp', 'month_day'], inplace=True)
    new_row = pd.DataFrame([['()', '()', '()', '(MJ/m2)', '(oC)', '(oC)', '(mm)', '(mm)']],
                           columns=df.columns)
    df = pd.concat([df.iloc[:0], new_row, df.iloc[0:]], ignore_index=True)

    # print(df[df.isnull().any(axis=1)])
    df = df.astype(str)
    df = df['site'] + " " + df['year'] + " " + df['day'] + " " + df['radn'] + " " + df['maxt'] + " " + df[
        'mint'] + " " + df['rain']  # + " " + df['evap']
    # new_row2 = pd.DataFrame([['site year day radn maxt mint rain evap']])
    new_row2 = pd.DataFrame([['site year day radn maxt mint rain']])
    df = pd.concat([df.iloc[:0], new_row2, df.iloc[0:]], ignore_index=True)

    output_dir_xlsx = "../output/preprocess_weather/each/weather_xlsx/"
    if not os.path.exists(output_dir_xlsx):
        os.makedirs(output_dir_xlsx)

    # model 요구에 맞춰 data 추가 & xlsx 완성
    writer = pd.ExcelWriter(os.path.join(output_dir_xlsx, f"{filename}_weather.xlsx"), engine='xlsxwriter')
    workbook = writer.book
    worksheet = workbook.add_worksheet()
    worksheet.write('A1', '[weather.met.weather]')
    worksheet.write('A2', '[weather.met.weather]')
    worksheet.write('A3', f'!Title = {site} {start}-{end}')
    worksheet.write('A4', f'latitude ={latitude}')
    worksheet.write('A5', f'Longitude ={longitude}')
    worksheet.write('A6',
                    f"! TAV and AMP inserted by 'tav_amp' on 31/12/{end} at 10:00 for period from   1/{end} to 366/{end} (ddd/yyyy)")
    worksheet.write('A7', f'tav =  {tav} (oC)     ! annual average ambient temperature')
    worksheet.write('A8', f'amp =  {amp} (oC)     ! annual amplitude in mean monthly temperature')
    worksheet.write('A9', ' ')
    worksheet.write('A10', ' ')
    writer.close()
    writer = pd.ExcelWriter(os.path.join(output_dir_xlsx, f"{filename}_weather.xlsx"), engine='openpyxl', mode="a",
                            if_sheet_exists='overlay')
    df.to_excel(writer, index=False, startrow=10, sheet_name="Sheet1", header=None)
    writer.close()

    output_dir_txt = "../output/preprocess_weather/each/weather_txt/"
    if not os.path.exists(output_dir_txt):
        os.makedirs(output_dir_txt)

    output_dir_met = "../output/preprocess_weather/each/weather_met/"
    if not os.path.exists(output_dir_met):
        os.makedirs(output_dir_met)

    c = pd.read_excel(os.path.join(output_dir_xlsx, f"{filename}_weather.xlsx"))

    c.to_csv(os.path.join(output_dir_txt, f"{filename}.txt"), index=False, header=None, sep=" ",
             quoting=csv.QUOTE_NONE, escapechar=' ', quotechar='', errors='ignore')
    c.to_csv(os.path.join(output_dir_met, f"{filename}.met"), index=False, header=None, sep=" ",
             quoting=csv.QUOTE_NONE, escapechar=' ', quotechar='', errors='ignore')

    return filename


def main():
    latitude = 35.4023
    longitude = 127.3351
    site = 'Namwon'

    filenames = [x for x in os.listdir("../output/preprocess_weather/each/csv_file/") if x.endswith(".csv")]

    for filename in filenames:
        df = pd.read_csv(f'../output/preprocess_weather/each/csv_file/{filename[:-4]}.csv')
        preprocess(df, site, latitude, longitude, filename[:-4])

if __name__=='__main__':
    main()