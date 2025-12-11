import os
import numpy as np
import geopandas as gpd
from libpysal.weights import Queen
from spopt.region import Skater
from sklearn.preprocessing import StandardScaler

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT_DIR = os.path.join(BASE_DIR, "output")
shp_path = os.path.join(OUT_DIR, "cook_bg_acs2020_ses.shp")

print("="*80)
print("SKATER: Cook County only, ~75 clusters")
print("="*80)

# 1. Read SES shapefile and restrict to Cook County
gdf = gpd.read_file(shp_path)
print(f"Total rows in shapefile: {len(gdf)}")

# Filter to Cook County (GEOID starting with 17031)
gdf = gdf[gdf["GEOID"].str.startswith("17031")].copy()
print(f"Rows in Cook County subset: {len(gdf)}")

# 2. Choose a small SES feature set (5 vars) using your truncated names
attrs_name = [
    "pct_white_",   # race
    "pct_black_",
    "poverty_ra",   # poverty rate
    "pct_ba_plu",   # % BA+
    "unemployme",   # unemployment rate
]

# keep only those that actually exist
attrs_name = [c for c in attrs_name if c in gdf.columns]
print(f"Using these SES variables: {attrs_name}")

# Drop rows with NaNs in these columns
gdf = gdf.dropna(subset=attrs_name).reset_index(drop=True)
print(f"Rows after dropping NaNs: {len(gdf)}")

# 3. Build Queen contiguity weights on this Cook subset
print("\nBuilding Queen contiguity weights...")
w = Queen.from_dataframe(gdf, use_index=False)
print("Done. Number of regions with neighbors:", len(w.neighbors))

# 4. Prepare standardized data matrix
X = gdf[attrs_name].to_numpy()
scaler = StandardScaler()
X_scaled = scaler.fit_transform(X)

# 5. Run SKATER once with n_clusters ~75
n_clusters = 75
floor = 10
print(f"\nRunning SKATER with n_clusters={n_clusters}, floor={floor} ...")

model = Skater(
    gdf,
    w,
    attrs_name=attrs_name,
    n_clusters=n_clusters,
    floor=floor,
    trace=True,          # show some progress
    islands="increase",
    spanning_forest_kwds={}
)
model.solve()

labels = np.array(model.labels_)
gdf["skater_75"] = labels
print("SKATER finished.")

# 6. Save output shapefile
out_shp = os.path.join(OUT_DIR, "cook_bg_skater_75.shp")
gdf.to_file(out_shp)
print(f"\nSaved SKATER 75-cluster result to: {out_shp}")
print("Done.")
