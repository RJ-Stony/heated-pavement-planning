# ❄️ 제설 사각지대 해소를 위한 열선 설치 입지 분석

도심 내 겨울철 결빙 사고를 예방하고, 의료·보행 취약 지역의 안전 사각지대를 줄이기 위해 과학적 근거 기반으로 열선 포장 설치 후보지를 선정하는 프로젝트입니다.

---

## 📌 목차
1. [프로젝트 개요](#프로젝트-개요)
2. [주요 분석 흐름](#주요-분석-흐름)
3. [디렉토리 구조](#디렉토리-구조)
4. [설치 및 실행 방법](#설치-및-실행-방법)
5. [QGIS 활용 시 권장 사항](#qgis-활용-시-권장-사항)
6. [모듈별 설명](#모듈별-설명)
7. [한계 및 개선 방향](#한계-및-개선-방향)
8. [참고 자료](#참고-자료)

---

## 프로젝트 개요
- **목표**: 겨울철 도로 결빙으로 인한 교통·보행 사고를 사전에 예방하기 위해, 응급의료 접근성 및 고령층 유동인구가 밀집한 위험 지역을 과학적으로 분석하여 우선 설치 도로를 제시합니다.
- **주요 대상**: 의료 취약 지역, 60세 이상 유동인구 밀집 지역
- **성과 기대**: 사고 감소, 민원 해소, 예산 효율화

---

## 주요 분석 흐름
1. **1차 필터링 (500m 격자 단위)**
   - 응급의료시설 접근성 하위 50% 격자
   - 60세 이상 유동인구 상위 50% 격자
   - 결빙 취약 기후 상위 50% 격자
   - 최대 경사도 상위 50% 격자

2. **2차 분석 (도로별 가점 요소)**
   - 24시간 음영지 포함 여부
   - 버스 노선 경유 여부
   - 과거 결빙 사고 이력
   - 이동약자 보호구역 포함 여부
   - 제설 취약 구간(도로 폭 ≤ 8m)
   - 굴착 제한 미적용 여부

3. **우선 설치 후보 선정**
   - 총점 ≥ 4: 우선 설치 도로
   - 총점 = 3: 설치 필요 도로

4. **예산 산정 및 타당성 검토**
   - 과거 사례 공사 단가(원/m) 적용
   - 평균·최소·최대 비용 범위 제시

---

## 디렉토리 구조

```text
...
.gitignore                            # Git ignore 설정파일
README.md                             # 프로젝트 소개 및 실행 방법
requirements.txt                      # Python 의존성 목록

├── data/                             # 원본·가공 GIS 자료
├── docs/                             # 기획안·발표 자료·보고서
├── scripts/
├── src/                              # 분석 코드 모음
│   ├── initial_filtering/            # 1차 필터링 관련 코드
│   │   ├── collect_weather_data_from_api.py
│   │   ├── collect_bus_routes.py
│   │   ├── create_500m_grid.py
│   │   └── slope_extraction.py
│   └── road_scoring/                 # 2차 도로별 가점 요소 분석 코드
│       ├── accident_history_analysis/      # 사고 이력 분석 모듈
│       ├── excavation_roads/               # 굴착 제한 도로 정보 모듈
│       ├── existing_heated_pavement/       # 기존 열선 포장 구역 모듈
│       ├── common_basemap/                 # 기본 배경지도 레이어 모듈
│       ├── snow_vulnerability/             # 제설 취약성 분석 모듈
│       ├── shading_analysis/               # 음영지(그림자) 분석 모듈
│       ├── slope/                          # 경사도 계산 모듈
│       └── bus_routes/                     # 버스 노선 데이터 및 시각화
├── intermediate_results/             # 중간 산출물 (정리 용도)
└── final_results/                    # 최종 QGIS 프로젝트 및 산출물
````

---

## 설치 및 실행 방법

1. 의존성 설치

   ```bash
   pip install -r requirements.txt
   ```
2. 1차 필터링 실행

   ```bash
   python src/initial_filtering/data_collection/collect_weather_data_from_api.py
   python src/initial_filtering/data_collection/collect_bus_routes.py
   python src/initial_filtering/preprocessing/create_500m_grid.py
   python src/initial_filtering/preprocessing/slope_extraction.py
   ```
3. 2차 분석 및 시각화 실행

   ```bash
   python src/road_scoring/analysis/scoring.py
   python src/road_scoring/visualization/freezing_visualization.py
   ```
4. 최종 결과 확인

   * QGIS 프로젝트: `final_results/final_analysis.qgz`
   * 우선 설치 도로: `final_results/final_selected_roads.gpkg`

---

## QGIS 활용 시 권장 사항

* 데이터 폴더 내 gpkg 파일 시행 & style 폴더 내 수동으로 QML 스타일 불러올 것

1. 레이어에서 → 마우스 우클릭 → 속성 (가장 아래쪽 메뉴, 속성(P)...) 들어가기
2. 속성 창이 뜨면 → 좌측에서 스타일 탭 클릭
3. 오른쪽 하단에 불러오기 (Load Style) 버튼 있음
4. 여기서 QML 파일을 선택해서 불러오면 바로 적용됩니다!
5. 적용되면 스타일이 바로 덮어씌워집니다.

---

## 모듈별 설명

* **src/initial\_filtering/data\_collection/**: 기상청 API, 버스노선 등 원본 데이터 수집 스크립트
* **src/initial\_filtering/preprocessing/**: 500m 격자 생성, 경사도 계산 등 전처리 모듈
* **src/road\_scoring/analysis/**: 가점 요소 집계 및 점수 계산 로직
* **src/road\_scoring/visualization/**: 위험도 지도 및 차트 생성 모듈
* **src/road\_scoring/sql/**: 결빙 판정 SQL 쿼리 파일

---

## 한계 및 개선 방향

* 기상관측소 기반 온도로 인한 도로별 정확도 부족
* 자동화 스크립트 보강 필요 (버스노선·보호구역 시각화)
* IoT 센서 연동을 통한 실시간 모니터링 권장
* 추가 요소(수목 음영, 제설 이력) 반영 확대

---

## 참고 자료

* Won et al. (2024), Jang & Park (2023)
* 기상청 API, 서울열린데이터광장, 국토정보플랫폼
* QGIS, Python, Folium, Kakao Geocoding API
