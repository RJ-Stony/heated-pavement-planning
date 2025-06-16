import pandas as pd
import geopandas as gpd
import matplotlib.pyplot as plt
import contextily as ctx
import koreanize_matplotlib


def get_filtered_a60(opt_csv_path, pop_shp_path):
    df_opt = pd.read_csv(opt_csv_path)
    df_opt.columns = df_opt.columns.str.lower()
    opt_gids = df_opt['gid_500'].astype(str).unique()

    gdf_pop = gpd.read_file(pop_shp_path)
    gdf_pop.columns = gdf_pop.columns.str.lower()
    gdf_pop['gid_500'] = gdf_pop['gid_500'].astype(str)

    gdf_filtered = gdf_pop[gdf_pop['gid_500'].isin(opt_gids)].copy()

    if gdf_filtered.crs is None:
        gdf_filtered.set_crs(epsg=5181, inplace=True)
    return gdf_filtered.to_crs(epsg=3857)


def get_filtered_slope_in_freeze(slope_path, freeze_path):
    gdf_slope = gpd.read_file(slope_path)
    gdf_freeze = gpd.read_file(freeze_path)

    if gdf_slope.crs is None:
        gdf_slope.set_crs(epsg=5181, inplace=True)
    if gdf_freeze.crs is None:
        gdf_freeze.set_crs(epsg=5181, inplace=True)

    gdf_slope = gdf_slope.to_crs(epsg=3857)
    gdf_freeze = gdf_freeze.to_crs(epsg=3857)

    # slope 격자가 freeze 안에 포함된 것만
    gdf_selected = gpd.sjoin(gdf_slope, gdf_freeze, predicate='within', how='inner')
    gdf_result = gdf_slope[gdf_slope.index.isin(gdf_selected.index)].copy()
    return gdf_result


def save_and_visualize_intersection(gdf_a, gdf_b, full_shp_path, output_path,
                                    title="전체 필터링된 지역"):
    # 1. 교차 영역 추출
    gdf_intersection = gpd.overlay(gdf_a, gdf_b, how='intersection')

    # 2. 저장
    gdf_intersection.to_file(output_path)
    print(f"✅ 교차 영역 저장 완료: {output_path}")

    # 3. 전체 도형 불러오기 (정확하게 전체 100m 격자)
    gdf_all = gpd.read_file(full_shp_path)
    if gdf_all.crs is None:
        gdf_all.set_crs(epsg=5181, inplace=True)
    gdf_all = gdf_all.to_crs(epsg=3857)

    # 4. 시각화
    fig, ax = plt.subplots(figsize=(12, 12))

    # 전체 배경: 흐릿한 회색
    gdf_all.plot(ax=ax, color="#D3D3D3", edgecolor="black", alpha=0.6)

    # 강조 대상: 진한 파랑
    gdf_intersection.plot(ax=ax, color="black", edgecolor="black", alpha=0.6)

    # 베이스맵
    ctx.add_basemap(ax, source=ctx.providers.OpenStreetMap.Mapnik)

    ax.set_title(f"{title} (총 {len(gdf_intersection)}개)", fontsize=14)
    plt.axis("equal")
    plt.tight_layout()
    plt.show()

# 입력 파일 경로
opt_csv_path = "./data/opt.csv"
pop_shp_path = "./extract_shp/filtered_pop.shp"
slope_path = "./extract_shp/filtered_slope.shp"
freeze_path = "./extract_shp/filtered_freeze.shp"
output_path = "./extract_shp/overlap_final.shp"

# 1. A60 격자 불러오기
gdf_a = get_filtered_a60(opt_csv_path, pop_shp_path)

# 2. 경사도 격자 불러오기
gdf_b = get_filtered_slope_in_freeze(slope_path, freeze_path)

# 3. 교차 결과 시각화
save_and_visualize_intersection(
    gdf_a=gdf_a,
    gdf_b=gdf_b,
    full_shp_path="./shp/100m_500m.shp",  # 전체 100m 대상 배경
    output_path=output_path,
    title="전체 필터링된 지역"
)

