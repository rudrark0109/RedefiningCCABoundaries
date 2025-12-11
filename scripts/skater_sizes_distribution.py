import os
import pandas as pd
import matplotlib
matplotlib.use("Agg")  
import matplotlib.pyplot as plt

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT_DIR = os.path.join(BASE_DIR, "output")
sizes_path = os.path.join(OUT_DIR, "cluster_sizes_90.csv")

sizes = pd.read_csv(sizes_path)  # columns: skater_80, n_bgs, share_of_all

plt.figure()
plt.hist(sizes["n_bgs"], bins=20)
plt.xlabel("Block groups per region")
plt.ylabel("Number of regions")
plt.title("Region size distribution (k = 90)")
plt.savefig(os.path.join(OUT_DIR, "region_size_hist_80.png"), dpi=300, bbox_inches="tight")
