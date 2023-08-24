# apsim_runner.py

import os
import subprocess
import shutil
import xml.etree.ElementTree as ET
import tqdm

def run(met_list, apsim_file):
    '''met 파일 불러오기'''
    print('met 리스트 : \n', met_list)

    inpath = r'C:/Apsim_scenario_GUI/apsim_run/'
    os.chdir(inpath)

    '''apsim 파일 불러오기'''
    wheat_tree = ET.parse(apsim_file)
    root = wheat_tree.getroot()

    '''run.apsim 파일 내 met 경로 변경'''
    for i in tqdm.tqdm(range(len(met_list))):
        for node in root.iter('simulation'):
            node.attrib['name'] = met_list[i][65:-4] ## path len = 76

            for metfile in node.iter('metfile'):
                for filename in metfile.iter('filename'):
                    filename.text = met_list[i]

        updated_xml_data = ET.tostring(wheat_tree.getroot(), encoding='utf-8').decode('utf-8')
        wheat_tree.write(apsim_file)  # apsim 파일 덮어 씌우기
        apsim_exe = f'C:/Program Files (x86)/APSIM710-r4218/Model/Apsim.exe {apsim_file}'  # apsim exe 경로 및 apsim 파일 선언
        subprocess.run(apsim_exe, stdout=open(os.devnull, 'wb'))

def move_files(dir_path):
    """폴더내 파일 검사"""

    global_cache = {}

    def cached_listdir(path):
        res = global_cache.get(path)
        if res is None:
            res = os.listdir(path)
            global_cache[path] = res
        return res

    def move_file(ext):
        if item.rpartition(".")[2] == ext:
            """폴더 이동"""
            tDir = dir_path + '/' + ext

            if not os.path.isdir(tDir):
                os.mkdir(tDir)

            filePath = dir_path + '/' + item
            finalPath = tDir + '/' + item

            if os.path.isfile(filePath):
                shutil.move(filePath, finalPath)

    cached_listdir(dir_path)

    for item in global_cache[dir_path]:

        """추가할 확장자를 수동으로 리스트에 추가"""
        extList = ["sum", "out"]

        for i in range(0, len(extList)):
            move_file(extList[i])

def main():
    met_list = [f'C:\Apsim_scenario_GUI\output\preprocess_weather\each\weather_met\{x}' for x in os.listdir("../output/preprocess_weather/each/weather_met/") if x.endswith(".met")]
    apsim_file = "run.apsim"
    run(met_list, apsim_file)

if __name__ == '__main__':
    main()
    move_files(r'C:\Apsim_scenario_GUI\apsim_run')
