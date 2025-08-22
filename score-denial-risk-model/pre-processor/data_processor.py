import duckdb
import pandas as pd
import ast
import json
from sklearn.model_selection import train_test_split

# === Step 1: Load Claims and CCS Mapping ===
INPUT_CLAIMS_FILE = "data/claim_data.csv"

CCS_FILE_PATH = "data/ccsr_icd10cm_2025_v1.csv"  # Rename to your saved version

ccs_df = pd.read_csv(CCS_FILE_PATH, dtype=str)
ccs_df.columns = [col.strip().strip("'") for col in ccs_df.columns]

ccs_df = pd.DataFrame({
    "icd10": ccs_df["ICD-10-CM CODE"].str.replace(".", "", regex=False).str.upper().str.strip(),
    "ccs_category": ccs_df["CCSR CATEGORY 1"].str.strip().str.strip("'"),
    "ccs_label": ccs_df["CCSR CATEGORY 1 DESCRIPTION"].str.strip()
})

# Load claims
print(f"Loading claims from {INPUT_CLAIMS_FILE}")
df = pd.read_csv(INPUT_CLAIMS_FILE, on_bad_lines='skip')

# === Step 2: Filter Required Columns ===
required = [
    "cpt", "payer", "pos", "duration", "icd_count", "modifier_count",
    "has_modifier_25", "procedures_count", "denied", "primary_icd", "icd_list"
]
missing = [col for col in required if col not in df.columns]
if missing:
    raise ValueError(f"Missing required columns: {missing}")

df = df.dropna(subset=required)
df = df[df["denied"].isin([0, 1])]
df["primary_icd"] = df["primary_icd"].str.replace(".", "").str.upper().str.strip()

# === Step 3: Map Primary ICD to CCS Group ===
df = df.merge(ccs_df[["icd10", "ccs_category", "ccs_label"]],
              left_on="primary_icd", right_on="icd10", how="left")
df = df.rename(columns={"ccs_category": "icd_ccs_id", "ccs_label": "icd_ccs_label"})

# === Step 4: Multi-ICD CCS One-Hot Encoding ===
def extract_ccs_set(icd_raw):
    if pd.isnull(icd_raw): return set()
    try:
        codes = ast.literal_eval(icd_raw) if isinstance(icd_raw, str) else icd_raw
        codes = [code.replace(".", "").upper().strip() for code in codes]
        return set(ccs_df.loc[ccs_df["icd10"].isin(codes), "ccs_label"])
    except Exception:
        return set()

ccs_sets = df["icd_list"].apply(extract_ccs_set)
all_ccs_labels = sorted(set.union(*ccs_sets))

# Create multi-hot CCS group columns
multi_hot_cols = []
for label in all_ccs_labels:
    safe_label = label.lower().replace(" ", "_").replace("-", "_")
    col_name = f"ccs_{safe_label}"
    df[col_name] = ccs_sets.apply(lambda s: 1 if label in s else 0)
    multi_hot_cols.append(col_name)

# Add count of CCS groups per claim
df["ccs_count_per_claim"] = ccs_sets.apply(len)

# Save CCS feature list
with open("ccs_features.json", "w") as f:
    json.dump(multi_hot_cols, f)

# === Step 5: Normalize Data Types ===
df["cpt"] = df["cpt"].astype(str)
df["payer"] = df["payer"].astype(str)
df["pos"] = df["pos"].astype(str)
df["has_modifier_25"] = df["has_modifier_25"].astype(int)
df["modifier_count"] = df["modifier_count"].astype(int)
df["icd_count"] = df["icd_count"].astype(int)
df["procedures_count"] = df["procedures_count"].astype(int)

# === Step 6: Save Intermediate to DuckDB ===
df.to_csv("filtered_claims_with_ccs.csv", index=False)

con = duckdb.connect()
con.execute("""
    CREATE TABLE claims AS 
    SELECT * FROM read_csv_auto('filtered_claims_with_ccs.csv', header=True, sample_size=-1)
""")

# === Step 7: CPT Pairing Column (Guard against missing secondary_cpt) ===
con.execute("""
    CREATE TABLE claims_with_pair AS
    SELECT *,
           CASE
               WHEN 'secondary_cpt' IN (SELECT column_name FROM information_schema.columns WHERE table_name = 'claims')
               AND secondary_cpt IS NOT NULL THEN cpt || '_' || secondary_cpt
               ELSE cpt || '_81001'
           END AS code_pair_combo
    FROM claims
""")

# === Step 8: Calculate Past Denial Rate ===
con.execute("""
    CREATE TABLE denial_stats AS
    SELECT cpt, payer, AVG(denied::INTEGER)::FLOAT AS past_denial_rate
    FROM claims_with_pair
    GROUP BY cpt, payer
""")

# === Step 9: Join Denial Rate Back ===
con.execute("""
    CREATE TABLE enriched_claims AS
    SELECT c.*, d.past_denial_rate
    FROM claims_with_pair c
    LEFT JOIN denial_stats d ON c.cpt = d.cpt AND c.payer = d.payer
""")

# === Step 10: Downsample Balanced Sample (~50K) ===
df_sampled = con.execute("""
    SELECT * FROM (
        SELECT * FROM enriched_claims WHERE denied = 1 USING SAMPLE 20000 ROWS
        UNION ALL
        SELECT * FROM enriched_claims WHERE denied = 0 USING SAMPLE 30000 ROWS
    )
""").fetchdf()

# === Step 11: Train/Val/Test Split ===
train, temp = train_test_split(df_sampled, stratify=df_sampled["denied"], test_size=0.3, random_state=42)
test, val = train_test_split(temp, stratify=temp["denied"], test_size=0.5, random_state=42)

train.to_csv("claims_train.csv", index=False)
test.to_csv("claims_test.csv", index=False)
val.to_csv("claims_val.csv", index=False)

print("ICD10 CCS multi-hot features and pipeline complete")
