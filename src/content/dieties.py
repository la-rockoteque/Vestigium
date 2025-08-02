import pandas as pd
from src.sources import source, json_source

diety_url = "https://docs.google.com/spreadsheets/d/1I4FHncl40_xx1Udc_Q2rWWWvpL6xaMlpJyY90WBftag/export?format=csv&gid=1410134136"
df_diety = pd.read_csv(diety_url)
df_diety.head()

def row_to_diety(row):
    return     {
        "name": row.get("Name").lower(),
        "source": json_source,
        "pantheon": "None",
        "symbol": row.get("Symbol"),
        "entries": [
            row.get("Description"),
        ],
        "page": 0,
        "alignment": [row.get("Alignment")[:1].upper()],
        "altNames": row.get("Epithet").split(", ") if pd.notnull(row.get("Epithet")) else [],
        "domains": row.get("Domains").split(", ") if pd.notnull(row.get("Domains")) else [],
        "customProperties": {
            "Plane": row.get("Plane"),
            "Followers": row.get("Followers"),
            "Slogan": row.get("Slogan"),
            "Lore": row.get("Lore"),
            "Quote": row.get("Quote"),
        }
    }

diety_list = [
    row_to_diety(row)
    for index, row in df_diety.iterrows()
    if pd.notnull(row.get("Name")) and row.get("Source") == source
]
