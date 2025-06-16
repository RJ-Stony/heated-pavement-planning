import pandas as pd
import requests
import pandas as pd
import geopandas as gpd
from shapely.geometry import LineString
import koreanize_matplotlib
import matplotlib.pyplot as plt
import contextily as ctx

# 1. 광진구 노선 ID 리스트 불러오기
df = pd.read_excel("./data/광진구_근접기반_정류소_노선정보.xlsx")
route_ids = sorted(set(df["ROUTE_ID"]))

# 2. API 설정
SERVICE_KEY = "MyAPIKey"
BASE_URL = "http://ws.bus.go.kr/api/rest/busRouteInfo/getRoutePath"

# 3. 결과 저장 리스트
lines = []

# 4. API 호출 및 LineString 생성
for route_id in route_ids:
    params = {
        "serviceKey": SERVICE_KEY,
        "busRouteId": str(route_id),
        "resultType": "json"
    }
    try:
        response = requests.get(BASE_URL, params=params)
        if response.status_code != 200:
            continue
        print(response.text)
        data = response.json()
        points = data["ServiceResult"]["msgBody"]["itemList"]
        coords = [(float(p["gpsX"]), float(p["gpsY"])) for p in points]
        if len(coords) > 1:
            lines.append({
                "ROUTE_ID": route_id,
                "geometry": LineString(coords)
            })
    except Exception as e:
        print(f"[{route_id}] 처리 중 오류 발생: {e}")
        continue

# 5. GeoDataFrame 생성 및 좌표계 변환 (for contextily)
gdf = gpd.GeoDataFrame(lines, crs="EPSG:4326").to_crs(epsg=3857)

# 6. 시각화
fig, ax = plt.subplots(figsize=(12, 12))
gdf.plot(ax=ax, linewidth=2, alpha=0.8, column="ROUTE_ID", cmap="tab20")
ctx.add_basemap(ax, source=ctx.providers.CartoDB.Positron, zoom=12)
ax.set_title("광진구 경유 버스노선 경로 시각화 (with 배경지도)", fontsize=15)
ax.axis("off")
plt.tight_layout()
plt.show()
