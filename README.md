
## GSE144259 GEO Data Curation

This script curates RNA-seq expression data from the GEO study **GSE144259**, which includes colorectal cancer (CRC) tissue samples from three patients (CRC1, CRC2, CRC3), across matched normal, primary tumor, and metastatic tissues.

---

## Files Used

- `GSE144259_all.fpkm.exp.txt.gz`: Expression matrix (FPKM values)  
  Source: [GEO FTP](https://ftp.ncbi.nlm.nih.gov/geo/series/GSE144nnn/GSE144259/suppl/)

- Metadata from GSM4284531: Used to check for demographic fields like sex and age  
  Source: [GEO Metadata Tool](https://www.ncbi.nlm.nih.gov/geo/tools/geometa.cgi?acc=GSM4284531)

---

## Output

### `curated_data.csv`

Long-form gene expression table with the following columns:

| Column                    | Description                                  |
|---------------------------|----------------------------------------------|
| STUDY_ID                  | GEO study ID (GSE144259)                     |
| PATIENT_ID                | CRC1, CRC2, CRC3 (parsed from sample ID)     |
| UNIQUE_PATIENT_ID         | STUDY_ID + Sample ID                         |
| SEX, AGE                  | Not available in this dataset (NA)           |
| SAMPLE_ID                 | e.g. CRC1N, CRC2T, CRC3M                     |
| SAMPLE_GENERAL_PATHOLOGY  | NORMAL, PRIMARY, or METASTATIC               |
| MATERIAL_TYPE             | RNA                                          |
| GENE_SYMBOL               | Gene name/ID                                 |
| RESULT                    | Expression value (FPKM)                      |
| RESULT_UNITS              | FPKM                                         |
| STATUS                    | NA                                           |

---

## Metadata Availability Check

From GSM4284531, the metadata includes tissue info but **does not** include age, sex, or patient ID.

---

## How to Run

```bash
python curate_gse144259.py
```

This will generate the `curated_data.csv` file in your working directory.

