import geopandas as gpd
import matplotlib.pyplot as plt
import contextily as ctx
import koreanize_matplotlib


def visualize_slope_within_freeze(slope_path, freeze_path):
    # 1. 파일 불러오기
    gdf_slope = gpd.read_file(slope_path)
    gdf_freeze = gpd.read_file(freeze_path)

    # 2. 좌표계 설정 및 통일
    if gdf_slope.crs is None:
        gdf_slope.set_crs(epsg=5181, inplace=True)
    if gdf_freeze.crs is None:
        gdf_freeze.set_crs(epsg=5181, inplace=True)

    gdf_slope = gdf_slope.to_crs(epsg=3857)
    gdf_freeze = gdf_freeze.to_crs(epsg=3857)

    # 3. 공간 조인: slope가 freeze에 포함되는 것만 추출
    gdf_selected = gpd.sjoin(gdf_slope, gdf_freeze, predicate='within', how='inner')

    # 4. 중복 제거 (중복되는 slope 격자가 여러 freeze에 걸칠 수 있음)
    gdf_result = gdf_slope[gdf_slope.index.isin(gdf_selected.index)].copy()

    # 5. 시각화
    fig, ax = plt.subplots(figsize=(12, 12))
    gdf_result.plot(ax=ax, color='#2E7B78', edgecolor='black', alpha=0.7)
    ctx.add_basemap(ax, source=ctx.providers.OpenStreetMap.Mapnik)

    ax.set_title(f"결빙 지역 + 경사도 (총 {len(gdf_result)}개)", fontsize=14)
    plt.axis("equal")
    plt.tight_layout()
    plt.show()

    return gdf_result

gdf_result = visualize_slope_within_freeze(
    slope_path="./extract_shp/filtered_slope.shp",
    freeze_path="./extract_shp/filtered_freeze.shp"
)
