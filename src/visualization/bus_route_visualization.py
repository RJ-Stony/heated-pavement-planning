import geopandas as gpd
import matplotlib.pyplot as plt
import contextily as ctx
import osmnx as ox
import koreanize_matplotlib
import pandas as pd

# -------------------------------
# 1. 도로명 리스트 추출
# -------------------------------
df_master = pd.read_csv("./광진구_도로명_주소마스터.csv", encoding="utf-8-sig")
safe_road_names = df_master["도로명"].dropna().unique().tolist()

# -------------------------------
# 2. 광진구 도로망 불러오기 (OSM 기반)
# -------------------------------
gdf = gpd.read_file("./shp/LARD_ADM_SECT_SGG_11_202502.shp", encoding="cp949")
gwangjin = gdf[gdf['SGG_NM'] == '광진구'].copy().to_crs(epsg=4326)

polygon = gwangjin.geometry.unary_union
graph = ox.graph_from_polygon(polygon, network_type="drive")
edges = ox.graph_to_gdfs(graph, nodes=False, edges=True).to_crs(epsg=3857)

# -------------------------------
# 3. 격자 (보호구역) 불러오기
# -------------------------------
filtered_gdf = gpd.read_file("./shp/overlap_final.shp").to_crs(epsg=3857)

# -------------------------------
# 4. 도로명 처리 + 보호구역 내부 도로만 필터링
# -------------------------------
# 도로명 통합 (리스트 → 문자열)
edges["road_name"] = edges["name"].apply(
    lambda x: ", ".join(x) if isinstance(x, list) else x
)

# 보호구역 격자 내 도로만 추출
edges_in_highlighted = gpd.overlay(edges, filtered_gdf, how="intersection")

# 도로명 조건 일치하는 것만 추출
safe_edges = edges_in_highlighted[edges_in_highlighted["road_name"].apply(
    lambda name: any(rd in name for rd in safe_road_names) if isinstance(name, str) else False
)]

# -------------------------------
# 5. 시각화
# -------------------------------
fig, ax = plt.subplots(figsize=(12, 12))

# 전체 도로망 (배경)
edges.plot(ax=ax, color="black", linewidth=0.5, alpha=0.4, label="전체 도로망")

# 보호구역 내 실제 도로명 매칭 도로 강조
safe_edges.plot(ax=ax, color="#d62828", linewidth=2.5, alpha=0.95, label="필터링 지역 내 버스 노선")

# 지도 타일
ctx.add_basemap(ax, source=ctx.providers.OpenStreetMap.Mapnik)

# 마무리
plt.title(f"광진구 내 버스 노선 (총 {len(safe_edges)}개)", fontsize=14)
plt.legend()
plt.axis("equal")
plt.tight_layout()
plt.show()
