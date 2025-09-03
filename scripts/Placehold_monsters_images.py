import pandas as pd
from src.sources import source, json_source
import inflection
import shutil

monster_url = "https://docs.google.com/spreadsheets/d/1I4FHncl40_xx1Udc_Q2rWWWvpL6xaMlpJyY90WBftag/export?format=csv&gid=371472904"
df_monster = pd.read_csv(monster_url)
df_monster.head()


def placehold(row):
  src = f"../images/Monsters/Placeholder.png"
  dst = f"../images/Monsters/{row.get('Name')}.png"
  shutil.copyfile(src, dst)


[
  placehold(row)
  for index, row in df_monster.iterrows()
  if pd.notnull(row.get("Name")) and row.get("Source") == source
]
