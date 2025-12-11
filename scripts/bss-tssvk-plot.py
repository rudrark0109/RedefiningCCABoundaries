import os
import pandas as pd
import matplotlib
matplotlib.use("Agg")  
import matplotlib.pyplot as plt

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT_DIR = os.path.join(BASE_DIR, "output")
metrics_path = os.path.join(OUT_DIR, "skater_metrics_60_90.csv")

df = pd.read_csv(metrics_path) 

plt.figure()
plt.plot(df["n_clusters"], df["BSS_TSS"], marker="o")
plt.xlabel("Number of regions (k)")
plt.ylabel("BSS/TSS")
plt.title("SES separation vs number of regions (SKATER)")
plt.grid(True)
plt.savefig(os.path.join(OUT_DIR, "bss_tss_vs_k.png"), dpi=300, bbox_inches="tight")
