import pandas as pd
import geopandas as gpd
from shapely.geometry import Point
import koreanize_matplotlib  # 한글 폰트 사용 (설치되어 있다면)
import matplotlib.pyplot as plt

# --- 1. 데이터 로딩 ---
# (1) 결빙 건수 데이터 (컬럼: gid, total_count)
freezing_df = pd.read_csv('기후 격자별 결빙 건수 값.csv')

# (2) 전체 기상 데이터 (컬럼: gid, lon, lat 등)
weather_df = pd.read_csv('전체_기상_데이터.csv')
# gid별 첫 번째 행의 좌표를 추출하여 gid→(lon, lat) 매핑 생성 (중복 제거)
coord_df = weather_df.groupby('gid').first().reset_index()[['gid', 'lon', 'lat']]

# (3) 500m 격자 중심점 데이터 (컬럼: grid_x, grid_y 등; gid 없음)
centroids_df = pd.read_csv('500m_grid_centroids.csv')

# --- 2. gid 기준 결빙 건수에 좌표 추가 ---
# freezing_df와 coord_df를 gid 기준으로 병합하여 각 격자의 중심 좌표 확보
freezing_coord_df = pd.merge(freezing_df, coord_df, on='gid', how='left')
# freezing_coord_df에는 gid, total_count, lon, lat 정보가 포함됨

# --- 3. 좌표 기준으로 centroids_df와 병합 ---
# 여기서는 freezing_coord_df의 (lon, lat)와 centroids_df의 (grid_x, grid_y)가 동일하다고 가정
merged_df = pd.merge(freezing_coord_df, centroids_df, left_on=['lon', 'lat'], right_on=['grid_x', 'grid_y'], how='left')
# merged_df에 gid, total_count, lon, lat, grid_x, grid_y 등의 정보가 포함됨

# --- 4. GeoDataFrame 생성 (좌표계 변환 없이) ---
# centroids_df의 grid_x, grid_y를 사용하여 GeoDataFrame 생성 (EPSG:4326로 가정)
gdf_centroids = gpd.GeoDataFrame(
    merged_df,
    geometry=gpd.points_from_xy(merged_df['grid_x'], merged_df['grid_y']),
    crs='EPSG:4326'
)

# --- 5. 500m 격자 shapefile 불러오기 ---
gdf_shp = gpd.read_file('500m.shp')
# 여기서는 shapefile의 좌표계를 그대로 사용한다고 가정 (예: EPSG:4326)

# 좌표계 맞추기: gdf_centroids를 gdf_shp의 CRS로 변환
gdf_centroids = gdf_centroids.to_crs(gdf_shp.crs)

# --- 6. 공간 조인 (Spatial Join) ---
joined = gpd.sjoin(gdf_shp, gdf_centroids, how="left", predicate='contains')

# --- 7. 시각화 (좌표계 변환 없이) ---
fig, ax = plt.subplots(figsize=(12, 12))

# Choropleth 지도: 폴리곤을 total_count 값에 따라 색상으로 표시
joined.plot(
    column='total_count',
    cmap='coolwarm',
    legend=True,
    edgecolor='grey',
    linewidth=0.3,
    ax=ax
)

# 각 폴리곤 중앙에 결빙 건수 텍스트 라벨 추가
for idx, row in joined.iterrows():
    if pd.notnull(row['total_count']):
        centroid = row.geometry.centroid
        ax.text(centroid.x, centroid.y, str(int(row['total_count'])),
                ha='center', va='center', fontsize=8, color='black')

plt.title("500m 격자별 결빙 예측 건수 (좌표계 변환 없음)", fontsize=16)
plt.axis("off")
plt.tight_layout()
plt.show()
