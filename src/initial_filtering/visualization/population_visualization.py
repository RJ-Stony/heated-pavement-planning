import geopandas as gpd
import pandas as pd
import koreanize_matplotlib
import matplotlib.pyplot as plt
import contextily as ctx


def load_population_data(csv_paths):
    """
    여러 개의 연령별 유동인구 CSV 파일을 불러와 GID 기준으로 A60 평균을 계산합니다.
    """
    dfs = [pd.read_csv(path, encoding='cp949')[['GID', 'A60']] for path in csv_paths]
    df_concat = pd.concat(dfs)
    df_avg = df_concat.groupby('GID', as_index=False).mean()
    df_avg.rename(columns={'A60': 'total_count', 'GID': 'gid'}, inplace=True)
    return df_avg


def merge_population_with_gdf(gdf: gpd.GeoDataFrame, df_pop: pd.DataFrame) -> gpd.GeoDataFrame:
    gdf = gdf.copy()
    gdf = gdf.to_crs(epsg=3857)
    gdf["gid"] = gdf["gid"].astype(str)
    df_pop["gid"] = df_pop["gid"].astype(str)
    gdf = gdf.merge(df_pop, on="gid", how="left")
    return gdf


def visualize_population(gdf: gpd.GeoDataFrame, top_percent: float = 0.5,
                         title: str = "60세 이상 유동인구 (상위 50%)"):
    top_n = int(len(gdf) * top_percent)
    top_ids = gdf.nlargest(top_n, 'total_count')['gid'].tolist()
    gdf["plot_color"] = gdf["gid"].apply(lambda x: "#EFB0C9" if x in top_ids else "#D3D3D3")

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


def population_visualization_pipeline(csv_paths, shapefile_path, top_percent=0.5):
    df_pop = load_population_data(csv_paths)
    gdf = gpd.read_file(shapefile_path)
    gdf_merged = merge_population_with_gdf(gdf, df_pop)
    visualize_population(gdf_merged, top_percent=top_percent)
