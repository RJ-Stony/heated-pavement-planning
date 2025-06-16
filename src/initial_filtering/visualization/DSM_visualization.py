import rasterio
import numpy as np
import matplotlib.pyplot as plt
import math
from pyproj import Transformer
import geopandas as gpd
import contextily as ctx
from rasterio.features import geometry_mask

########################################
# 1. DSM 파일 읽고 Hillshade 계산
########################################
dsm_path = "DSM_output.tif"  # DSM 파일 경로
with rasterio.open(dsm_path) as src:
    dsm = src.read(1).astype(np.float32)
    transform = src.transform      # 예: EPSG:5174
    crs = src.crs
    resolution = transform.a       # 가로 해상도 (세로도 동일)
    width = src.width
    height = src.height

# DSM의 기울기와 방향 계산
dy, dx = np.gradient(dsm, resolution)
slope = np.arctan(np.sqrt(dx**2 + dy**2))  # radian 단위
aspect = np.arctan2(dy, -dx)               # radian 단위
aspect = np.where(aspect < 0, 2*np.pi + aspect, aspect)

# 태양 고도 및 방위각 (2월 20일 겨울철 정오 12시 기준 수동 입력 예시)
sun_alt_deg = 40   # degree
sun_az_deg = 180   # degree
sun_alt_rad = math.radians(sun_alt_deg)
sun_az_rad  = math.radians(sun_az_deg)

# Hillshade 공식 적용
hillshade = 255.0 * ( np.cos(sun_alt_rad) * np.cos(slope) +
                      np.sin(sun_alt_rad) * np.sin(slope) * np.cos(sun_az_rad - aspect) )
hillshade = np.clip(hillshade, 0, 255)

########################################
# 2. 광진구 격자(100m격자) Shapefile 읽기 및 CRS 통일
########################################
grid_shp = "100m격자.shp"  # 격자 파일 경로 (본인 경로에 맞게 수정)
grid = gpd.read_file(grid_shp)
# DEM/DSM와 같은 좌표계가 아니라면 변환 (예: DEM이 EPSG:5174일 때)
if grid.crs != crs:
    grid = grid.to_crs(crs)

########################################
# 3. 각 격자 셀에 대해 평균 Hillshade 계산하기
########################################
avg_hillshade_list = []
for geom in grid.geometry:
    # geometry_mask: 해당 격자 영역을 True로 마스킹 (invert=True → 격자 영역을 선택)
    mask_arr = geometry_mask([geom], out_shape=hillshade.shape, transform=transform, invert=True)
    # 해당 영역의 Hillshade 값을 추출
    values = hillshade[mask_arr]
    if values.size == 0:
        avg = np.nan
    else:
        avg = np.nanmean(values)
    avg_hillshade_list.append(avg)

grid["avg_hillshade"] = avg_hillshade_list
print("각 격자 셀의 평균 Hillshade 값 계산 완료.")

########################################
# 4. 결과 시각화 (EPSG:3854 → EPSG:3857로 변환하여 지도 배경과 함께)
########################################
# 우선, 광진구 격자 데이터를 EPSG:3857로 재투영하여 contextily 배경지도를 사용할 수 있게 함
grid_3857 = grid.to_crs(epsg=3857)

fig, ax = plt.subplots(figsize=(12, 12))
# 격자 셀의 평균 Hillshade 값을 컬러로 표현 (컬러맵: 예를 들면 viridis)
grid_3857.plot(column="avg_hillshade", cmap="viridis", linewidth=0.5, edgecolor="black",
               legend=True, ax=ax, legend_kwds={"label": "평균 Hillshade", "orientation": "vertical"})

ctx.add_basemap(ax, source=ctx.providers.OpenStreetMap.Mapnik, crs=grid_3857.crs)
ax.set_title("광진구 음영(결빙 위험) 정도 (평균 Hillshade) - 100m 격자")
ax.set_axis_off()
plt.tight_layout()
plt.show()





