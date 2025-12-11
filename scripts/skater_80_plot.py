import os
import geopandas as gpd
import matplotlib
matplotlib.use("Agg")  # no GUI
import matplotlib.pyplot as plt

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT_DIR = os.path.join(BASE_DIR, "output")

shp_path = os.path.join(OUT_DIR, "cook_bg_skater_60_90.shp")  # adjust if different
gdf = gpd.read_file(shp_path)

col = "skater_90"

fig, ax = plt.subplots(1, 1, figsize=(8, 8))
gdf.plot(column=col, categorical=True, legend=False, linewidth=0.1,
         edgecolor="black", ax=ax)
ax.set_axis_off()
ax.set_title("SKATER Regions (k = 90)", fontsize=14)

out_png = os.path.join(OUT_DIR, "map_skater_90.png")
plt.savefig(out_png, dpi=300, bbox_inches="tight")
print("Saved:", out_png)
