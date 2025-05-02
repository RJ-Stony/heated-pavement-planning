import geopandas as gpd
import pandas as pd
from shapely.geometry import shape
import fiona
import matplotlib.pyplot as plt

# --- 1. 유동인구 데이터 (A60 기준 상위 50개) ---
df_pop = pd.read_csv("2023연령별_유동인구_순위_2023_02.csv", encoding='cp949')
df_top50 = df_pop.sort_values("A60", ascending=False).head(795)
df_top50.rename(columns={"GID": "gid"}, inplace=True)

# --- 2. 100m 격자 Shapefile 파싱 ---
geoms = []
props_list = []

with fiona.open("100m격자.shp", "r") as src:
    for feat in src:
        geom = shape(feat["geometry"])
        props = feat["properties"]
        props["geometry"] = geom
        props_list.append(props)

# ✅ GeoDataFrame 생성 시 geometry 따로 지정 (Shapely 2.x 대응)
gdf_grid = gpd.GeoDataFrame(props_list)
gdf_grid.set_geometry("geometry", inplace=True)
gdf_grid.set_crs("EPSG:5179", inplace=True)

# --- 3. 병합 ---
gdf_grid.rename(columns={"gid": "gid"}, inplace=True)
merged = gdf_grid.merge(df_top50, on="gid", how="inner")

# --- 4. 시각화 (Web Mercator 투영) ---
merged = merged.to_crs(epsg=3857)

fig, ax = plt.subplots(figsize=(12, 12))
merged.plot(
    ax=ax,
    column="A60",
    cmap="YlOrRd",
    legend=True,
    edgecolor="black",
    linewidth=0.3,
    alpha=0.9
)

# 중심에 A60 수치 표시
for idx, row in merged.iterrows():
    centroid = row.geometry.centroid
    ax.text(centroid.x, centroid.y, str(int(row["A60"])),
            ha='center', va='center', fontsize=7, color='black')

plt.title("2023-02 유동인구 상위 50프로 시각화", fontsize=14)
plt.axis("off")
plt.tight_layout()
plt.show()

# --- 1. GID별 A60 총합 데이터 불러오기 ---
df_total = pd.read_csv("GID별_A60_총합_병합결과.csv")
df_total.rename(columns={"GID": "gid"}, inplace=True)

# A60 값이 적은 순서로 정렬 후 하위 795개 추출
df_bottom_795 = df_total.sort_values("A60").tail(795)

# --- 2. 100m 격자 Shapefile 파싱 ---
geoms = []
props_list = []

with fiona.open("100m격자.shp", "r") as src:
    for feat in src:
        geom = shape(feat["geometry"])
        props = feat["properties"]
        props["geometry"] = geom  # geometry를 props에 포함
        props_list.append(props)

# ✅ GeoDataFrame 생성
gdf_grid = gpd.GeoDataFrame(props_list, crs="EPSG:5179")

# --- 3. 병합 (gid 기준) ---
merged = gdf_grid.merge(df_bottom_795, on="gid", how="inner")

# --- 4. 시각화 ---
merged = merged.to_crs(epsg=3857)

fig, ax = plt.subplots(figsize=(12, 12))
merged.plot(
    ax=ax,
    column="A60",
    cmap="YlOrBr",
    legend=True,
    edgecolor="black",
    linewidth=0.2,
    alpha=0.9
)

# 수치 표시
for idx, row in merged.iterrows():
    centroid = row.geometry.centroid
    ax.text(
        centroid.x, centroid.y,
        str(int(row["A60"])),
        ha='center', va='center',
        fontsize=6,
        color='black'
    )

plt.title("GID별 A60 총합 하위 795개 히트맵", fontsize=15)
plt.axis("off")
plt.tight_layout()
plt.show()
