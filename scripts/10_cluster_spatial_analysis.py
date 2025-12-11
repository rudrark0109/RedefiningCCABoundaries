import os
import geopandas as gpd
import pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT_DIR = os.path.join(BASE_DIR, "output")

print("Creating Cluster Size and Compactness Analysis...")

# Read shapefile
shp_path = os.path.join(OUT_DIR, "cook_bg_skater_60_90.shp")
gdf = gpd.read_file(shp_path)

# Calculate cluster statistics
cluster_stats = []

for cluster_id in sorted(gdf["skater_90"].unique()):
    cluster_geom = gdf[gdf["skater_90"] == cluster_id]
    
    # Number of block groups
    n_bgs = len(cluster_geom)
    
    # Total area (in square meters, convert to square km)
    total_area = cluster_geom.geometry.area.sum() / 1_000_000
    
    # Compactness: perimeter^2 / area (lower is more compact)
    # Use union to get overall cluster shape
    union_geom = cluster_geom.geometry.unary_union
    perimeter = union_geom.length
    area = union_geom.area
    compactness = (perimeter ** 2) / area if area > 0 else 0
    
    # Average SES indicators
    avg_poverty = cluster_geom["poverty_ra"].mean()
    avg_income = cluster_geom["median_hh_"].mean()
    
    cluster_stats.append({
        "cluster_id": cluster_id,
        "n_block_groups": n_bgs,
        "area_sq_km": total_area,
        "compactness": compactness,
        "avg_poverty_rate": avg_poverty,
        "avg_median_income": avg_income
    })

stats_df = pd.DataFrame(cluster_stats)

# Create multi-panel figure
fig, axes = plt.subplots(2, 2, figsize=(16, 12))

# 1. Cluster size distribution (already have this but add to comprehensive view)
axes[0, 0].hist(stats_df["n_block_groups"], bins=20, edgecolor="black", alpha=0.7)
axes[0, 0].set_xlabel("Block Groups per Cluster", fontsize=11)
axes[0, 0].set_ylabel("Frequency", fontsize=11)
axes[0, 0].set_title("Cluster Size Distribution", fontsize=12)
axes[0, 0].grid(True, alpha=0.3)

# 2. Area distribution
axes[0, 1].hist(stats_df["area_sq_km"], bins=20, edgecolor="black", alpha=0.7, color="green")
axes[0, 1].set_xlabel("Area (sq km)", fontsize=11)
axes[0, 1].set_ylabel("Frequency", fontsize=11)
axes[0, 1].set_title("Cluster Area Distribution", fontsize=12)
axes[0, 1].grid(True, alpha=0.3)

# 3. Size vs Compactness
scatter = axes[1, 0].scatter(stats_df["n_block_groups"], stats_df["compactness"], 
                             c=stats_df["avg_poverty_rate"], cmap="RdYlGn_r", 
                             s=100, alpha=0.6, edgecolors="black", linewidth=0.5)
axes[1, 0].set_xlabel("Block Groups per Cluster", fontsize=11)
axes[1, 0].set_ylabel("Compactness Index", fontsize=11)
axes[1, 0].set_title("Cluster Size vs Compactness (color = poverty rate)", fontsize=12)
axes[1, 0].grid(True, alpha=0.3)
cbar = plt.colorbar(scatter, ax=axes[1, 0])
cbar.set_label("Avg Poverty Rate (%)", fontsize=10)

# 4. Income vs Poverty by cluster
scatter2 = axes[1, 1].scatter(stats_df["avg_median_income"], stats_df["avg_poverty_rate"],
                              s=stats_df["n_block_groups"]*5, alpha=0.6, 
                              edgecolors="black", linewidth=0.5, c="coral")
axes[1, 1].set_xlabel("Avg Median Income ($)", fontsize=11)
axes[1, 1].set_ylabel("Avg Poverty Rate (%)", fontsize=11)
axes[1, 1].set_title("Income vs Poverty by Cluster (size = # block groups)", fontsize=12)
axes[1, 1].grid(True, alpha=0.3)

plt.suptitle("Cluster Spatial and Socioeconomic Characteristics (k=90)", fontsize=14, y=0.995)
plt.tight_layout()
plt.savefig(os.path.join(OUT_DIR, "cluster_spatial_analysis.png"), dpi=300, bbox_inches="tight")
print(f"Saved: {os.path.join(OUT_DIR, 'cluster_spatial_analysis.png')}")

# Save statistics to CSV
stats_df.to_csv(os.path.join(OUT_DIR, "cluster_spatial_stats.csv"), index=False)
print(f"Saved: {os.path.join(OUT_DIR, 'cluster_spatial_stats.csv')}")
