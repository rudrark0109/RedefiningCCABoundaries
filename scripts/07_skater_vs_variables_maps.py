import os
import geopandas as gpd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.colors import ListedColormap
import numpy as np

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT_DIR = os.path.join(BASE_DIR, "output")

print("Creating SKATER Clusters vs SES Variables Comparison Maps...")

# Read shapefile
shp_path = os.path.join(OUT_DIR, "cook_bg_skater_60_90.shp")
gdf = gpd.read_file(shp_path)

# Define key SES variables to compare with clusters
comparison_vars = [
    ("poverty_ra", "Poverty Rate (%)", "RdYlGn_r"),
    ("median_hh_", "Median Household Income ($)", "RdYlGn"),
    ("pct_ba_plu", "% Bachelor's Degree+", "Blues"),
    ("unemployme", "Unemployment Rate (%)", "Reds")
]

# Create figure: SKATER map on left, 4 SES variable maps on right
fig = plt.figure(figsize=(24, 10))
gs = fig.add_gridspec(2, 3, hspace=0.3, wspace=0.2)

# Large SKATER cluster map (left side, spanning 2 rows)
ax_skater = fig.add_subplot(gs[:, 0])
gdf.plot(column="skater_90", categorical=True, legend=False, 
         linewidth=0.2, edgecolor="black", ax=ax_skater, cmap="tab20c")
ax_skater.set_title("SKATER Clusters (k=90)", fontsize=14, fontweight='bold', pad=15)
ax_skater.set_axis_off()

# Add cluster count text
n_clusters = gdf["skater_90"].nunique()
ax_skater.text(0.02, 0.98, f'{n_clusters} regions', 
               transform=ax_skater.transAxes, fontsize=11,
               verticalalignment='top',
               bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.8))

# SES variable maps (right side, 2x2 grid)
positions = [(0, 1), (0, 2), (1, 1), (1, 2)]
for idx, (var, title, cmap) in enumerate(comparison_vars):
    row, col = positions[idx]
    ax = fig.add_subplot(gs[row, col])
    
    # Plot with continuous color scale
    gdf.plot(column=var, cmap=cmap, linewidth=0.1, ax=ax,
             edgecolor="gray", legend=True,
             legend_kwds={'label': title, 'orientation': "vertical",
                         'shrink': 0.7, 'pad': 0.02})
    
    ax.set_title(title, fontsize=12, pad=10)
    ax.set_axis_off()

plt.suptitle("SKATER Regionalization vs Key Socioeconomic Indicators", 
             fontsize=16, fontweight='bold', y=0.98)
plt.savefig(os.path.join(OUT_DIR, "skater_vs_ses_comparison.png"), 
            dpi=300, bbox_inches="tight")
print(f"Saved: {os.path.join(OUT_DIR, 'skater_vs_ses_comparison.png')}")

# Create second figure: Side-by-side comparison for each variable
for var, title, cmap in comparison_vars:
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(18, 8))
    
    # SKATER clusters
    gdf.plot(column="skater_90", categorical=True, legend=False,
             linewidth=0.2, edgecolor="black", ax=ax1, cmap="tab20c")
    ax1.set_title(f"SKATER Clusters (k=90)", fontsize=13, fontweight='bold')
    ax1.set_axis_off()
    
    # SES variable
    gdf.plot(column=var, cmap=cmap, linewidth=0.1, ax=ax2,
             edgecolor="gray", legend=True,
             legend_kwds={'label': title, 'shrink': 0.8})
    ax2.set_title(title, fontsize=13, fontweight='bold')
    ax2.set_axis_off()
    
    var_clean = var.replace("_", "").replace(".", "")
    filename = f"skater_vs_{var_clean}_comparison.png"
    plt.suptitle(f"Spatial Clustering vs {title}", fontsize=15, fontweight='bold')
    plt.tight_layout()
    plt.savefig(os.path.join(OUT_DIR, filename), dpi=300, bbox_inches="tight")
    print(f"Saved: {os.path.join(OUT_DIR, filename)}")
    plt.close()

print("All comparison maps created successfully!")
