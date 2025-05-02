import geopandas as gpd
import pandas as pd
import koreanize_matplotlib
import matplotlib.pyplot as plt

def load_population_data(csv_paths):
    dfs = [pd.read_csv(path, encoding='cp949')[['GID', 'A60']] for path in csv_paths]
    df_concat = pd.concat(dfs)
    df_avg = df_concat.groupby('GID', as_index=False).mean()
    df_avg.rename(columns={'A60': 'total_count', 'GID': 'gid'}, inplace=True)
    return df_avg

def merge_population_with_gdf(shp_path, df_pop):
    gdf = gpd.read_file(shp_path)
    gdf = gdf.to_crs(epsg=3857)
    gdf["gid"] = gdf["gid"].astype(str)
    df_pop["gid"] = df_pop["gid"].astype(str)
    gdf_merged = gdf.merge(df_pop, on="gid", how="left")
    return gdf_merged

def extract_top50_gid500(gdf_merged, output_path):
    top_n = int(len(gdf_merged) * 0.5)
    gdf_top50 = gdf_merged.nlargest(top_n, 'total_count')
    gdf_top_gid500 = gpd.GeoDataFrame(
        gdf_top50[['gid_500']].copy(),
        geometry=gdf_top50['geometry'].copy(),
        crs=gdf_top50.crs
    )
    gdf_top_gid500.to_file(output_path)
    print(f"✅ 저장 완료: {output_path}")
    return gdf_top_gid500

def plot_gid500(gdf_top_gid500, title="Top 50% A60 유동인구의 gid_500"):
    fig, ax = plt.subplots(figsize=(12, 12))
    gdf_top_gid500.plot(ax=ax, edgecolor='black', facecolor='lightcoral', alpha=0.6)
    for idx, row in gdf_top_gid500.iterrows():
        centroid = row.geometry.centroid
        ax.annotate(str(row['gid_500']), xy=(centroid.x, centroid.y),
                    ha='center', va='center', fontsize=8, color='black')
    ax.set_title(title)
    plt.tight_layout()
    plt.show()

# 사용 예시
csv_paths = ["./data/2023_01_pop.csv", "./data/2023_02_pop.csv", "./data/2023_12_pop.csv",
             "./data/2024_01_pop.csv", "./data/2024_02_pop.csv", "./data/2024_12_pop.csv"]  # 실제 파일 경로 입력
shapefile_path = "./shp/100m_500m.shp"
output_path = "./extract_shp/filter_pop.shp"

df_pop = load_population_data(csv_paths)
gdf_merged = merge_population_with_gdf(shapefile_path, df_pop)
gdf_top_gid500 = extract_top50_gid500(gdf_merged, output_path)
plot_gid500(gdf_top_gid500)
