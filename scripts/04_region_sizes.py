import os
import geopandas as gpd
import pandas as pd

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT_DIR = os.path.join(BASE_DIR, "output")
shp = os.path.join(OUT_DIR, "cook_bg_skater_60_90.shp")  

gdf = gpd.read_file(shp)
col = "skater_90"

sizes = gdf.groupby(col).size().reset_index(name="n_bgs")
sizes["share_of_all"] = sizes["n_bgs"] / len(gdf)
print(sizes.describe())

sizes.to_csv(os.path.join(OUT_DIR, "cluster_sizes_90.csv"), index=False)
