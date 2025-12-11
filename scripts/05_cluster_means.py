import os
import geopandas as gpd
import pandas as pd

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT_DIR = os.path.join(BASE_DIR, "output")
shp = os.path.join(OUT_DIR, "cook_bg_skater_60_90.shp")  

gdf = gpd.read_file(shp)
col = "skater_80"

ses_vars = [
    "pct_white_", "pct_black_", "pct_asian_", "pct_hispan",
    "median_hh_", "poverty_ra", "pct_ba_plu",
    "unemployme", "pct_owner", "pct_renter",
]

means = gdf.groupby(col)[ses_vars].mean().reset_index()
means.to_csv(os.path.join(OUT_DIR, "cluster_means_80.csv"), index=False)
print(means.head())
