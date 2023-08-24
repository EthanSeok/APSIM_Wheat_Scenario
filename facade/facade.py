import os
import pandas as pd
import PySimpleGUI as sg
from download_weather import weather_download
from preprocess_weather import preprocessing_weather_01
from preprocess_weather import preprocessing_weather_02
from apsim_run import run_apsim
from apsim_run import apsim_afterprocessing
from weather_analysis import analysis_model_stage

def show_popup(message, auto_close_duration=None):
    sg.popup_non_blocking(message, non_blocking=True, auto_close_duration=auto_close_duration)

def show_popup_image(image_path):
    layout = [
        [sg.Image(filename=image_path)],
        [sg.Button("Close")]
    ]

    window = sg.Window("Graph", layout, finalize=True)

    while True:
        event, _ = window.read()

        if event == sg.WIN_CLOSED or event == "Close":
            break

    window.close()

def show_help():
    sg.popup("사용 설명서:\n"
             "1. C 드라이브 root에 설치하십시요.\n"
             "2. 시뮬레이션 매개변수를 입력하고 'Run Simulation' 버튼을 클릭하여 시뮬레이션을 실행할 수 있습니다.\n"
             "3. 'Select Graphs' 옵션을 사용하여 표시할 그래프를 선택할 수 있습니다.\n"
             "4. 'Display Graph' 버튼을 클릭하여 선택한 그래프를 표시할 수 있습니다.",
             title="도움말")


def open_folder():
    folder_path = sg.popup_get_folder("폴더를 선택하세요")
    if folder_path:
        sg.popup(f"선택한 폴더: {folder_path}")

def dw_api(start, end, stn_Ids, latitude):
    # show_popup('downloading weather ...', auto_close_duration=1.5)
    weather_download.dw_weather(stn_Ids, start, end)
    weather_download.pm_weather(weather_download.dw_weather(stn_Ids, start, end), latitude)
    # print('downloading weather Complete!')
    show_popup('Downloading weather complete!', auto_close_duration=1.5)

def preprocess(current_year, check_month, check_day, past_year, site, latitude, longitude):
    # show_popup('preprocess weather ...', auto_close_duration=1.5)
    preprocessing_weather_01.preprocess(current_year, check_month, check_day, past_year, site)

    filenames = [x for x in os.listdir("../output/preprocess_weather/each/csv_file/") if x.endswith(".csv") and site in x]

    for filename in filenames:
        df = pd.read_csv(f'../output/preprocess_weather/each/csv_file/{filename[:-4]}.csv')
        preprocessing_weather_02.preprocess(df, site, latitude, longitude, filename[:-4])
    show_popup('preprocess weather Complete!')

def run_sim(met_path, apsim_file, site):
    show_popup('runnig APSIM ...', auto_close_duration=1.5)

    met_list = [f'{met_path}\{x}' for x in os.listdir(f"{met_path}") if x.endswith(".met") and site in x]

    run_apsim.run(met_list, apsim_file)
    run_apsim.move_files(r'C:\Apsim_scenario_GUI\apsim_run')
    show_popup('Simulation Complete!', auto_close_duration=1.5)

def postprocess(met_path, site, start, end):
    # show_popup('post processing ...', auto_close_duration=1.5)
    met_list = [f'{met_path}\{x}'  for x in os.listdir(f"{met_path}") if x.endswith(".met") and site in x]
    filenames = [x for x in os.listdir("../output/preprocess_weather/each/csv_file/") if x.endswith(".csv") and site in x]

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
    apsim_afterprocessing.afterprocess(result, year_list, start, end)

    show_popup('Complete all Process. check your output files', auto_close_duration=1.5)

def graph(date_today_month, date_today_day):
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
    for year in year_list['past_year'].unique():
        gdd_ndawn.append(analysis_model_stage.cal_gdd_ndawn(df, year))
    gdd_ndawn = pd.concat(gdd_ndawn, axis=0, ignore_index=False)

    analysis_model_stage.dashboard(gdd_ndawn, date_today_month, date_today_day)
    analysis_model_stage.dashboard_rain_sws(gdd_ndawn,date_today_month, date_today_day)
    analysis_model_stage.rain_toplow(gdd_ndawn, date_today_month, date_today_day)

    dashboard_path = '../output/weather_analysis/figure/dashboard_v2/dashboard_v2.png'
    dashboard_rain_sws_path = '../output/weather_analysis/figure/dashboard_rain_sws_v2/dashboard_rain_sws_v2.png'
    rain_toplow_path = '../output/weather_analysis/figure/dashboard_rain_toplow_v2/dashboard_rain_toplow_v2.png'

    return dashboard_path, dashboard_rain_sws_path, rain_toplow_path

