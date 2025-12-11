import os
import numpy as np
import pandas as pd
import geopandas as gpd

# -----------------------------------------------------------------------------
# Paths
# -----------------------------------------------------------------------------
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_DIR = os.path.join(BASE_DIR, "data")
SHAPE_DIR = os.path.join(BASE_DIR, "shapefiles")
OUT_DIR = os.path.join(BASE_DIR, "output")
os.makedirs(OUT_DIR, exist_ok=True)

print("="*80)
print("ACS 2020 & TIGER/Line Data Extraction Pipeline")
print("="*80)
print(f"Base Directory: {BASE_DIR}")
print(f"Data Directory: {DATA_DIR}")
print(f"Shapefile Directory: {SHAPE_DIR}")
print(f"Output Directory: {OUT_DIR}\n")

# -----------------------------------------------------------------------------
# Helper: read an ACS table
# -----------------------------------------------------------------------------
def read_acs_table(filename, id_col="GEO_ID"):
    path = os.path.join(DATA_DIR, filename)
    df = pd.read_csv(path, dtype=str)
    print(f"Reading {filename}... ✓ ({len(df)} rows)")
    return df

# -----------------------------------------------------------------------------
# 1. Read ACS tables
# -----------------------------------------------------------------------------
b03002 = read_acs_table("ACSDT5Y2020.B03002-Data.csv")   # race/ethnicity
b19013 = read_acs_table("ACSDT5Y2020.B19013-Data.csv")   # income
b17021 = read_acs_table("ACSDT5Y2020.B17021-Data.csv")   # poverty
b15003 = read_acs_table("ACSDT5Y2020.B15003-Data.csv")   # education
b23025 = read_acs_table("ACSDT5Y2020.B23025-Data.csv")   # labor
b25003 = read_acs_table("ACSDT5Y2020.B25003-Data.csv")   # tenure
b01001 = read_acs_table("ACSDT5Y2020.B01001-Data.csv")   # age (optional)

# All have GEO_ID like '1500000US170318391001'
for df in [b03002, b19013, b17021, b15003, b23025, b25003, b01001]:
    df["GEOID"] = df["GEO_ID"].str.replace("1500000US", "", regex=False)

# -----------------------------------------------------------------------------
# 2. Filter to Cook County (state 17, county 031 → prefix 17031)
# -----------------------------------------------------------------------------
def filter_cook(df):
    out = df[df["GEOID"].str.startswith("17031")].copy()
    return out

b03002 = filter_cook(b03002)
b19013 = filter_cook(b19013)
b17021 = filter_cook(b17021)
b15003 = filter_cook(b15003)
b23025 = filter_cook(b23025)
b25003 = filter_cook(b25003)
b01001 = filter_cook(b01001)

print("\nCook County block groups per table:")
print(f"  B03002: {len(b03002)}")
print(f"  B19013: {len(b19013)}")
print(f"  B17021: {len(b17021)}")
print(f"  B15003: {len(b15003)}")
print(f"  B23025: {len(b23025)}")
print(f"  B25003: {len(b25003)}")
print(f"  B01001: {len(b01001)}")

# -----------------------------------------------------------------------------
# 3. Select needed columns and rename
#    NOTE: column names follow Census API naming; adjust if yours differ.
# -----------------------------------------------------------------------------

# --- Race / Ethnicity (B03002) ---
race_cols = {
    "GEOID": "GEOID",
    "B03002_001E": "total_pop",
    "B03002_003E": "white_nh",
    "B03002_004E": "black_nh",
    "B03002_006E": "asian_nh",
    "B03002_012E": "hispanic"
}
race = b03002[list(race_cols.keys())].rename(columns=race_cols)

# --- Income (B19013) ---
income = b19013[["GEOID", "B19013_001E"]].rename(
    columns={"B19013_001E": "median_hh_income"}
)

# --- Poverty (B17021) ---
poverty = b17021[["GEOID", "B17021_001E", "B17021_002E"]].rename(
    columns={
        "B17021_001E": "poverty_universe",
        "B17021_002E": "poverty_below"
    }
)

# --- Education (B15003) ---
# BA+ is sum of 022–025 (bachelor, master, professional, doctorate)
edu_cols = ["GEOID", "B15003_001E",
            "B15003_022E", "B15003_023E", "B15003_024E", "B15003_025E"]
edu = b15003[edu_cols].copy()
edu = edu.rename(columns={"B15003_001E": "edu_total_25plus"})
edu["edu_ba_plus_raw"] = (
    edu["B15003_022E"].astype(str) + "," +  # temp, numeric later
    edu["B15003_023E"].astype(str) + "," +
    edu["B15003_024E"].astype(str) + "," +
    edu["B15003_025E"].astype(str)
)

# --- Labor (B23025) ---
labor = b23025[["GEOID", "B23025_001E", "B23025_005E"]].rename(
    columns={
        "B23025_001E": "labor_force",
        "B23025_005E": "unemployed"
    }
)

