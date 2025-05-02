import geopandas as gpd
import pandas as pd
import koreanize_matplotlib
import matplotlib.pyplot as plt
import contextily as ctx


def load_slope_data(slope_csv_path):
    """
    경사도 CSV 파일을 불러오고 gid와 max 값을 추출합니다.
    """
    df = pd.read_csv(slope_csv_path, encoding='cp949')[['gid', 'max']]
    df['gid'] = df['gid'].astype(str)
    return df


def merge_slope_with_gdf(gdf: gpd.GeoDataFrame, df_slope: pd.DataFrame) -> gpd.GeoDataFrame:
    gdf = gdf.copy()
    gdf = gdf.to_crs(epsg=3857)
    gdf['gid'] = gdf['gid'].astype(str)
    merged = gdf.merge(df_slope, on='gid', how='left')
    return merged


def visualize_slope(gdf: gpd.GeoDataFrame, top_percent: float = 0.5,
                    title: str = "경사도 max 기준 상위 50% 지역"):
    top_n = int(len(gdf) * top_percent)
    top_ids = gdf.nlargest(top_n, 'max')['gid'].tolist()
    gdf["plot_color"] = gdf["gid"].apply(lambda x: "#5DBB63" if x in top_ids else "#D3D3D3")

    fig, ax = plt.subplots(figsize=(12, 12))
    gdf.plot(
        ax=ax,
        color=gdf["plot_color"],
        edgecolor="black",
        linewidth=0.5,
        alpha=0.6
    )
    ctx.add_basemap(ax, source=ctx.providers.OpenStreetMap.Mapnik)
    plt.title(title)
    plt.tight_layout()
    plt.show()


def slope_visualization_pipeline(slope_csv_path, shapefile_path, top_percent=0.5):
    df_slope = load_slope_data(slope_csv_path)
    gdf = gpd.read_file(shapefile_path)
    gdf_merged = merge_slope_with_gdf(gdf, df_slope)
    visualize_slope(gdf_merged, top_percent=top_percent)
