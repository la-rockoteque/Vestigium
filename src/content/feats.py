import pandas as pd
from src.sources import source, json_source

feat_url = "https://docs.google.com/spreadsheets/d/1I4FHncl40_xx1Udc_Q2rWWWvpL6xaMlpJyY90WBftag/export?format=csv&gid=1076107525"
df_feat = pd.read_csv(feat_url)
df_feat.head()

def row_to_feat(row):
    feat_pos = row.index.get_loc("Feat")
    return     {
        "name": row.get("Name").lower(),
        "source": json_source,
        "entries": [
            row.get("Flavor Text"),
            *row.iloc[feat_pos:].dropna().tolist()
        ],
    }

feat_list = [
    row_to_feat(row)
    for index, row in df_feat.iterrows()
    if pd.notnull(row.get("Name")) and row.get("Source") == source
]