# --- Tenure (B25003) ---
tenure = b25003[["GEOID", "B25003_001E", "B25003_002E", "B25003_003E"]].rename(
    columns={
        "B25003_001E": "tenure_total_occ",
        "B25003_002E": "owner_occ",
        "B25003_003E": "renter_occ"
    }
)

# --- Age (B01001) optional ---
# under 18: B01001_003E–B01001_020E (roughly), 65+: B01001_020E+ (simplified)
age = b01001[["GEOID", "B01001_001E"]].rename(
    columns={"B01001_001E": "age_total"}
)

# (we'll skip detailed age breakdown for now to keep script simple)

# -----------------------------------------------------------------------------
# 4. Merge all attribute tables on GEOID
# -----------------------------------------------------------------------------
master = race.merge(income, on="GEOID", how="left")
master = master.merge(poverty, on="GEOID", how="left")
master = master.merge(edu[["GEOID", "edu_total_25plus",
                           "B15003_022E", "B15003_023E",
                           "B15003_024E", "B15003_025E"]],
                      on="GEOID", how="left")
master = master.merge(labor, on="GEOID", how="left")
master = master.merge(tenure, on="GEOID", how="left")
master = master.merge(age, on="GEOID", how="left")

print(f"\nMerged attribute dataframe shape: {master.shape}")

# -----------------------------------------------------------------------------
# 5. Convert to numeric (fix your earlier error)
# -----------------------------------------------------------------------------
num_cols = [c for c in master.columns if c != "GEOID"]
for c in num_cols:
    master[c] = pd.to_numeric(
        master[c].astype(str).str.replace(",", ""),
        errors="coerce"
    )

# Recompute BA+ (now numeric)
master["ba_plus"] = (
    master["B15003_022E"].fillna(0) +
    master["B15003_023E"].fillna(0) +
    master["B15003_024E"].fillna(0) +
    master["B15003_025E"].fillna(0)
)

# -----------------------------------------------------------------------------
# 6. Safe division helper + SES variables
# -----------------------------------------------------------------------------
def safe_div(num, den):
    den = den.replace({0: np.nan})
    return num / den

print("\nCalculating percentages and rates...")

# Race percentages
master["pct_white_nh"] = safe_div(master["white_nh"], master["total_pop"]) * 100
master["pct_black_nh"] = safe_div(master["black_nh"], master["total_pop"]) * 100
master["pct_asian_nh"] = safe_div(master["asian_nh"], master["total_pop"]) * 100
master["pct_hispanic"] = safe_div(master["hispanic"], master["total_pop"]) * 100

# Poverty rate
master["poverty_rate"] = safe_div(master["poverty_below"],
                                  master["poverty_universe"]) * 100

# Education % BA+
master["pct_ba_plus"] = safe_div(master["ba_plus"],
                                 master["edu_total_25plus"]) * 100

# Unemployment rate
master["unemployment_rate"] = safe_div(master["unemployed"],
                                       master["labor_force"]) * 100

# Tenure
master["pct_owner"] = safe_div(master["owner_occ"],
                               master["tenure_total_occ"]) * 100
master["pct_renter"] = safe_div(master["renter_occ"],
                                master["tenure_total_occ"]) * 100

# (Optional) we’re not computing age shares here to keep it short.

# -----------------------------------------------------------------------------
# 7. Keep only needed final columns
# -----------------------------------------------------------------------------
final_cols = [
    "GEOID",
    "total_pop",
    "pct_white_nh", "pct_black_nh", "pct_asian_nh", "pct_hispanic",
    "median_hh_income",
    "poverty_rate",
    "pct_ba_plus",
    "unemployment_rate",
    "pct_owner", "pct_renter"
]
master_final = master[final_cols].copy()

# -----------------------------------------------------------------------------
# 8. Merge with shapefile
# -----------------------------------------------------------------------------
print("\nReading shapefile...")
shp_path = os.path.join(SHAPE_DIR, "tl_2020_17_bg.shp")
gdf = gpd.read_file(shp_path)

print(f"Shapefile rows (Illinois BGs): {len(gdf)}")

# GEOID is already in tl_2020_17_bg as 12-digit
gdf_cook = gdf[gdf["COUNTYFP"] == "031"].copy()
print(f"Shapefile rows (Cook County BGs): {len(gdf_cook)}")

gdf_merged = gdf_cook.merge(master_final, on="GEOID", how="left")
print(f"Merged GeoDataFrame rows: {len(gdf_merged)}")

# -----------------------------------------------------------------------------
# 9. Save outputs
# -----------------------------------------------------------------------------
csv_out = os.path.join(OUT_DIR, "cook_bg_acs2020_ses.csv")
shp_out = os.path.join(OUT_DIR, "cook_bg_acs2020_ses.shp")

master_final.to_csv(csv_out, index=False)
# keep Cook County only: GEOID starts with '17031'
master_final = master_final[master_final["GEOID"].str.startswith("17031")].copy()
print("Rows in master_final (Cook only):", len(master_final))

gdf_merged.to_file(shp_out)

print(f"\nSaved attribute CSV to: {csv_out}")
print(f"Saved SES shapefile to: {shp_out}")
print("\nDone.")
