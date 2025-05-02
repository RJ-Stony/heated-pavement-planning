import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from visualization.population_visualization import population_visualization_pipeline

csv_paths = [
    "./data/2023_01_pop.csv",
    "./data/2023_02_pop.csv",
    "./data/2023_12_pop.csv",
    "./data/2024_01_pop.csv",
    "./data/2024_02_pop.csv",
    "./data/2024_12_pop.csv"
]

shapefile_path = "./shp/100m_500m.shp"

population_visualization_pipeline(csv_paths, shapefile_path, top_percent=0.5)
