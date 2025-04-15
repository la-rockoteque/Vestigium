import pandas as pd
from src.sources import source, json_source
conditions_url = "https://docs.google.com/spreadsheets/d/1I4FHncl40_xx1Udc_Q2rWWWvpL6xaMlpJyY90WBftag/export?format=csv&gid=1321788284"
df_condition = pd.read_csv(conditions_url)
df_condition.head()

condition_list = [
  {
    "name": row.get("Condition Name"),
    "source": json_source,
    "entries": [
      *row.get("Condition Text").split(";"),
    ]
  }
  for index, row in df_condition.iterrows()
  if pd.notnull(row.get("Condition Name"))
]