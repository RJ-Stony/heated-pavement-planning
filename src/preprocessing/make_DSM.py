import geopandas as gpd
import rasterio
from rasterio.features import rasterize
import numpy as np

# 1. DEM 파일 불러오기
dem_path = "output_dem_clip.tif"  # DEM 파일 경로 (본인의 경로에 맞게 수정)
with rasterio.open(dem_path) as dem_src:
    dem = dem_src.read(1).astype(np.float32)  # DEM 데이터를 float32 형식으로 읽음
    dem_transform = dem_src.transform        # 공간 변환 행렬 (geotransform)
    dem_crs = dem_src.crs                    # 좌표계 (예: EPSG:5174)
    dem_profile = dem_src.profile            # 메타데이터 (이후 DSM 저장에 사용)
    dem_shape = dem.shape                    # (행, 열)

print(f"DEM 읽기 완료: shape={dem_shape}, CRS={dem_crs}")

# 2. 건물 데이터 불러오기 및 DEM과 동일 CRS로 변환
building_shp = "F_FAC_BUILDING_11215_202503.shp"  # 건물 shapefile 경로
buildings = gpd.read_file(building_shp)
# DEM 파일의 좌표계에 맞추기 (대소문자 구분 없이 변환)
buildings = buildings.to_crs(dem_crs)
print(f"건물 데이터 읽기 완료: 건물 개수={len(buildings)}")

# 3. 건물 높이 래스터화
# 각 건물 폴리곤에서 "HEIGHT" 컬럼 값을 value로 사용
# shapes: 제너레이터 형태로 (geometry, building_height) 튜플 생성
shapes = ((geom, height) for geom, height in zip(buildings.geometry, buildings["HEIGHT"]))

# rasterize()를 사용해서 건물 래스터 생성: 건물이 있는 픽셀은 해당 건물 높이, 없으면 0
building_raster = rasterize(
    shapes=shapes,
    out_shape=dem_shape,
    transform=dem_transform,
    fill=0,
    dtype=np.float32
)
print("건물 높이 래스터화 완료.")

# 4. DSM 생성: DSM = DEM + 건물 높이 래스터
# (건물이 없는 곳: building_raster 값은 0이므로 DEM 값 그대로)
dsm = dem + building_raster
print("DSM 생성 완료.")

# 5. DSM 저장하기
dsm_output_path = "DSM_output.tif"  # 저장할 DSM 파일 경로
# 기존 DEM의 profile을 업데이트 (자료형, 밴드 개수 지정)
dem_profile.update(dtype=rasterio.float32, count=1)
with rasterio.open(dsm_output_path, "w", **dem_profile) as dst:
    dst.write(dsm, 1)

print(f"DSM 파일이 저장되었습니다: {dsm_output_path}")
