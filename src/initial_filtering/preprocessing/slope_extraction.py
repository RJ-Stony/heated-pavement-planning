import geopandas as gpd
import pandas as pd
import koreanize_matplotlib
import matplotlib.pyplot as plt

def load_slope_data(slope_csv_path):
    df = pd.read_csv(slope_csv_path, encoding='cp949')[['gid', 'max']]
    df['gid'] = df['gid'].astype(str)
    return df

def merge_slope_with_gdf(shapefile_path, df_slope):
    gdf = gpd.read_file(shapefile_path)
    gdf = gdf.to_crs(epsg=3857)
    gdf["gid"] = gdf["gid"].astype(str)
    df_slope["gid"] = df_slope["gid"].astype(str)
    return gdf.merge(df_slope, on="gid", how="left")

def extract_top50_slope(gdf_merged, output_path):
    top_n = int(len(gdf_merged) * 0.5)
    gdf_top50 = gdf_merged.nlargest(top_n, 'max').copy()
    gdf_top50.to_file(output_path)
    print(f"✅ 저장 완료: {output_path}")
    return gdf_top50

def plot_top_slope(gdf_top50, title="Top 50% 경사도 영역"):
    fig, ax = plt.subplots(figsize=(12, 12))
    gdf_top50.plot(ax=ax, edgecolor='black', facecolor='#5DBB63', alpha=0.6)
    ax.set_title(title)
    
    # 선택적: centroid에 gid 표시
    for idx, row in gdf_top50.iterrows():
        centroid = row.geometry.centroid
        ax.annotate(str(row['gid']), xy=(centroid.x, centroid.y),
                    ha='center', va='center', fontsize=7, color='black')
    
    plt.tight_layout()
    plt.show()

slope_csv_path = "./data/slope_stats_by_cell.csv"
shapefile_path = "./shp/100m_500m.shp"
output_path = "./extract_shp/filtered_slope.shp"

df_slope = load_slope_data(slope_csv_path)
gdf_merged = merge_slope_with_gdf(shapefile_path, df_slope)
gdf_top50 = extract_top50_slope(gdf_merged, output_path)
plot_top_slope(gdf_top50)
