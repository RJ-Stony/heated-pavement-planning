import geopandas as gpd
import pandas as pd
import koreanize_matplotlib
import matplotlib.pyplot as plt
import contextily as ctx


def load_accessibility_shapefile(filepath: str, target_crs="EPSG:5179") -> gpd.GeoDataFrame:
    encodings = ['utf-8', 'cp949', 'euc-kr']
    gdf = None
    for encoding in encodings:
        try:
            gdf = gpd.read_file(filepath, encoding=encoding)
            if not gdf.empty and not any(gdf['gid'].astype(str).str.contains('떎궗')):
                print(f"성공적인 인코딩: {encoding}")
                break
        except Exception as e:
            print(f"{encoding} 인코딩 시도 실패: {e}")

    if gdf is None or gdf.empty:
        raise ValueError("어떤 인코딩으로도 파일을 제대로 읽을 수 없습니다.")

    if gdf.crs is None or gdf.crs.to_string() != target_crs:
        gdf.crs = target_crs
        print(f"좌표계를 {target_crs}로 설정했습니다.")

    return gdf

def filter_region_by_code(gdf: gpd.GeoDataFrame, sgg_cd: str) -> gpd.GeoDataFrame:
    return gdf[gdf['sgg_cd'] == sgg_cd]

def get_bottom_percent(df: gpd.GeoDataFrame, column: str, bottom_percent: float) -> gpd.GeoDataFrame:
    df_sorted = df.sort_values(by=column, ascending=True)
    count = int(len(df_sorted) * bottom_percent)
    df['is_bottom'] = df['gid'].isin(df_sorted.iloc[count:]['gid'])
    return df

def visualize_accessibility(gdf: gpd.GeoDataFrame, column: str = 'value', title: str = ''):
    gdf = gdf.to_crs(epsg=3857)

    gdf["plot_color"] = gdf["is_bottom"].apply(lambda x: "#D62828" if x else "#D3D3D3")

    fig, ax = plt.subplots(figsize=(12, 12))
    gdf.plot(
        ax=ax,
        color=gdf["plot_color"],
        edgecolor="black",
        linewidth=0.5,
        alpha=0.5
    )
    ctx.add_basemap(ax, source=ctx.providers.OpenStreetMap.Mapnik)

    for idx, row in gdf.iterrows():
        centroid = row.geometry.centroid
        count = row[column]
        if pd.notnull(count):
            ax.annotate(f"{count}", xy=(centroid.x, centroid.y),
                        ha='center', va='center', fontweight='medium', fontsize=12, color='black')

    plt.title(title)
    plt.tight_layout()
    plt.show()

def accessibility_visualization_pipeline(filepath: str, sgg_cd: str = '11215', column: str = 'value', bottom_percent: float = 0.5):
    gdf = load_accessibility_shapefile(filepath)
    gdf_region = filter_region_by_code(gdf, sgg_cd)
    gdf_labeled = get_bottom_percent(gdf_region, column, bottom_percent)
    visualize_accessibility(
        gdf_labeled,
        column=column,
        title=f"응급의료시설 접근성 (하위 {int(bottom_percent * 100)}%)"
    )
