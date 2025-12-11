import os, geopandas as gpd

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT_DIR = os.path.join(BASE_DIR, "output")
shp_path = os.path.join(OUT_DIR, "cook_bg_acs2020_ses.shp")

gdf = gpd.read_file(shp_path)
print(len(gdf))
print(sorted(gdf.columns))
