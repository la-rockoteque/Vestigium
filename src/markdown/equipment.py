import pandas as pd
from src.sources import source, json_source

items_url = "https://docs.google.com/spreadsheets/d/1I4FHncl40_xx1Udc_Q2rWWWvpL6xaMlpJyY90WBftag/export?format=csv&gid=876046336"
df_items = pd.read_csv(items_url)
df_items.head()

grp = df_items.groupby(by=["Type"])

lines = []

index = 1

def row_to_item(row):
  global index
  image = row.get("Image Url") if pd.notnull(row.get("Image Url")) else ""
  properties = row['Property'] if pd.notnull(row['Property']) else "-"
  line =  [f"|![]({image}) {{width:24px,mix-blend-mode:multiply}}|{row['Name']} | {row['Value']} | {properties} | {row['Weight']} |"]
  if index % 52 == 0:
    line = ["\page",
            "| |Name | Cost | Properties | Weight |",
            "| --- |--- | --- | --- | --- |"
            ] + line
    index += 1
  elif index % 26 == 0:
    line = ["\column",
            "| |Name | Cost | Properties | Weight |",
            "| --- |--- | --- | --- | --- |"
            ] + line
    index += 1
  index += 1
  if len(properties) > 23:
    index += 1
  return "\n".join(line)

for name, groups in grp:
  table = [
    f"### {name[0]} Table",
    "| |Name | Cost | Properties | Weight |",
    "| --- |--- | --- | --- | --- |"
  ] + [
    row_to_item(row) for _, row in groups.iterrows()
    if pd.notnull(row.get("Name"))
       and str(row.get("Name")).strip() != ""
       and row.get("Source") == source
  ]
  lines.append("\n".join(table))

items = "---\n".join(lines)



magic_items_url = "https://docs.google.com/spreadsheets/d/1I4FHncl40_xx1Udc_Q2rWWWvpL6xaMlpJyY90WBftag/export?format=csv&gid=695912920"
df_magic_items = pd.read_csv(magic_items_url)
df_magic_items.head()

m_grp = df_magic_items.groupby(by=["Type"])

magic_items = ""

m_index = 1

def row_to_magic_item(row):
  global m_index
  line = f"""
### *{row.get('Name')}*
*{row.get('Rarity')}, {row.get('value')} credits, {row.get('row.get(weight)')} lbs*  
A **liquid mirror**, reflecting countless shifting faces.
Drinking it allows the user to **fully transform into another humanoid** of their choice for **1 hour**—not just in appearance, but in **memories, voice, and mannerisms**.
At the end of the hour, they must **make a DC 17 Charisma saving throw** or **forget who they originally were** for the next 24 hours, leaving them trapped in their borrowed identity.
"""
  if m_index % 10 == 0:
    line = line +  "\n\page\n"
  m_index += 1
  return line

for name, groups in m_grp:
  item = [
            f"## {name[0]}",
          ] + [
    row_to_magic_item(row) for _, row in groups.iterrows()
            if pd.notnull(row.get("Name"))
               and str(row.get("Name")).strip() != ""
               and row.get("Source") == source
          ]
  magic_items = magic_items + "\n---\n".join(item)
