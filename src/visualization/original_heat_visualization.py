import geopandas as gpd
import pandas as pd
import osmnx as ox
import fiona
import matplotlib.pyplot as plt
import koreanize_matplotlib
import os
import matplotlib.cm as cm

# -------------------------------
# [1] 데이터 준비 함수
# -------------------------------
def load_filtered_edges(target_road_name: str) -> gpd.GeoDataFrame:
    # 도로열선 도로명
    df_heat = pd.read_csv("./data/서울특별시 광진구 도로열선.csv", encoding="euc-kr")
    heat_road_names = df_heat["도로명"].dropna().unique().tolist()

    # 광진구 행정경계
    gdf = gpd.read_file("./shp/LARD_ADM_SECT_SGG_11_202502.shp", encoding="cp949")
    gwangjin = gdf[gdf['SGG_NM'] == '광진구'].copy().to_crs(epsg=4326)
    polygon = gwangjin.geometry.unary_union

    # 도로망
    graph = ox.graph_from_polygon(polygon, network_type="drive")
    edges = ox.graph_to_gdfs(graph, nodes=False, edges=True).to_crs(epsg=3857)
    edges["road_name"] = edges["name"].apply(lambda x: ", ".join(x) if isinstance(x, list) else x)

    # 보호구역 격자
    filtered_gdf = gpd.read_file("./shp/overlap_final.shp").to_crs(epsg=3857)
    edges_in_highlighted = gpd.overlay(edges, filtered_gdf, how="intersection")

    # 열선 도로 중 해당 도로명만 필터링
    safe_edges = edges_in_highlighted[edges_in_highlighted["road_name"].apply(
        lambda name: any(rd in name for rd in heat_road_names) if isinstance(name, str) else False
    )]

    return safe_edges[safe_edges["road_name"].str.contains(target_road_name, na=False)].copy()

# -------------------------------
# [2] 시각화 함수 (선택 구간만)
# -------------------------------
def visualize_segments(gdf: gpd.GeoDataFrame, indices: list[int], title="선택 구간 시각화"):
    fig, ax = plt.subplots(figsize=(18, 18))

    # Base Layer
    gdf_road = gpd.read_file("./shp/overlap/N3A_A0010000.shp").to_crs(epsg=3857)
    gdf_boundary = gpd.read_file("./shp/overlap/TN_SIGNGU_BNDRY.shp").to_crs(epsg=3857)
    gpkg_path = "./shp/overlap/garim_role.gpkg"
    layers = fiona.listlayers(gpkg_path)
    gdf_layers = {
        layer: gpd.read_file(gpkg_path, layer=layer).to_crs(epsg=3857)
        for layer in layers
    }

    gdf_road.plot(ax=ax, facecolor="#e8f5e9", edgecolor="#000000", linewidth=1)
    gdf_boundary.plot(ax=ax, facecolor="none", edgecolor="#2c8949", linewidth=3)
    for gdf_layer in gdf_layers.values():
        gdf_layer.plot(ax=ax, facecolor="#e8e8e8", edgecolor="none", alpha=1)

    # 선택된 구간만 다른 색상으로 시각화
    cmap = cm.get_cmap("tab20", len(indices))
    for i, idx in enumerate(indices):
        row = gdf.iloc[idx]
        gpd.GeoSeries([row.geometry]).plot(ax=ax, color=cmap(i), linewidth=10, label=f"구간 {idx+1}")

    plt.title(title, fontsize=14)
    plt.legend()
    plt.axis("equal")
    plt.tight_layout()
    plt.show()

# -------------------------------
# [3] 저장 함수 (누적 저장)
# -------------------------------
def save_segment_by_index(gdf: gpd.GeoDataFrame, index: int, output_path: str):
    segment = gdf.iloc[[index]][["road_name", "geometry"]]
    os.makedirs(os.path.dirname(output_path), exist_ok=True)

    if os.path.exists(output_path):
        segment.to_csv(output_path, mode='a', header=False, index=False, encoding="utf-8-sig")
    else:
        segment.to_csv(output_path, index=False, encoding="utf-8-sig")

# -------------------------------
# ✅ [4] 실행 예시
# -------------------------------
if __name__ == "__main__":
    # 1. 데이터 불러오기 (자양로50길)
    target_road_name = "자양로4길"
    filtered_edges = load_filtered_edges(target_road_name)

    # 2. 특정 구간 시각화 (예: 6, 7, 8 → 구간 7~9)
    # i for i in range(len(filtered_edges))
    visualize_segments(filtered_edges, indices=[i for i in range(len(filtered_edges))], title=f"'{target_road_name}' 구간 7~9 시각화")

    # 3. 구간 8 (index=7) 누적 저장
    save_segment_by_index(filtered_edges, index=24, output_path="./output/selected_segments.csv")
