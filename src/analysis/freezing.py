import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from visualization.freezing_visualization import freezing_visualization_pipeline

freezing_visualization_pipeline(
    weather_csv="./data/전체_기상_데이터.csv",
    freezing_csv="./data/기후 격자별 결빙 건수 값.csv",
    shapefile="./shp/500m.shp",
    top_percent=0.5
)
