import numpy as np
import rasterio
from rasterio.plot import plotting_extent
from rasterstats import zonal_stats
import geopandas as gpd
import koreanize_matplotlib
import matplotlib.pyplot as plt

# 파일 경로 설정 (성동구 2022 DEM 자료와 100m 격자 shapefile)
dem_path = '37705.img'             # 성동구 2022 DEM 자료
grid_shp_path = '100m격자.shp'       # 광진구에 해당하는 100m 격자 shapefile
slope_raster_path = 'slope.tif'      # 계산된 기울기 레스터 저장 경로

# 1. DEM으로부터 기울기(경사도) 계산하기
with rasterio.open(dem_path) as src:
    dem = src.read(1, masked=True)
    transform = src.transform
    crs = src.crs
    resolution = src.res[0]
    
    # x, y 방향 기울기 계산 (numpy.gradient 이용)
    dzdx, dzdy = np.gradient(dem, resolution, resolution)
    # 각 픽셀의 기울기를 계산 (라디안 단위 → 도 단위 변환)
    slope_rad = np.arctan(np.sqrt(dzdx**2 + dzdy**2))
    slope_deg = np.degrees(slope_rad)

# 2. 계산된 기울기 데이터를 GeoTIFF 파일로 저장
with rasterio.open(
    slope_raster_path, 'w',
    driver='GTiff',
    height=slope_deg.shape[0],
    width=slope_deg.shape[1],
    count=1,
    dtype=slope_deg.dtype,
    crs=crs,
    transform=transform
) as dst:
    dst.write(slope_deg, 1)

print("DEM 자료로부터 기울기(경사도) 계산 완료 및 파일 저장됨.")

# 3. 100m 격자별 최대 경사도 계산
grid = gpd.read_file(grid_shp_path)
stats = zonal_stats(grid_shp_path, slope_raster_path, stats=['max'])
grid['max_slope'] = [s['max'] for s in stats]

print("각 격자별 최대 경사도 계산 완료.")
print(grid[['max_slope']].head())

# 4. 시각화: 격자별 최대 경사도 choropleth 지도 생성
fig, ax = plt.subplots(figsize=(10, 10))
grid.plot(column='max_slope', ax=ax, cmap='viridis', legend=True, 
          edgecolor='black', linewidth=0.5)
ax.set_title("광진구 100m 격자별 최대 경사도")
ax.set_xlabel("X 좌표")
ax.set_ylabel("Y 좌표")
plt.show()

# 5. CSV 내보내기 전에 gid 인코딩 수정  
# (이미 grid 객체에 max_slope 컬럼 및 기타 정보가 있으므로 이를 그대로 사용)
if 'gid' in grid.columns:
    def fix_gid(x):
        try:
            # 경우에 따라 'latin1' 대신 다른 인코딩을 시도할 수 있음
            return x.encode('latin1').decode('cp949')
        except Exception:
            return x
    grid['gid'] = grid['gid'].apply(fix_gid)

# 6. "max_slope"를 기준으로 순위(rank) 컬럼 생성 (높은 경사도에 낮은 순위 번호)
grid['rank'] = grid['max_slope'].rank(method='min', ascending=False)

# 7. geometry 컬럼 제거 후 DataFrame 변환
grid_df = grid.drop(columns='geometry')

# 8. 전체 데이터 CSV 저장 (경사도 및 순위 포함)
csv_all = 'grid_with_slope_and_rank_fixed.csv'
grid_df.to_csv('grid_with_slope_and_rank_fixed.csv', index=False, encoding='utf-8-sig')
print('전체 격자 데이터 저장')

# 9. 상위 50% 데이터(경사도 높은 순) 저장
n_total = len(grid_df)
top_half = grid_df.sort_values(by='max_slope', ascending=False).head(n_total // 2)
csv_top = 'top_half_slope_fixed.csv'
top_half.to_csv('top_half_slope_fixed.csv', index=False, encoding='utf-8-sig')
print("상위 50% 격자 데이터 저장되었습니다.")
