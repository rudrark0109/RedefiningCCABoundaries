import os
import numpy as np
import pandas as pd
import geopandas as gpd
from libpysal.weights import Queen
from spopt.region import Skater
from sklearn.preprocessing import StandardScaler

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT_DIR = os.path.join(BASE_DIR, "output")

print("="*80)
print("SKATER regionalization over range of cluster numbers (Cook only)")
print("="*80)

# 1. Read SES shapefile and restrict to Cook County
shp_path = os.path.join(OUT_DIR, "cook_bg_acs2020_ses.shp")
gdf_all = gpd.read_file(shp_path)
print(f"Total rows in original shapefile: {len(gdf_all)}")

# Filter to Cook: COUNTYFP == '031' if present, else GEOID prefix
if "COUNTYFP" in gdf_all.columns:
    gdf = gdf_all[gdf_all["COUNTYFP"] == "031"].copy()
else:
    gdf = gdf_all[gdf_all["GEOID"].str.startswith("17031")].copy()

print(f"Rows in Cook County subset: {len(gdf)}")

# 2. Choose SES variables using your truncated names
candidate_attrs = [
    "pct_white_",   # % White NH
    "pct_black_",   # % Black NH
    "pct_asian_",   # % Asian NH
    "pct_hispan",   # % Hispanic
    "median_hh_",   # median HH income
    "poverty_ra",   # poverty rate
    "pct_ba_plu",   # % BA+
    "unemployme",   # unemployment rate
    "pct_owner",    # % owner
    "pct_renter",   # % renter
]

attrs_name = [c for c in candidate_attrs if c in gdf.columns]
print("\nUsing these SES variables for clustering:")
print(attrs_name)

# 3. Drop rows with NaNs in these columns
gdf = gdf.dropna(subset=attrs_name).reset_index(drop=True)
print(f"\nRows after dropping NaNs in SES variables: {len(gdf)}")

# 4. Build Queen weights on Cook subset
print("\nBuilding Queen contiguity weights on Cook subset...")
w = Queen.from_dataframe(gdf, use_index=False)
print("Done. Number of regions with neighbors:", len(w.neighbors))

#drop islands smaller than quorum
print("Dropping islands (units with no neighbors)...")
islands = w.islands
if islands:
    gdf = gdf.drop(index=islands).reset_index(drop=True)
    print(f"Rows after dropping islands: {len(gdf)}")
    w = Queen.from_dataframe(gdf, use_index=False)
else:
    print("No islands found.")

# 5. Standardize SES data
X = gdf[attrs_name].to_numpy()
scaler = StandardScaler()
X_scaled = scaler.fit_transform(X)

def compute_bss_tss(data, labels):
    overall_mean = data.mean(axis=0)
    tss = ((data - overall_mean) ** 2).sum()
    wss = 0.0
    for k in np.unique(labels):
        cluster = data[labels == k]
        if len(cluster) == 0:
            continue
        cm = cluster.mean(axis=0)
        wss += ((cluster - cm) ** 2).sum()
    bss = tss - wss
    return float(bss), float(tss), float(bss / tss)

# 6. Run SKATER for range 60–90
n_clusters_range = list(range(75, 91, 5))  # 60,65,...,90
floor = 10
results = []

for n_clust in n_clusters_range:
    print(f"\nRunning SKATER: n_clusters = {n_clust}, floor = {floor}")
    model = Skater(
        gdf,
        w,
        attrs_name=attrs_name,
        n_clusters=n_clust,
        floor=floor,
        trace=False,
        islands="increase",
        spanning_forest_kwds={}
    )
    model.solve()
    labels = np.array(model.labels_)
    gdf[f"skater_{n_clust}"] = labels

    bss, tss, ratio = compute_bss_tss(X_scaled, labels)
    print(f"  BSS/TSS: {ratio:.3f}")
    results.append({"n_clusters": n_clust, "BSS_TSS": ratio})

# 7. Save metrics + clusters
metrics_df = pd.DataFrame(results)
metrics_path = os.path.join(OUT_DIR, "skater_metrics_60_90.csv")
metrics_df.to_csv(metrics_path, index=False)
print(f"\nSaved metrics to: {metrics_path}")

out_shp = os.path.join(OUT_DIR, "cook_bg_skater_60_90.shp")
gdf.to_file(out_shp)
print(f"Saved clustered GeoDataFrame to: {out_shp}")

print("\nDone.")
