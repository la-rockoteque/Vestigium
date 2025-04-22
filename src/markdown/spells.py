import pandas as pd
from src.sources import source, json_source

def row_to_markdown(row):
    spell_name = row["Spell Name"].strip()
    level = row["Level"].strip()
    school = row["School"].strip()
    casting_time = row["Casting Time"].strip()
    spell_range = row["Range"].strip()
    components = row["Components ABVR"] if pd.notna(row["Components ABVR"]) else "V, S, M"
    duration = row["Duration"].strip()
    description = row["Description"].strip()
    # image = row["Image Url"].strip()

    return f"""
#### {spell_name}
*{level} {school}*
**Casting Time:** :: {casting_time}
**Range:**        :: {spell_range}
**Components:**   :: {components}
**Duration:**     :: {duration}

{description}

---
"""

spells_url = "https://docs.google.com/spreadsheets/d/1I4FHncl40_xx1Udc_Q2rWWWvpL6xaMlpJyY90WBftag/export?format=csv&gid=625265890"
df_spells = pd.read_csv(spells_url)
df_spells.head()

spells_list = [
    row_to_markdown(row)
    for index, row in df_spells.iterrows()
    if pd.notnull(row.get("Spell Name")) and str(row.get("Spell Name")).strip() != "" and row.get("Source") == source
]

spells = "\n\n".join(spells_list)