import geopandas as gpd
from shapely.geometry import box, Point
import matplotlib.pyplot as plt

# 1. 100m 격자 shp 파일 읽기
gdf_100m = gpd.read_file('100m.shp')

# 만약 현재 좌표계가 미터 단위가 아닌 경우 적절한 투영(projection)으로 변환 필요
# gdf_100m = gdf_100m.to_crs(epsg=####) 

# 2. 각 100m 셀의 중심점 계산 (경계가 정사각형인 경우 안전하게 사용 가능)
gdf_100m['centroid'] = gdf_100m.geometry.centroid

# 3. 500m 업스케일링을 위한 그룹화 ID 생성 
# (각 중심점의 x, y 좌표를 500으로 나눈 후 내림하여 다시 500을 곱하면 500m 단위의 그룹이 만들어짐)
gdf_100m['grid_x'] = (gdf_100m['centroid'].x // 500) * 500
gdf_100m['grid_y'] = (gdf_100m['centroid'].y // 500) * 500

# 4. 고유한 500m 격자 셀별로 그룹핑 (grid_x, grid_y의 조합)
grid_df = gdf_100m[['grid_x', 'grid_y']].drop_duplicates().reset_index(drop=True)

# 5. 각 500m 격자의 중심점 좌표 계산
# (500m 셀은 grid_x, grid_y가 왼쪽 하단 좌표이므로 +250을 하면 중심점이 됨)
grid_df['centroid_x'] = grid_df['grid_x'] + 250
grid_df['centroid_y'] = grid_df['grid_y'] + 250

# 6. 500m 셀의 폴리곤 생성 (왼쪽 하단에서 오른쪽 상단까지의 사각형)
grid_df['geometry'] = grid_df.apply(lambda row: box(row['grid_x'], row['grid_y'], row['grid_x']+500, row['grid_y']+500), axis=1)

# 7. GeoDataFrame 생성 (기존 shp의 좌표계 유지)
gdf_500m = gpd.GeoDataFrame(grid_df, geometry='geometry', crs=gdf_100m.crs)

# 8. 중심점을 Point 객체로 저장하여 별도 GeoDataFrame 생성
gdf_500m['centroid_point'] = gdf_500m.apply(lambda row: Point(row['centroid_x'], row['centroid_y']), axis=1)
gdf_centroid = gpd.GeoDataFrame(gdf_500m[['grid_x', 'grid_y']], geometry=gdf_500m['centroid_point'], crs=gdf_500m.crs)

# 9. 경위도 좌표(일반적으로 EPSG:4326)로 변환
gdf_500m = gdf_500m.to_crs(epsg=4326)
gdf_centroid = gdf_centroid.to_crs(epsg=4326)

# 10. 중심점의 경도, 위도 추출 및 데이터프레임 생성
gdf_centroid['lon'] = gdf_centroid.geometry.x
gdf_centroid['lat'] = gdf_centroid.geometry.y

df_result = gdf_centroid[['grid_x', 'grid_y', 'lon', 'lat']]
df_result.to_csv('500m_grid_centroids.csv', index=False)

# 11. 500m 격자 시각화
fig, ax = plt.subplots(figsize=(10, 10))
gdf_500m.boundary.plot(ax=ax, edgecolor='black')  # 경계선만 그림
ax.set_title("500m Grid Visualization")
ax.set_xlabel("Longitude")
ax.set_ylabel("Latitude")
plt.show()
