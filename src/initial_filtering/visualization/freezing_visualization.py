import geopandas as gpd
import pandas as pd
import koreanize_matplotlib
import matplotlib.pyplot as plt
import contextily as ctx


def extract_unique_gid_coords(df_weather: pd.DataFrame) -> gpd.GeoDataFrame:
    df_coords = df_weather[['gid', 'lon', 'lat']].drop_duplicates(subset='gid')
    return gpd.GeoDataFrame(
        df_coords,
        geometry=gpd.points_from_xy(df_coords.lon, df_coords.lat),
        crs="EPSG:4326"
    )


def calculate_centroids(gdf: gpd.GeoDataFrame, target_crs="EPSG:4326") -> gpd.GeoDataFrame:
    gdf_centroids = gdf.copy()
    gdf_centroids["geometry"] = gdf_centroids.centroid
    return gdf_centroids.to_crs(target_crs)


def spatial_join_nearest_gid(gdf_centroids: gpd.GeoDataFrame, gdf_coords: gpd.GeoDataFrame) -> gpd.GeoDataFrame:
    gdf_centroids_proj = gdf_centroids.to_crs(epsg=3857)
    gdf_coords_proj = gdf_coords.to_crs(epsg=3857)
    joined = gpd.sjoin_nearest(
        gdf_centroids_proj,
        gdf_coords_proj[['gid', 'geometry']],
        distance_col="dist"
    )
    return joined


def merge_freezing_counts(gdf_centroids_with_gid: gpd.GeoDataFrame, df_freezing: pd.DataFrame) -> gpd.GeoDataFrame:
    return gdf_centroids_with_gid.merge(df_freezing, on="gid", how="left")


def visualize_result(gdf: gpd.GeoDataFrame, enriched_centroids: gpd.GeoDataFrame,
                     top_percent: float = 0.5, title: str = "결빙 예측 건수 (상위 50%)"):
    gdf = gdf.to_crs(epsg=3857)
    gdf["gid"] = enriched_centroids["gid"].values
    gdf["total_count"] = enriched_centroids["total_count"].values

    top_n = int(len(gdf) * top_percent)
    top_ids = gdf.nlargest(top_n, 'total_count')['gid'].tolist()
    gdf["plot_color"] = gdf["gid"].apply(lambda x: "#003B8E" if x in top_ids else "#D3D3D3")

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
        count = row['total_count']
        if pd.notnull(count):
            ax.annotate(f"{int(count)}건", xy=(centroid.x, centroid.y),
                        ha='center', va='center', fontweight='medium', fontsize=12, color='black')

    plt.title(title)
    plt.tight_layout()
    plt.show()


def freezing_visualization_pipeline(weather_csv: str, freezing_csv: str, shapefile: str, top_percent: float = 0.5):
    df_weather = pd.read_csv(weather_csv)
    df_freezing = pd.read_csv(freezing_csv)
    gdf = gpd.read_file(shapefile)

    gdf_coords = extract_unique_gid_coords(df_weather)
    centroids = calculate_centroids(gdf)
    joined = spatial_join_nearest_gid(centroids, gdf_coords)
    enriched = merge_freezing_counts(joined, df_freezing)
    visualize_result(gdf, enriched, top_percent=top_percent)