def display_selected_image(selected_image_path):
    if selected_image_path and selected_image_path.lower().endswith(('.png', '.jpg', '.jpeg', '.gif')):
        show_popup_image(selected_image_path)
    else:
        sg.popup_error('Please select a valid image file.')


def main():
    sg.theme("LightGrey5")  # Set the theme

    # Default values
    default_values = {
        "stn_Ids": "247",
        "site": "Namwon",
        "latitude": "35.4023",
        "longitude": "127.3351",
        "past_year": "1983",
        "current": "2023",
        'start': '20221019',
        'end': '20230620',
        "check_month": "3",
        "check_day": "1",
        "met_path": "C:\\Apsim_scenario_GUI\\output\\preprocess_weather\\each\\weather_met",
        "apsim_file": "run.apsim",
    }

    menu_def = [
        ['File', ['폴더 열기']],
        ['Help', ['도움말']],
    ]

    layout = [
        [sg.Text("Simulation Parameters", font=("Helvetica", 18), justification="center")],
        [sg.Column([  # Create a column for input fields
            [sg.Text("지점 코드:", size=(15,1)), sg.InputText(key="stn_Ids", default_text=default_values["stn_Ids"])],
            [sg.Text("이름:", size=(15,1)), sg.InputText(key="site", default_text=default_values["site"])],
            [sg.Text("위도:", size=(15,1)), sg.InputText(key="latitude", default_text=default_values["latitude"])],
            [sg.Text("경도:", size=(15,1)), sg.InputText(key="longitude", default_text=default_values["longitude"])],
            [sg.Text("시작 년도:", size=(15,1)), sg.InputText(key="past_year", default_text=default_values["past_year"])],
            [sg.Text("끝 년도:", size=(15,1)), sg.InputText(key="current", default_text=default_values["current"])],
            [sg.Text("파종 날짜:", size=(15,1)), sg.InputText(key="start", default_text=default_values["start"])],
            [sg.Text("종료 날짜:", size=(15,1)), sg.InputText(key="end", default_text=default_values["end"])],
            [sg.Text("월:", size=(15,1)), sg.InputText(key="check_month", default_text=default_values["check_month"])],
            [sg.Text("일:", size=(15,1)), sg.InputText(key="check_day", default_text=default_values["check_day"])],
            [sg.Text("met 경로:", size=(15,1)), sg.InputText(key="met_path", default_text=default_values["met_path"])],
            [sg.Text("apsim 파일:", size=(15,1)), sg.InputText(key="apsim_file", default_text=default_values["apsim_file"])],
        ])],
        [sg.Button("Run Simulation", size=(15, 1))],  # Button outside the column
        [sg.Text("Select Graphs:", size=(15, 1))],
        [sg.Checkbox("Yield", key="display_dashboard", default=False),
         sg.Checkbox("SWS", key="display_dashboard_rain_sws", default=False),
         sg.Checkbox("Rain", key="display_rain_toplow", default=False)],
        [sg.Button("Display Graph", size=(15, 1))],
        [sg.Menu(menu_def, tearoff=False, pad=(15,1))],
    ]

    window = sg.Window("APSIM Simulation", layout, resizable=True, finalize=True)

    while True:
        event, values = window.read()

        if event == sg.WIN_CLOSED:
            break

        if event == "Run Simulation":
            stn_Ids = int(values["stn_Ids"])
            site = values["site"]
            latitude = float(values["latitude"])
            longitude = float(values["longitude"])
            past_year = int(values["past_year"])
            current = int(values["current"])
            start = int(values["start"])
            end = int(values["end"])
            check_month = int(values["check_month"])
            check_day = int(values["check_day"])
            met_path = values["met_path"]
            apsim_file = values["apsim_file"]

            dw_api(past_year, current, stn_Ids, latitude)
            preprocess(current, check_month, check_day, past_year, site, latitude, longitude)
            run_sim(met_path, apsim_file, site)
            postprocess(met_path, site, start, end)

        if event == "Display Graph":
            check_month = int(values["check_month"])
            check_day = int(values["check_day"])

            selected_image_path = None  # Initialize the selected_image_path

            if values["display_dashboard"]:
                selected_image_path = graph(check_month, check_day)[0]
            elif values["display_dashboard_rain_sws"]:
                selected_image_path = graph(check_month, check_day)[1]
            elif values["display_rain_toplow"]:
                selected_image_path = graph(check_month, check_day)[2]

            display_selected_image(selected_image_path)

        if event == "도움말":
            show_help()

        if event == "폴더 열기":
            open_folder()

    window.close()

if __name__=='__main__':
    main()
