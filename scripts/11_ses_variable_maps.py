import os
import geopandas as gpd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT_DIR = os.path.join(BASE_DIR, "output")

print("Creating Individual SES Variable Maps...")

# Read shapefile
shp_path = os.path.join(OUT_DIR, "cook_bg_skater_60_90.shp")
gdf = gpd.read_file(shp_path)

# Select variables to map
map_vars = [
    ("poverty_ra", "Poverty Rate (%)", "RdYlGn_r"),
    ("median_hh_", "Median Household Income ($)", "RdYlGn"),
    ("pct_ba_plu", "% Bachelor's Degree+", "Blues"),
    ("unemployme", "Unemployment Rate (%)", "Reds"),
    ("pct_white_", "% White (Non-Hispanic)", "Purples"),
    ("pct_black_", "% Black (Non-Hispanic)", "Oranges")
]

# Create figure with subplots
fig, axes = plt.subplots(2, 3, figsize=(20, 14))
axes = axes.flatten()

for idx, (var, title, cmap) in enumerate(map_vars):
    ax = axes[idx]
    
    # Plot
    gdf.plot(column=var, cmap=cmap, linewidth=0.1, ax=ax,
             edgecolor="gray", legend=True,
             legend_kwds={'label': title, 'orientation': "horizontal",
                         'shrink': 0.8, 'pad': 0.05})
    
    ax.set_title(title, fontsize=12, pad=10)
    ax.set_axis_off()

plt.suptitle("Socioeconomic Variables Across Cook County Block Groups", 
             fontsize=16, y=0.98)
plt.tight_layout()
plt.savefig(os.path.join(OUT_DIR, "ses_variables_maps.png"), dpi=300, bbox_inches="tight")
print(f"Saved: {os.path.join(OUT_DIR, 'ses_variables_maps.png')}")
