import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from visualization.accessibility_visualization import accessibility_visualization_pipeline

project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../"))
data_path = os.path.join(project_root, "data", "processed", "shp", "access", "159.2 응급의료시설(시군구격자) 접근성.shp")

accessibility_visualization_pipeline(
    filepath=data_path,
    sgg_cd="11215",              # 광진구
    column="value",              # 접근성 지표 컬럼
    bottom_percent=0.5           # 하위 50% 필터링
)
