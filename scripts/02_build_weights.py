import os
import geopandas as gpd
from libpysal.weights import Queen

# Paths
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT_DIR = os.path.join(BASE_DIR, "output")

print("="*80)
print("Building Queen contiguity weights for Cook County BGs")
print("="*80)
print(f"Base Directory: {BASE_DIR}")
print(f"Output Directory: {OUT_DIR}\n")

# 1. Read SES shapefile
shp_path = os.path.join(OUT_DIR, "cook_bg_acs2020_ses.shp")
print(f"Reading shapefile: {shp_path}")
gdf = gpd.read_file(shp_path)
print(f"GeoDataFrame rows: {len(gdf)}")

# Filter to Cook: COUNTYFP == '031' or GEOID startswith '17031'
if "COUNTYFP" in gdf.columns:
    gdf = gdf[gdf["COUNTYFP"] == "031"].copy()
else:
    gdf = gdf[gdf["GEOID"].str.startswith("17031")].copy()
print(f"GeoDataFrame rows (Cook only): {len(gdf)}")

# 2. Build Queen contiguity
print("\nConstructing Queen contiguity weights...")
w = Queen.from_dataframe(gdf)
print("Done.\n")

# 3. Basic diagnostics
n = len(w.neighbors)
avg_neighbors = sum(len(v) for v in w.neighbors.values()) / n
print(f"Number of regions (should match rows): {n}")
print(f"Average number of neighbors: {avg_neighbors:.2f}")

# 4. Optional: save neighbors to CSV for inspection
neighbors_out = os.path.join(OUT_DIR, "cook_bg_queen_neighbors.csv")
print(f"\nSaving neighbors list to: {neighbors_out}")
rows = []
for geoid, neighs in zip(w.id_order, w.neighbors.values()):
    rows.append({
        "GEOID": geoid,
        "neighbors": ",".join(str(gdf.loc[i, "GEOID"]) for i in neighs)
    })
import pandas as pd
pd.DataFrame(rows).to_csv(neighbors_out, index=False)

print("\nAll done.")
