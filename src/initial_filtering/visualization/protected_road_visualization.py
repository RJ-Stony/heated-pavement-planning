import geopandas as gpd
import matplotlib.pyplot as plt
import contextily as ctx
import osmnx as ox
from shapely.geometry import Point
import koreanize_matplotlib

# 1. SHP 파일 불러오기 (압축 해제된 경로 기준)
gdf = gpd.read_file("./shp/LARD_ADM_SECT_SGG_11_202502.shp", encoding='cp949')

# 2. 광진구만 필터링 (컬럼명: 'SIG_KOR_NM' 기준)
gwangjin = gdf[gdf['SGG_NM'] == '광진구'].copy()

gwangjin = gwangjin.to_crs(epsg=4326)

# -------------------------------
# 2. 광진구 polygon 기반 도로망 가져오기
# -------------------------------
polygon = gwangjin.geometry.unary_union
graph = ox.graph_from_polygon(polygon, network_type="drive")
edges = ox.graph_to_gdfs(graph, nodes=False, edges=True).to_crs(epsg=3857)
gwangjin = gwangjin.to_crs(epsg=3857)

# -------------------------------
# 3. 주소 기반 좌표 입력 → GeoDataFrame
# -------------------------------
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
addr_gdf = gpd.GeoDataFrame(
    geometry=[Point(xy) for xy in points],
    crs="EPSG:4326"
).to_crs(epsg=3857)

# -------------------------------
# 4. 전체 격자 및 필터링된 격자 불러오기
# -------------------------------
gdf_all = gpd.read_file("./shp/100m_500m.shp")
if gdf_all.crs is None:
    gdf_all.set_crs(epsg=5181, inplace=True)
gdf_all = gdf_all.to_crs(epsg=3857)

filtered_gdf = gpd.read_file("./shp/overlap_final.shp").to_crs(epsg=3857)
filtered_gdf["score"] = 0

# 주소 포인트가 포함된 격자에 점수 부여
joined = gpd.sjoin(addr_gdf, filtered_gdf, how="inner", predicate="within")
idx_with_score = joined.index_right.unique()
filtered_gdf.loc[idx_with_score, "score"] = 1

# 점수 부여된 격자만 추출
highlighted_gdf = filtered_gdf[filtered_gdf["score"] == 1]

# -------------------------------
# 5. 도로명 리스트 및 edges 전처리
# -------------------------------
safe_road_names = [
    "긴고랑로36길",
    "아차산로70길",
    "광장로1길",
    "영화사로",
    "뚝섬로64길",
    "용마산로22길",
    "천호대로113길",
    "광장로7길",
    "긴고랑로13길",
    "자양로44길",
    "능동로4길",
    "자양로50길",
    "워커힐로"
]

# name 컬럼 문자열화
edges["road_name"] = edges["name"].apply(
    lambda x: ", ".join(x) if isinstance(x, list) else x
)

# -------------------------------
# 6. 보호구역 격자 내 도로 필터링
# -------------------------------
edges_in_highlighted = gpd.overlay(edges, highlighted_gdf, how="intersection")

# 도로명 조건 적용
safe_edges = edges_in_highlighted[edges_in_highlighted["road_name"].apply(
    lambda name: any(rd in name for rd in safe_road_names) if isinstance(name, str) else False
)]

# -------------------------------
# 7. 시각화
# -------------------------------
# fig, ax 새로 생성
fig, ax = plt.subplots(figsize=(12, 12))

# 전체 도로망 (연회색 배경용)
edges.plot(
    ax=ax,
    color="black",
    linewidth=0.5,
    alpha=0.4,
    label="전체 도로망"
)

# 보호구역 내 특정 도로 (진하게 강조)
safe_edges.plot(
    ax=ax,
    color="#d62828",
    linewidth=2.5,
    alpha=0.95,
    label="보호구역 내 지정 도로"
)

# 지도 타일 (OpenStreetMap)
ctx.add_basemap(ax, source=ctx.providers.OpenStreetMap.Mapnik)

# 스타일 마무리
plt.title(f"광진구 보호구역 내 도로만 강조 (총 {len(safe_edges)}개)", fontsize=14)
plt.legend()
plt.axis("equal")
plt.tight_layout()
plt.show()
