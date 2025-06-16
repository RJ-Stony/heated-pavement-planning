import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from visualization.slope_visualization import slope_visualization_pipeline

slope_csv_path = "./data/slope_stats_by_cell.csv"
shapefile_path = "./shp/100m_500m.shp"

slope_visualization_pipeline(slope_csv_path, shapefile_path, top_percent=0.5)
