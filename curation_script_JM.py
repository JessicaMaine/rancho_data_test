# GEO Data Curation Script for GSE144259 (CRC RNA-seq)
import re
import os
import pandas as pd
import numpy as np
import urllib.request
import gzip
from io import StringIO
import urllib.request

# Step 1: Setup
gse_id = "GSE144259"
data_dir = "./data"
os.makedirs(data_dir, exist_ok=True)

# File paths and URLs
fpkm_filename = f"{gse_id}_all.fpkm.exp.txt.gz"
fpkm_path = os.path.join(data_dir, fpkm_filename)
fpkm_url = f"https://ftp.ncbi.nlm.nih.gov/geo/series/GSE144nnn/{gse_id}/suppl/{fpkm_filename}"

# Step 2: Download FPKM matrix if not already downloaded
if not os.path.exists(fpkm_path):
    print(f"⬇️ Downloading {fpkm_filename}...")
    urllib.request.urlretrieve(fpkm_url, fpkm_path)
else:
    print(f"📂 {fpkm_filename} already exists.")

# Step 3: Load FPKM expression matrix
with gzip.open(fpkm_path, 'rt') as f:
    fpkm_df = pd.read_csv(f, sep="\t")

# Step 4: Tidy the data
fpkm_df = fpkm_df.rename(columns={"GeneID": "GENE_SYMBOL"})
fpkm_long = fpkm_df.melt(id_vars=["GENE_SYMBOL"], var_name="Sample_ID", value_name="Result")

# Step 5: Parse Sample_ID into Patient_ID and Pathology
def parse_sample(sample_id):
    match = re.match(r"(CRC\d+)([NTM])", sample_id)
    if match:
        patient_id = match.group(1)
        tissue_code = match.group(2)
        if tissue_code == "N":
            path = "NORMAL"
        elif tissue_code == "T":
            path = "PRIMARY"
        elif tissue_code == "M":
            path = "METASTATIC"
        else:
            path = "NA"
        return patient_id, path
    return "NA", "NA"

parsed = fpkm_long["Sample_ID"].apply(parse_sample)
fpkm_long[["PATIENT_ID", "SAMPLE_GENERAL_PATHOLOGY"]] = pd.DataFrame(parsed.tolist(), index=fpkm_long.index)

# Step 6: Add curation fields
fpkm_long["STUDY_ID"] = gse_id
fpkm_long["UNIQUE_PATIENT_ID"] = fpkm_long["STUDY_ID"] + "_" + fpkm_long["Sample_ID"]
fpkm_long["SEX"] = "NA"   # Placeholder — not provided in metadata
fpkm_long["AGE"] = "NA"   # Placeholder — not provided in metadata
fpkm_long["MATERIAL_TYPE"] = "RNA"
fpkm_long["RESULT_UNITS"] = "FPKM"
fpkm_long["STATUS"] = "NA"

# Step 7: Final column ordering
final_df = fpkm_long[[
    "STUDY_ID", "PATIENT_ID", "UNIQUE_PATIENT_ID", "SEX", "AGE", "Sample_ID",
    "SAMPLE_GENERAL_PATHOLOGY", "MATERIAL_TYPE", "GENE_SYMBOL", "Result", "RESULT_UNITS", "STATUS"
]]
final_df.columns = final_df.columns.str.upper()
final_df.fillna("NA", inplace=True)

# Step 8: Export
output_file = "curated_data.csv"
final_df.to_csv(output_file, index=False)
print(f"✅ Saved {output_file}")

#### ***** Seems to be missing age and sex data 

# Step 1: Set GSM accession
gsm_id = "GSM4284531"
url = f"https://www.ncbi.nlm.nih.gov/geo/tools/geometa.cgi?acc={gsm_id}&scope=full&mode=soft"

# Step 2: Download SOFT text content
response = urllib.request.urlopen(url)
lines = [line.decode("utf-8").strip() for line in response.readlines()]

# Step 3: Extract metadata fields
title = ""
characteristics = []
organism = ""
platform = ""
library_strategy = ""
instrument_model = ""

for line in lines:
    if line.startswith("!Sample_title"):
        title = line.split("=", 1)[1].strip()
    elif line.startswith("!Sample_characteristics_ch1"):
        characteristics.append(line.split("=", 1)[1].strip())
    elif line.startswith("!Sample_organism_ch1"):
        organism = line.split("=", 1)[1].strip()
    elif line.startswith("!Sample_platform_id"):
        platform = line.split("=", 1)[1].strip()
    elif line.startswith("!Sample_library_strategy"):
        library_strategy = line.split("=", 1)[1].strip()
    elif line.startswith("!Sample_instrument_model"):
        instrument_model = line.split("=", 1)[1].strip()

# Step 4: Print extracted metadata
print("Sample Metadata Summary")
print("-" * 40)
print(f"Sample ID       : {gsm_id}")
print(f"Title           : {title}")
print(f"Organism        : {organism}")
print(f"Platform        : {platform}")
print(f"Library Strategy: {library_strategy}")
print(f"Instrument Model: {instrument_model}")
print("\nCharacteristics:")
for char in characteristics:
    print(f" - {char}")

# Step 5: Check for missing fields
has_age = any("age" in c.lower() for c in characteristics)
has_sex = any("sex" in c.lower() or "gender" in c.lower() for c in characteristics)
has_patient = any("patient" in c.lower() for c in characteristics)

print("\n Field Availability Check")
print("-" * 40)
print(f"Sex Found       : {'True' if has_sex else 'NA'}")
print(f"Age Found       : {'True' if has_age else 'NA'}")
print(f"Patient ID Found: {'True' if has_patient else 'NA'}")

if not any([has_age, has_sex, has_patient]):
    print("\nNo demographic (sex, age) or patient-level metadata found.")