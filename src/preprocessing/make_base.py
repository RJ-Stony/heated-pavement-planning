import geopandas as gpd
import matplotlib.pyplot as plt
import fiona

# -------------------------------
# 1. 파일 경로 설정
# -------------------------------
shp_boundary = "./shp/overlap/TN_SIGNGU_BNDRY.shp"
shp_road = "./shp/overlap/N3A_A0010000.shp"
gpkg_path = "./shp/overlap/garim_role.gpkg"

# -------------------------------
# 2. SHP 파일 불러오기
# -------------------------------
gdf_boundary = gpd.read_file(shp_boundary)
if gdf_boundary.crs is None:
    gdf_boundary.set_crs(epsg=5179, inplace=True)
gdf_boundary = gdf_boundary.to_crs(epsg=3857)

gdf_road = gpd.read_file(shp_road)
if gdf_road.crs is None:
    gdf_road.set_crs(epsg=5179, inplace=True)
gdf_road = gdf_road.to_crs(epsg=3857)

# -------------------------------
# 3. GPKG 레이어 불러오기
# -------------------------------
layers = fiona.listlayers(gpkg_path)
gdf_layers = {
    layer: gpd.read_file(gpkg_path, layer=layer).to_crs(epsg=3857)
    for layer in layers
}

# -------------------------------
# 4. 시각화
# -------------------------------
# 시각화 시작
fig, ax = plt.subplots(figsize=(12, 12))

# (1) 도로망: 먼저 깔기 (가장 아래)
gdf_road.plot(ax=ax, facecolor="#e8f5e9", edgecolor="#000000", linewidth=1.5, label="도로망")

# (2) 경계선: 중간
gdf_boundary.plot(ax=ax, facecolor="none", edgecolor="#2c8949", linewidth=3, label="광진구 경계")

# ✅ (3) GPKG 면: 가장 위로 올라오게 마지막에 그리기
for gdf in gdf_layers.values():
    gdf.plot(ax=ax, facecolor="#e8e8e8", edgecolor="none", alpha=1, label="GPKG 면")

# 스타일 마무리
plt.title("Base Layer", fontsize=15)
plt.axis("equal")
plt.tight_layout()
plt.legend()
plt.show()
