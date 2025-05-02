import geopandas as gpd
import matplotlib.pyplot as plt
import contextily as ctx
import osmnx as ox
import koreanize_matplotlib
import pandas as pd

# -------------------------------
# 1. 도로명 리스트 추출 (from sorted_roads.csv)
# -------------------------------
df_sorted_roads = pd.read_csv("./data/sorted_roads.csv", encoding="euc-kr")
safe_road_names = df_sorted_roads["도로명"].dropna().unique().tolist()

# -------------------------------
# 2. 광진구 도로망 생성
# -------------------------------
gdf = gpd.read_file("./shp/LARD_ADM_SECT_SGG_11_202502.shp", encoding="cp949")
gwangjin = gdf[gdf['SGG_NM'] == '광진구'].copy().to_crs(epsg=4326)

polygon = gwangjin.geometry.unary_union
graph = ox.graph_from_polygon(polygon, network_type="drive")
edges = ox.graph_to_gdfs(graph, nodes=False, edges=True).to_crs(epsg=3857)

# -------------------------------
# 3. 보호구역 격자 불러오기
# -------------------------------
filtered_gdf = gpd.read_file("./shp/overlap_final.shp").to_crs(epsg=3857)

# -------------------------------
# 4. 도로명 처리 + 조건 필터링
# -------------------------------
edges["road_name"] = edges["name"].apply(
    lambda x: ", ".join(x) if isinstance(x, list) else x
)

edges_in_highlighted = gpd.overlay(edges, filtered_gdf, how="intersection")

safe_edges = edges_in_highlighted[edges_in_highlighted["road_name"].apply(
    lambda name: any(rd in name for rd in safe_road_names) if isinstance(name, str) else False
)]

# -------------------------------
# 5. 시각화
# -------------------------------
fig, ax = plt.subplots(figsize=(12, 12))

# 전체 도로망 (연하게)
edges.plot(ax=ax, color="black", linewidth=0.5, alpha=0.4, label="전체 도로망")

# 보호구역 내 실제 도로명 일치한 도로
safe_edges.plot(ax=ax, color="#d62828", linewidth=2.5, alpha=0.95, label="도로 폭 필터링")

ctx.add_basemap(ax, source=ctx.providers.OpenStreetMap.Mapnik)

plt.title(f"광진구 내 도로 폭으로 선별 (총 {len(safe_edges)}개)", fontsize=14)
plt.legend()
plt.axis("equal")
plt.tight_layout()
plt.show()
