import geopandas as gpd
import pandas as pd
import matplotlib.pyplot as plt
import contextily as ctx

# --- 1. 전체 기상 데이터에서 gid와 좌표 추출 ---
df_weather = pd.read_csv("전체_기상_데이터.csv")
df_coords = df_weather[['gid', 'lon', 'lat']].drop_duplicates(subset='gid')
gdf_coords = gpd.GeoDataFrame(
    df_coords, 
    geometry=gpd.points_from_xy(df_coords.lon, df_coords.lat),
    crs="EPSG:4326"
)

# --- 2. 기후 격자별 결빙 건수 데이터 불러오기 ---
df_freezing = pd.read_csv("기후 격자별 결빙 건수 값.csv")

# --- 3. 500m 격자 shapefile 불러오기 및 중심점 계산 ---
gdf = gpd.read_file("500m.shp")
if gdf.crs is None:
    gdf = gdf.set_crs("EPSG:4326")

# 각 격자의 중심점을 계산
gdf_centroids = gdf.copy()
gdf_centroids["geometry"] = gdf_centroids.centroid
gdf_centroids = gdf_centroids.to_crs("EPSG:4326")

# --- 4. 공간 결합을 위해 투영 좌표계(EPSG:3857)로 변환 ---
gdf_centroids_proj = gdf_centroids.to_crs(epsg=3857)
gdf_coords_proj = gdf_coords.to_crs(epsg=3857)

# 공간 결합: 각 중심점에 가장 가까운 weather 좌표의 gid 부여
gdf_centroids_with_gid = gpd.sjoin_nearest(
    gdf_centroids_proj, 
    gdf_coords_proj[['gid', 'geometry']], 
    distance_col="dist"
)

# --- 5. gid를 기준으로 결빙 건수(total_count) 병합 ---
gdf_centroids_with_gid = gdf_centroids_with_gid.merge(df_freezing, on="gid", how="left")

# --- 6. 원래의 격자(gdf)를 EPSG:3857로 변환한 후 gid와 total_count 할당 ---
gdf = gdf.to_crs(epsg=3857)
gdf["gid"] = gdf_centroids_with_gid["gid"].values
gdf["total_count"] = gdf_centroids_with_gid["total_count"].values

# --- 7. 상위 20개 격자(gid) 추출 및 색상 지정 ---
top20_ids = gdf.nlargest(47, 'total_count')['gid'].tolist()
# 상위 20개는 "red", 나머지는 "lightgray"로 색상 부여하는 새 컬럼 생성
gdf["plot_color"] = gdf["gid"].apply(lambda x: "lightcoral" if x in top20_ids else "lightgray")

# --- 8. 시각화: 전체 격자에 대해 지정된 색상으로 표시 ---
fig, ax = plt.subplots(figsize=(12, 12))
gdf.plot(
    ax=ax,
    color=gdf["plot_color"],
    edgecolor="black",
    linewidth=0.5,
    alpha=0.5
)
ctx.add_basemap(ax, source=ctx.providers.OpenStreetMap.Mapnik)

# --- 9. 각 격자 중앙에 결빙 건수 텍스트 추가 ---
for idx, row in gdf.iterrows():
    centroid = row.geometry.centroid
    count = row['total_count']
    if pd.notnull(count):
        ax.annotate(f"{int(count)}건", xy=(centroid.x, centroid.y),
                    ha='center', va='center', fontsize=10, color='black')

plt.title("결빙 예측 건수 시각화 (상위 50%)")
plt.tight_layout()
plt.show()
