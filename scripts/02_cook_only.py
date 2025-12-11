# new script: 02_make_cook_only.py
import os, geopandas as gpd
BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(BASE, "output")
gdf = gpd.read_file(os.path.join(OUT, "cook_bg_acs2020_ses.shp"))
gdf_cook = gdf[gdf["GEOID"].str.startswith("17031")].copy()
print(len(gdf_cook))
gdf_cook.to_file(os.path.join(OUT, "cook_only_ses.shp"))
