# ❄️ 제설 사각지대 해소를 위한 열선 설치 입지 분석

도심 내 겨울철 결빙 사고를 예방하고, 의료·보행 취약 지역의 안전 사각지대를 줄이기 위해 과학적 근거 기반으로 열선 설치 후보지를 선정하는 프로젝트입니다.

---

## 📌 목차
1. [프로젝트 개요](#프로젝트-개요)
2. [주요 분석 흐름](#주요-분석-흐름)
3. [디렉토리 구조](#디렉토리-구조)
4. [설치 및 실행 방법](#설치-및-실행-방법)
5. [모듈별 설명](#모듈별-설명)
6. [한계 및 개선 방향](#한계-및-개선-방향)
7. [참고 자료](#참고-자료)

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
   다음 6가지 요소 충족 시 1점 부여 (0~6점)
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
   - 지역별 과거 공사 단가(원/m) 적용
   - 평균·최소·최대 비용 범위 제시

---

## 디렉토리 구조

```text
...
├── data/                     # 원본·가공 GIS 자료
│   ├── raw/                  # 원본 shapefile, API 결과 등
│   └── processed/            # 분석용 가공 데이터
├── src/
│   ├── data_collection/      # 기상·버스노선 등 수집 스크립트
│   ├── preprocessing/        # 격자 생성, 경사도 추출 모듈
│   ├── analysis/             # 접근성·결빙 분석 및 점수화 스크립트
│   ├── visualization/        # 지도 시각화 모듈
│   └── sql/                  # 결빙 판정 SQL 쿼리
├── final_results/            # 최종 QGIS 프로젝트 및 산출물
├── docs/                     # 기획안·발표 자료·보고서
└── requirements.txt          # Python 의존성 목록
````

---

## 설치 및 실행 방법

1. 리포지토리 클론

   ```bash
   git clone https://github.com/your-org/freezing-heatmap.git
   cd freezing-heatmap
   ```
2. 의존성 설치

   ```bash
   pip install -r requirements.txt
   ```
3. 데이터 수집

   ```bash
   # 기상 데이터 수집
   python src/data_collection/collect_weather_data_from_api.py
   # 버스 노선 정보 수집
   python src/data_collection/collect_bus_routes.py
   ```
4. 전처리 및 분석

   ```bash
   # 격자 생성 및 경사도 추출
   python src/preprocessing/create_500m_grid.py
   python src/preprocessing/slope_extraction.py

   # 접근성 평가 및 결빙 판단
   python src/analysis/scoring.py
   ```
5. 시각화

   ```bash
   python src/visualization/freezing_visualization.py
   ```
6. 결과 확인

   * `final_results/final_analysis.qgz` (QGIS 프로젝트)
   * `final_results/final_selected_roads.gpkg` (우선 설치 도로)

---

## 모듈별 설명

* **data\_collection/**: 공공 API 및 스크래핑으로 원본 데이터를 수집합니다.
* **preprocessing/**: 공간 격자 생성, DEM 기반 경사도 계산 등 전처리를 수행합니다.
* **analysis/**: 필터링, 가점 요소 적용, 점수화 로직을 포함합니다.
* **visualization/**: Folium·Matplotlib 기반 지도 및 차트 생성 모듈입니다.
* **sql/**: PostgreSQL에서 결빙 여부를 판정하는 쿼리를 관리합니다.

---

## 한계 및 개선 방향

* **도로별 온도 정확도**: 기상관측소 관측값 사용으로 로컬 마이크로 클라이밋 반영 미흡
* **자동화 보강**: 버스 노선·보호구역 시각화 자동화 스크립트 추가 필요
* **실시간 모니터링**: IoT 센서 연동 및 실시간 계측 데이터 활용 권장
* **추가 요소 반영**: 수목·건물 음영·제설 이력 등 세부 인자 확장

---

## 참고 자료

* 논문: Won et al. (2024), Jang & Park (2023)
* 데이터: 기상청 API, 서울열린데이터광장, 국토정보플랫폼
* 도구: QGIS, Python, Folium, Kakao Geocoding API

```
