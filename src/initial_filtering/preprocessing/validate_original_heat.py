import pandas as pd
import geopandas as gpd
import osmnx as ox

# -------------------------------
# 1. 도로열선 데이터 로딩
# -------------------------------
df_heat = pd.read_csv("./data/서울특별시 광진구 도로열선.csv", encoding="euc-kr")
df_heat.columns = df_heat.columns.str.strip()  # 공백 제거
heat_road_names = df_heat["도로명"].dropna().unique().tolist()

# -------------------------------
# 2. 광진구 도로망 (OSM)
# -------------------------------
gdf = gpd.read_file("./shp/LARD_ADM_SECT_SGG_11_202502.shp", encoding="cp949")
gwangjin = gdf[gdf["SGG_NM"] == "광진구"].copy().to_crs(epsg=4326)

# 🔥 괄호 제거!
polygon = gwangjin.geometry.unary_union

graph = ox.graph_from_polygon(polygon, network_type="drive")
edges = ox.graph_to_gdfs(graph, nodes=False, edges=True).to_crs(epsg=3857)

# -------------------------------
# 3. 도로열선 필터링
# -------------------------------
matched = edges[edges["road_name"].apply(
    lambda name: any(n in name for n in heat_road_names) if isinstance(name, str) else False
)].copy()

# -------------------------------
# 4. 매칭 요약
# -------------------------------
matched_summary = (
    matched["road_name"]
    .value_counts()
    .reset_index()
)
matched_summary.columns = ["도로명", "Segment 수"]

print(matched_summary.columns.tolist())

# 정렬
matched_summary = matched_summary.sort_values("도로명")


