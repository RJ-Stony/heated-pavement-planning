import netCDF4 as nc
import numpy as np
import geopandas as gpd
from shapely.geometry import Point
import koreanize_matplotlib
import matplotlib.pyplot as plt

#############################
# 1. 100m → 500m 격자 변환 및 중심점 추출
#############################

# (1) 100m 격자 읽기
gdf_100 = gpd.read_file('100m.shp')
print("100m 격자 데이터 예시:")
print(gdf_100.head())
print("CRS:", gdf_100.crs)

# (2) 각 셀 중심 좌표 계산 (좌표계가 미터 단위라고 가정)
gdf_100['centroid_x'] = gdf_100.geometry.centroid.x
gdf_100['centroid_y'] = gdf_100.geometry.centroid.y

# (3) 500m 격자 인덱스 생성
gdf_100['grid_x'] = (gdf_100['centroid_x'] // 500).astype(int)
gdf_100['grid_y'] = (gdf_100['centroid_y'] // 500).astype(int)

# (4) 동일한 500m 격자로 dissolve
gdf_500 = gdf_100.dissolve(by=['grid_x', 'grid_y'])

# (5) 500m 폴리곤들의 중심점(centroid) 추출
gdf_500_centers = gdf_500.copy()
gdf_500_centers['geometry'] = gdf_500_centers.geometry.centroid
print("500m 격자 수:", len(gdf_500_centers))

#############################
# 2. API NetCDF 파일에서 중심점 추출
#############################

# (1) NetCDF 파일 열기
nc_file = './nc/sfc_grid_latlon.nc'
ds = nc.Dataset(nc_file)
print("NetCDF 변수 목록:", ds.variables.keys())

lon_api = ds.variables['lon'][:]  # 예: shape (2049, 2049)
lat_api = ds.variables['lat'][:]

print("API 격자 경도 범위:", np.min(lon_api), np.max(lon_api))
print("API 격자 위도 범위:", np.min(lat_api), np.max(lat_api))

# (2) 관심 영역(500m 격자 범위)에 해당하는 셀만 골라내기
#     우선 500m 격자의 전체 범위를 WGS84로 변환해서 min/max lon/lat을 구함
gdf_500_wgs84 = gdf_500.to_crs(epsg=4326)  # WGS84
minx, miny, maxx, maxy = gdf_500_wgs84.total_bounds

# NetCDF가 이미 WGS84(lon/lat)라 가정하고, 마스킹
mask = (
    (lon_api >= minx) & (lon_api <= maxx) &
    (lat_api >= miny) & (lat_api <= maxy)
)
indices = np.where(mask)
print("관심 영역 내 API 격자 셀 개수:", len(indices[0]))

# (3) API 격자 '점' 데이터 생성 (폴리곤 대신 중심점)
points_api = []
for i, j in zip(indices[0], indices[1]):
    points_api.append(Point(lon_api[i, j], lat_api[i, j]))

gdf_api_points = gpd.GeoDataFrame({'geometry': points_api}, crs="EPSG:4326")

#############################
# 3. 좌표계 맞추고 시각화 (점 vs. 점)
#############################

# (1) API 점들을 500m 격자의 CRS로 변환
target_crs = gdf_500.crs  # 예: EPSG:5179 등
gdf_api_points_local = gdf_api_points.to_crs(target_crs)

# (2) 500m 격자의 중심점은 이미 target_crs이므로 그대로 사용
gdf_500_points_local = gdf_500_centers  # 별칭

# (3) 시각화 (scatter plot 느낌으로 표시)
fig, ax = plt.subplots(figsize=(10, 10))

# API 격자 중심점 (빨간 점)
gdf_api_points_local.plot(
    ax=ax,
    marker='o',
    color='red',
    markersize=5,
    label='API Center Points'
)

# 500m 격자 중심점 (파란 점)
gdf_500_points_local.plot(
    ax=ax,
    marker='x',
    color='blue',
    markersize=5,
    label='500m Grid Center Points'
)

plt.legend()
plt.title("API 격자 중심점 vs. 100m→500m 격자 중심점 비교")
plt.xlabel("X (m)")
plt.ylabel("Y (m)")
plt.show()
