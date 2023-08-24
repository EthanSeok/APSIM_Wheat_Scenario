### APSIM scenario DDS

---

* 오늘 이후의 기상자료는 과거 40년 기상 자료로 대체합니다.


* 과거 40년간의 기상자료 중  생산량이 가장 높은 해와 낮은 해의 토양 수분, 강수량을 비교합니다.


* 본 프로그램을 사용하여 강수량과 토양 수분 함량을 확인하고, 분석함으로써 생산량을 높이기 위한 관수 전략을 세울 수 있습니다.

<br>

### 사용 방법

**APSIM 7.10-r4218 버전이 설치되어있어야 합니다.**

**반드시 C드라이브 root에 설치할 것.**


* 코드를 실행하면 GUI 창이 표시됩니다. 여기에서 사용자는 APSIM 시뮬레이션을 설정하고 실행할 수 있습니다.


* "Simulation Parameters" 섹션에서 시뮬레이션 매개변수를 입력합니다. 이 매개변수에는 지점 코드, 이름, 위도, 경도, 시작 및 끝 년도, 파종 날짜, 종료 날짜, 월 및 일, met 경로 및 apsim 파일이 포함됩니다.


* "Run Simulation" 버튼을 클릭하여 시뮬레이션을 실행합니다. 이 단계에서 날씨 데이터를 다운로드하고 전처리하며, APSIM 시뮬레이션을 실행하고 결과를 생성합니다.


* "Select Graphs" 옵션에서 표시할 그래프를 선택합니다.


* "Display Graph" 버튼을 클릭하여 선택한 그래프를 표시합니다. 그래프는 시뮬레이션 결과를 시각화하는 데 사용됩니다.


* "Help" 메뉴를 통해 사용 설명서를 확인할 수 있습니다.


* "File" 메뉴의 "폴더 열기" 옵션을 사용하여 폴더를 선택하고 선택한 폴더 경로를 확인할 수 있습니다.

**이 코드는 APSIM 시뮬레이션 실행 및 결과 분석을 단순화하고 시각화하는 데 도움이 될 수 있습니다. 사용자가 필요에 따라 매개변수를 조정하고 결과를 시각화할 수 있습니다.**

<br>

![dashboard_v2](https://github.com/EthanSeok/APSIM_Python/assets/93086581/a915021e-8217-4716-8875-f4c46cb15714)*Yield*

![dashboard_rain_sws](https://github.com/EthanSeok/APSIM_Python/assets/93086581/5f9786d3-af57-4878-a1a2-be45a4c551e7)*Soil Water Content*

![dashboard_rain_toplow_v2](https://github.com/EthanSeok/APSIM_Python/assets/93086581/f39a6aa9-bab8-45f0-8e40-577eabfe9242)*Cumilative Precipitation*

<br>

### APSIM scenario GUI

![image](https://github.com/EthanSeok/APSIM_Python/assets/93086581/14d1e3f0-0603-4fe5-9d2b-3e01d7b162ec)
