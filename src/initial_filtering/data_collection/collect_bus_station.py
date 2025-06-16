import pandas as pd
import geopandas as gpd
from shapely.geometry import Point

# 1. 광진구 SHP 파일 로드 및 필터링
gdf = gpd.read_file("./shp/bsst_info.shp")
gwangjin = gdf[gdf["SIGNGU_NM"] == "광진구"]
gwangjin = gwangjin.to_crs(epsg=4326)

# 2. 엑셀에서 정류소 데이터 불러오기 + geometry 생성
df = pd.read_excel("./data/서울시버스노선별정류소정보(20250204).xlsx")
df["geometry"] = df.apply(lambda row: Point(row["X좌표"], row["Y좌표"]), axis=1)
df_gdf = gpd.GeoDataFrame(df, geometry="geometry", crs="EPSG:4326")

# 3. 광진구 정류소와 엑셀 정류소들 간의 '근접 매칭'
# max_distance는 약 50미터 이내로 판단
joined = gpd.sjoin_nearest(df_gdf, gwangjin[["geometry"]], how="inner", max_distance=0.0005)

# 4. 필요한 컬럼 정리 후 저장
result = joined[["ROUTE_ID", "노선명", "순번", "NODE_ID", "ARS_ID", "정류소명", "X좌표", "Y좌표"]]
result.to_excel("./data/광진구_근접기반_정류소_노선정보.xlsx", index=False)
route_ids = result["정류소명"].unique()
print(len(route_ids))
