import geopandas as gpd
import matplotlib.pyplot as plt
import contextily as ctx
import fiona
import pandas as pd
import osmnx as ox
import koreanize_matplotlib

# -------------------------------
# 1. Base Layer 관련 파일 불러오기
# -------------------------------
shp_boundary = "./shp/overlap/TN_SIGNGU_BNDRY.shp"
shp_road = "./shp/overlap/N3A_A0010000.shp"
gpkg_path = "./shp/overlap/garim_role.gpkg"

gdf_boundary = gpd.read_file(shp_boundary).to_crs(epsg=3857)
gdf_road = gpd.read_file(shp_road).to_crs(epsg=3857)
layers = fiona.listlayers(gpkg_path)
gdf_layers = {
    layer: gpd.read_file(gpkg_path, layer=layer).to_crs(epsg=3857)
    for layer in layers
}

# -------------------------------
# 2. 도로명 리스트 + OSM 도로 불러오기
# -------------------------------
df_master = pd.read_csv("./data/광진구_도로명_주소마스터.csv", encoding="utf-8-sig")
safe_road_names = df_master["도로명"].dropna().unique().tolist()

gdf = gpd.read_file("./shp/LARD_ADM_SECT_SGG_11_202502.shp", encoding='cp949')
gwangjin = gdf[gdf['SGG_NM'] == '광진구'].copy().to_crs(epsg=4326)
polygon = gwangjin.geometry.unary_union
graph = ox.graph_from_polygon(polygon, network_type="drive")
edges = ox.graph_to_gdfs(graph, nodes=False, edges=True).to_crs(epsg=3857)

# -------------------------------
# 3. 격자 및 도로 필터링
# -------------------------------
filtered_gdf = gpd.read_file("./shp/overlap_final.shp").to_crs(epsg=3857)
edges["road_name"] = edges["name"].apply(lambda x: ", ".join(x) if isinstance(x, list) else x)
edges_in_highlighted = gpd.overlay(edges, filtered_gdf, how="intersection")
safe_edges = edges_in_highlighted[edges_in_highlighted["road_name"].apply(
    lambda name: any(rd in name for rd in safe_road_names) if isinstance(name, str) else False
)]

# -------------------------------
# 4. 시각화 (Base Layer + 버스노선 도로만)
# -------------------------------
fig, ax = plt.subplots(figsize=(12, 12))

# (1) 도로망 배경
gdf_road.plot(ax=ax, facecolor="#e8f5e9", edgecolor="#000000", linewidth=1)

# (2) 경계선
gdf_boundary.plot(ax=ax, facecolor="none", edgecolor="#2c8949", linewidth=3)

# (3) GPKG 면
for gdf in gdf_layers.values():
    gdf.plot(ax=ax, facecolor="#e8e8e8", edgecolor="none", alpha=1)

# ✅ (4) 보호구역 내 버스 노선 도로 강조
safe_edges.plot(ax=ax, color="#F3722C", linewidth=2.5, alpha=0.95, label="선별된 버스 노선 도로")

# -------------------------------
# 5. 선별된 버스 노선 도로 저장 (road_name + geometry만)
# -------------------------------
output_path = "./output/bus_route.csv"

# road_name과 geometry만 선택
safe_edges[["road_name", "geometry"]].to_csv(output_path, index=False, encoding="utf-8-sig")

# 마무리
plt.title("선별된 버스 노선 도로", fontsize=14)
plt.legend()
plt.axis("equal")
plt.tight_layout()
plt.show()

