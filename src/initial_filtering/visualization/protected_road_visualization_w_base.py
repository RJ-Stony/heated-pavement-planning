import geopandas as gpd
import matplotlib.pyplot as plt
import pandas as pd
import fiona
import osmnx as ox
from shapely.geometry import Point
import contextily as ctx
import koreanize_matplotlib

# -------------------------------
# 1. Base Layer 관련 파일 불러오기
# -------------------------------
shp_boundary = "./shp/overlap/TN_SIGNGU_BNDRY.shp"
shp_road = "./shp/overlap/N3A_A0010000.shp"
gpkg_path = "./shp/overlap/garim_role.gpkg"

gdf_boundary = gpd.read_file(shp_boundary)
if gdf_boundary.crs is None:
    gdf_boundary.set_crs(epsg=5179, inplace=True)
gdf_boundary = gdf_boundary.to_crs(epsg=3857)

gdf_road = gpd.read_file(shp_road)
if gdf_road.crs is None:
    gdf_road.set_crs(epsg=5179, inplace=True)
gdf_road = gdf_road.to_crs(epsg=3857)

layers = fiona.listlayers(gpkg_path)
gdf_layers = {
    layer: gpd.read_file(gpkg_path, layer=layer).to_crs(epsg=3857)
    for layer in layers
}

# -------------------------------
# 2. 보호구역 내 도로 (safe_edges) 생성
# -------------------------------
gdf = gpd.read_file("./shp/LARD_ADM_SECT_SGG_11_202502.shp", encoding='cp949')
gwangjin = gdf[gdf['SGG_NM'] == '광진구'].copy().to_crs(epsg=4326)
polygon = gwangjin.geometry.unary_union
graph = ox.graph_from_polygon(polygon, network_type="drive")
edges = ox.graph_to_gdfs(graph, nodes=False, edges=True).to_crs(epsg=3857)

points = [
    (127.091743, 37.557558),
    (127.100496, 37.541105),
    (127.100646, 37.548106),
    (127.098655, 37.553036),
    (127.089106, 37.530348),
    (127.088346, 37.564860),
    (127.083542, 37.558158),
    (127.104934, 37.548403),
    (127.097621, 37.553968),
    (127.082961, 37.564937),
    (127.096317, 37.550054),
    (127.071287, 37.530952),
    (127.096383, 37.552830),
    (127.097188, 37.550597),
]
addr_gdf = gpd.GeoDataFrame(geometry=[Point(xy) for xy in points], crs="EPSG:4326").to_crs(epsg=3857)

gdf_all = gpd.read_file("./shp/100m_500m.shp")
if gdf_all.crs is None:
    gdf_all.set_crs(epsg=5181, inplace=True)
gdf_all = gdf_all.to_crs(epsg=3857)

filtered_gdf = gpd.read_file("./shp/overlap_final.shp").to_crs(epsg=3857)
filtered_gdf["score"] = 0

joined = gpd.sjoin(addr_gdf, filtered_gdf, how="inner", predicate="within")
idx_with_score = joined.index_right.unique()
filtered_gdf.loc[idx_with_score, "score"] = 1
highlighted_gdf = filtered_gdf[filtered_gdf["score"] == 1]

safe_road_names = [
    "긴고랑로36길", "아차산로70길", "광장로1길", "영화사로", "뚝섬로64길",
    "용마산로22길", "천호대로113길", "광장로7길", "긴고랑로13길", "자양로44길",
    "능동로4길", "자양로50길", "워커힐로"
]

edges["road_name"] = edges["name"].apply(lambda x: ", ".join(x) if isinstance(x, list) else x)
edges_in_highlighted = gpd.overlay(edges, highlighted_gdf, how="intersection")
safe_edges = edges_in_highlighted[edges_in_highlighted["road_name"].apply(
    lambda name: any(rd in name for rd in safe_road_names) if isinstance(name, str) else False
)]

# -------------------------------
# 3. 시각화 (Base Layer + Safe Roads)
# -------------------------------
fig, ax = plt.subplots(figsize=(12, 12))

# (1) 도로망 (가장 아래)
gdf_road.plot(ax=ax, facecolor="#e8f5e9", edgecolor="#000000", linewidth=1)

# (2) 광진구 경계선
gdf_boundary.plot(ax=ax, facecolor="none", edgecolor="#2c8949", linewidth=3)

# (3) GPKG 면 (그 위)
for gdf in gdf_layers.values():
    gdf.plot(ax=ax, facecolor="#e8e8e8", edgecolor="none", alpha=1)

# ✅ (4) 보호구역 내 강조 도로 (맨 위)
safe_edges.plot(ax=ax, color="#F9C74F", linewidth=3, alpha=0.95, label="선별된 보호 구역 도로")

# -------------------------------
# 4. safe_edges 저장 (road_name + geometry만)
# -------------------------------
output_path = "./output/protected_road.csv"

# 필요한 컬럼만 선택하여 저장
safe_edges[["road_name", "geometry"]].to_csv(output_path, index=False, encoding="utf-8-sig")

# 스타일 마무리
plt.title("선별된 보호 구역 도로", fontsize=15)
plt.axis("equal")
plt.tight_layout()
plt.legend()
plt.show()
