import os
import geopandas as gpd
import matplotlib.pyplot as plt
import contextily as ctx

# 1. 환경 변수 설정 (shx 문제 발생 시)
# 2. os.environ["SHAPE_RESTORE_SHX"] = "YES" # 필요시

# 3. Shapefile 불러오기
encodings = ['utf-8', 'cp949', 'euc-kr']
gdf = None

for encoding in encodings:
    try:
        gdf = gpd.read_file('data/159.2 응급의료시설(시군구격자) 접근성.shp', encoding=encoding)
        # 인코딩이 올바른지 확인 (gid 컬럼에 한글이 제대로 표시되는지)
        if not gdf.empty and not any(gdf['gid'].astype(str).str.contains('떎궗')):
            print(f"성공적인 인코딩: {encoding}")
            break
    except Exception as e:
        print(f"{encoding} 인코딩 시도 실패: {e}")

if gdf is None or gdf.empty:
    raise ValueError("어떤 인코딩으로도 파일을 제대로 읽을 수 없습니다.")

# 4. 좌표계 확인 및 필요 시 설정 (prj 파일에 따라 자동 인식될 수도 있음)
#   - 만약 crs가 None 이거나 잘못 인식된다면, gdf.crs = 'EPSG:5179' 로 직접 지정
print("원본 좌표계:", gdf.crs)

if gdf.crs is None or gdf.crs.to_string() != 'EPSG:5179':
    # 메타데이터에 따라 직접 지정
    gdf.crs = 'EPSG:5179'
    print("좌표계를 EPSG:5179(GRS80 UTM-K)로 설정했습니다.")

# 5. 광진구 데이터 필터링
#   - sgg_cd == '11215' 가 광진구임을 확인
gdf_gwangjin = gdf[gdf['sgg_cd'] == '11215']
print("광진구 격자 개수:", len(gdf_gwangjin))

# 6. 하위 50%(접근성이 낮은 지역) 추출
#   - value 기준 오름차순 정렬 → 뒤쪽 절반이 접근성이 낮은 영역
gdf_sorted = gdf_gwangjin.sort_values(by='value', ascending=True)
half_count = int(len(gdf_sorted) * 0.5)
gdf_bottom50 = gdf_sorted.iloc[half_count:]
print("광진구 하위 50% 격자 수:", len(gdf_bottom50))

# 7. Basemap과 겹쳐 그리기 위해 EPSG:3857(Web Mercator)로 변환
gdf_bottom50_3857 = gdf_bottom50.to_crs(epsg=3857)

# 8. 시각화
fig, ax = plt.subplots(figsize=(12, 8))
# 분홍/빨강 계열로 표현하고 싶다면 Reds, OrRd, PuRd 등을 사용할 수 있습니다.
gdf_bottom50_3857.plot(
    ax=ax,
    column='value',
    cmap='Reds',
    legend=False,
    alpha=0.6,        # 투명도(원하는 대로 조절)
    edgecolor='gray'  # 격자 테두리 색상
)

# 9. 각 격자에 'value' 값을 표시 (대표점 사용)
for idx, row in gdf_bottom50_3857.iterrows():
    rep_point = row['geometry'].representative_point()
    ax.text(rep_point.x, rep_point.y,
            str(row['value']),
            ha='center', va='center',
            fontsize=8, color='black')


# OpenStreetMap 사용
ctx.add_basemap(ax, source=ctx.providers.OpenStreetMap.Mapnik)

# 11. 제목 및 축 설정
plt.title('광진구 응급의료시설 접근성 - 하위 50% (접근성이 낮은 지역)')
plt.xlabel('경도')
plt.ylabel('위도')
plt.tight_layout()
plt.show()
