import pandas as pd
import geopandas as gpd
import matplotlib.pyplot as plt
import contextily as ctx
import koreanize_matplotlib


def visualize_opt_area(opt_csv_path, shapefile_path):
    # 1. opt.csv 불러오기
    df_opt = pd.read_csv(opt_csv_path)
    df_opt.columns = df_opt.columns.str.lower()
    opt_gids = df_opt['gid_500'].astype(str).unique()

    # 2. filtered_pop.shp 불러오기
    gdf_pop = gpd.read_file(shapefile_path)
    gdf_pop.columns = gdf_pop.columns.str.lower()
    gdf_pop['gid_500'] = gdf_pop['gid_500'].astype(str)

    # 3. 필터링
    gdf_filtered = gdf_pop[gdf_pop['gid_500'].isin(opt_gids)].copy()

    # 4. 좌표계 설정 및 EPSG:3857로 변환
    if gdf_filtered.crs is None:
        gdf_filtered.set_crs(epsg=5181, inplace=True)  # 예: 중부 원점
    gdf_filtered = gdf_filtered.to_crs(epsg=3857)

    # 5. 시각화
    fig, ax = plt.subplots(figsize=(12, 12))
    gdf_filtered.plot(ax=ax, color='lightcoral', edgecolor='black', alpha=0.8)

    # 베이스맵 추가
    ctx.add_basemap(ax, source=ctx.providers.OpenStreetMap.Mapnik)

    ax.set_title(f"응급 의료 + 노인 유동인구 (총 {len(gdf_filtered)}개)", fontsize=14)
    plt.axis("equal")
    plt.tight_layout()
    plt.show()

visualize_opt_area(
    opt_csv_path="./data/opt.csv",
    shapefile_path="./extract_shp/filtered_pop.shp"
)
