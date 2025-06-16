import pandas as pd
import geopandas as gpd
from shapely.geometry import Point
import matplotlib.pyplot as plt
import contextily as ctx
import koreanize_matplotlib

# 1. 좌표 입력
points = [
    (127.091743, 37.557558),
    (127.100496, 37.541105),
    (127.100646, 37.548106),
    (127.098655, 37.553036),
    (127.089106, 37.530348),
    (127.088346, 37.564860),
    (127.083542, 37.558158),
    (127.104934, 37.548403),
    (127.097621, 37.553968),
    (127.082961, 37.564937),
    (127.096317, 37.550054),
    (127.071287, 37.530952),
    (127.096383, 37.552830),
    (127.097188, 37.550597),
]

# 2. 주소 포인트 → GeoDataFrame
addr_gdf = gpd.GeoDataFrame(
    geometry=[Point(xy) for xy in points],
    crs="EPSG:4326"
).to_crs(epsg=3857)

# 3. 전체 100m 격자
gdf_all = gpd.read_file("./shp/100m_500m.shp")
if gdf_all.crs is None:
    gdf_all.set_crs(epsg=5181, inplace=True)
gdf_all = gdf_all.to_crs(epsg=3857)

# 4. 필터링된 영역
filtered_gdf = gpd.read_file("./shp/overlap_final.shp").to_crs(epsg=3857)
filtered_gdf["score"] = 0  # 초기화

# 5. 공간 조인 → 점수 부여
joined = gpd.sjoin(addr_gdf, filtered_gdf, how="inner", predicate="within")
idx_with_score = joined.index_right.unique()
filtered_gdf.loc[idx_with_score, "score"] = 1

fig, ax = plt.subplots(figsize=(12, 12))

# (1) 전체 격자: 흐릿한 회색 배경
gdf_all.plot(ax=ax, color="#D3D3D3", edgecolor="gray", alpha=0.4)

# (2) 필터링된 격자: 노랑 + 테두리 강조
filtered_gdf[filtered_gdf["score"] == 0].plot(
    ax=ax,
    color="#FFD166",
    edgecolor="black",  # 진한 회색 선
    linewidth=0.8,
    alpha=0.6,
    label="필터링된 지역"
)

# (3) 주소 포함 격자: 빨강 + 두껍게
filtered_gdf[filtered_gdf["score"] == 1].plot(
    ax=ax,
    color="#EF476F",
    edgecolor="black",
    linewidth=1.2,
    alpha=0.9,
    label="특정 주소 포함"
)   

# 베이스맵
ctx.add_basemap(ax, source=ctx.providers.OpenStreetMap.Mapnik)

# 제목/범례/스타일
plt.title(f"전체 격자 + 필터링 + 주소 포함 (총 {len(filtered_gdf)}개)", fontsize=14)
plt.legend()
plt.axis("equal")
plt.tight_layout()
plt.show()

# 주소 포함된 격자만 추출
highlighted_gdf = filtered_gdf[filtered_gdf["score"] == 1]

# 파일로 저장 (파일명은 원하는 대로)
highlighted_gdf.to_file("./shp/protected_area_senior_child.shp", encoding="utf-8")
