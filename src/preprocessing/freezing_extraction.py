import geopandas as gpd
import pandas as pd
import matplotlib.pyplot as plt

# 1. CSV 불러오기 (gid_500만 포함)
df_filtered = pd.read_csv("./extract_shp/filtered_weather.csv")

# 2. 속성만 불러오기
gdf_attrs = gpd.read_file("./shp/100m_500m.shp", ignore_geometry=True)

# 3. geometry만 따로 불러오기
gdf_geom = gpd.read_file("./shp/100m_500m.shp")

# 4. 속성과 geometry 수동 결합
gdf_full = gpd.GeoDataFrame(
    gdf_attrs,
    geometry=gdf_geom.geometry,
    crs=gdf_geom.crs
)

# 5. 필터링 (gid_500 기준)
gdf_filtered = gdf_full[gdf_full["gid_500"].isin(df_filtered["gid_500"])]

# 6. dissolve 로 500m 격자 단위 통합
gdf_dissolved = gdf_filtered.dissolve(by="gid_500", as_index=False)

# 7. 저장
gdf_dissolved.to_file("filtered_weather.shp")

# 8. 시각화
fig, ax = plt.subplots(figsize=(12, 12))
gdf_dissolved.to_crs(epsg=3857).plot(ax=ax, edgecolor="black", facecolor="skyblue", alpha=0.6)
ax.set_title("Filtered gid_500 지역 (500m 격자)")
plt.tight_layout()
plt.show()
