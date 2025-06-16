import geopandas as gpd
import pandas as pd
from shapely import wkt
import matplotlib.pyplot as plt
import fiona
import koreanize_matplotlib

# -------------------------------
# 1. 3점짜리 도로 불러와 GeoDataFrame 변환
# -------------------------------
df = pd.read_csv("./output/final_scored_roads.csv")  # 점수 통합된 파일 경로
df = df[df["score"] == 3].copy()
df["geometry"] = df["geometry"].apply(wkt.loads)
gdf = gpd.GeoDataFrame(df, geometry="geometry", crs="EPSG:3857")

# -------------------------------
# 2. 시각화 함수
# -------------------------------
def visualize_segments_single_style(gdf: gpd.GeoDataFrame, title="3점 도로 시각화 (통일 스타일)"):
    import matplotlib.pyplot as plt
    import fiona
    import geopandas as gpd

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

    # Base 맵 그리기
    gdf_road.plot(ax=ax, facecolor="#e8f5e9", edgecolor="#cccccc", linewidth=0.5)
    gdf_boundary.plot(ax=ax, facecolor="none", edgecolor="#2c8949", linewidth=2)
    for gdf_layer in gdf_layers.values():
        gdf_layer.plot(ax=ax, facecolor="#f2f2f2", edgecolor="none", alpha=1)

    # ✅ 도로 강조: 한 가지 컬러로 통일 (굵기 강조)
    gdf.plot(ax=ax, color="crimson", linewidth=6, label="3점 도로")

    plt.title(title, fontsize=16, fontweight="bold")
    plt.legend()
    plt.axis("equal")
    plt.tight_layout()
    plt.show()

# -------------------------------
# 3. 시각화 실행 (필요한 구간 인덱스 지정)
# -------------------------------
visualize_segments_single_style(gdf, title="모든 3점 도로 시각화")
