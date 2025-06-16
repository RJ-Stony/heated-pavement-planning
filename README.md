# ❄️ 보행 취약 계층 보호 및 제설 사각지대 해소를 위한 열선 설치 입지 분석

본 프로젝트는 겨울철 결빙으로 인한 보행자 사고를 줄이기 위해 도심 내 열선 포장 설치 후보지를 과학적으로 선정하는 과정을 다룹니다. 의료 접근성이 낮은 지역과 고령층 거주 지역에서 발생하는 안전 사각지대를 해소하고자 기획되었습니다.

## 1. 문제 인식 및 분석 목적
- **배경**: 겨울철 도로 결빙으로 인한 교통·보행 사고가 반복되고 있으며, 피해는 의료 취약 지역과 고령층에 집중되는 경향이 있습니다.
- **목표**: 합리적이고 수용성 높은 열선 설치 정책을 수립하기 위해 위험 지역을 선별하고 우선 설치 도로를 제시합니다.

분석 흐름은 다음과 같습니다.
1. **1차 필터링** – 500m 격자를 기준으로 안전·환경 지표가 모두 높은 지역을 추출합니다.
2. **2차 분석** – 선별된 격자 내 도로를 대상으로 버스 노선 경유 여부 등 6가지 가점 요소를 적용하여 도로별 점수를 부여합니다.
3. **우선 설치 도로 선정** – 4점 이상 도로는 "우선 설치", 3점 도로는 "설치 필요"로 분류하여 사례와 함께 제시합니다.
4. **예산 산정 및 정책 검토** – 과거 사례 단가를 기반으로 총 사업비를 추정하고 정책 타당성을 평가합니다.

## 2. 저장소 구조
```
├── data/                     # 원본·가공 GIS 자료
│   ├── raw/                  # 수집한 원본 shapefile, txt 등
│   └── processed/            # 분석에 사용한 가공 데이터
├── src/
│   ├── data_collection/      # 기상청·버스노선 등 데이터 수집 스크립트
│   ├── preprocessing/        # 격자 생성, 경사도 추출 등 전처리 모듈
│   ├── analysis/             # 접근성·결빙 분석 및 점수화 스크립트
│   ├── visualization/        # 위험도 지도 등 시각화 모듈
│   └── sql/                  # 결빙 판정 SQL 쿼리
├── final_results/            # QGIS 프로젝트와 최종 산출물
├── docs/                     # 기획안·발표 자료·분석 보고서
└── requirements.txt          # 파이썬 의존성 목록
```

주요 스크립트 예시는 다음과 같습니다.
- `src/data_collection/collect_weather_data_from_api.py` – 기상청 API를 활용한 날씨 데이터 수집
- `src/preprocessing/create_500m_grid_centroids.py` – 500m 격자 생성
- `src/preprocessing/slope_extraction.py` – DEM 기반 경사도 계산
- `src/analysis/scoring.py` – 도로별 가점 요소 집계 및 점수 계산
- `src/sql/freezing_detection_algorithm.sql` – 기상 데이터로 결빙 여부 판정
- `src/visualization/freezing_visualization.py` – 결빙 위험 지도 시각화

## 3. 실행 방법
1. 필수 패키지를 설치합니다.
   ```bash
   pip install -r requirements.txt
   ```
2. `src/data_collection` 의 스크립트를 실행해 날씨·버스 노선 등 데이터를 수집합니다.
3. `src/preprocessing` 모듈로 격자 생성과 경사도 추출 등 전처리를 수행합니다.
4. `src/analysis` 의 스크립트를 통해 접근성 평가와 결빙 판단, 도로 점수화를 진행합니다.
5. `src/visualization` 의 스크립트로 위험 지도와 최종 후보 도로를 시각화합니다.
6. 최종 결과(`final_results/`)에서 QGIS 프로젝트(`final_analysis.qgz`)와 선택 도로(`final_selected_roads.gpkg`)를 확인합니다.

## 4. 한계와 향후 개선
- 기상 관측소 기반 온도를 사용하여 도로별 정확도가 다소 떨어질 수 있습니다.
- 버스 노선 및 보호구역 시각화 자동화가 미흡하므로 향후 개선이 필요합니다.
- IoT 센서 기반 실시간 계측과 보행자 중심 분석을 추가하여 정밀도를 높일 것을 권장합니다.

## 5. 참고자료 및 데이터 출처
- Won et al. (2024), Jang & Park (2023) 등 관련 논문
- 기상청 API, 국토정보플랫폼, 서울 열린 데이터 광장, 광진구청 제공 자료
- QGIS, Python, Kakao Geocoding API 등
