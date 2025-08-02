import pandas as pd
from src.sources import source, json_source

disease_url = "https://docs.google.com/spreadsheets/d/1I4FHncl40_xx1Udc_Q2rWWWvpL6xaMlpJyY90WBftag/export?format=csv&gid=1196270347"
df_disease = pd.read_csv(disease_url)
df_disease.head()

def row_to_disease(row):
  return     {
    "name": row.get("Name"),
    "source": json_source,
    "entries": [
      row.get("Symptoms"),
      row.get("In-Game Effects"),
      row.get("Cure"),
      row.get("Prognosis"),
    ],
    "page": 0,
  }

disease_list = [
  row_to_disease(row)
  for index, row in df_disease.iterrows()
  if pd.notnull(row.get("Name"))
]
