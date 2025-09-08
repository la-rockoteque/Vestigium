import pandas as pd
from src.sources import source, json_source
import inflection
import re
import json

monster_url = "https://docs.google.com/spreadsheets/d/1I4FHncl40_xx1Udc_Q2rWWWvpL6xaMlpJyY90WBftag/export?format=csv&gid=736393386"
df_monster = pd.read_csv(monster_url)
df_monster.head()

def parse_entries(raw_text):
  pattern = re.compile(r"([A-Z][^.]+?)\.\s+(.*?)(?=(?:[A-Z][^.]+?\.)|$)", re.S)
  entries = []

  for match in pattern.finditer(raw_text):
    name = match.group(1).strip()
    entry = match.group(2).strip().replace("\n", " ")
    entries.append({
      "name": name,
      "entries": [entry]
    })
  return entries

def parse_saves(raw_text):
  # Regex to match things like STR +13
  pattern = re.compile(r"([A-Z]{3})\s*([+-]\d+)")
  saves = {}

  # Map abbreviations to lowercase keys
  key_map = {
    "STR": "str",
    "DEX": "dex",
    "CON": "con",
    "INT": "int",
    "WIS": "wis",
    "CHA": "cha"
  }

  for stat, value in pattern.findall(raw_text):
    if stat in key_map:
      saves[key_map[stat]] = value

  return saves

def parse_skills(text):
  # Regex to capture "SkillName +Number"
  pattern = re.compile(r"([A-Za-z]+)\s*([+-]\d+)")
  # Normalize to lowercase
  skills = {skill.lower(): value for skill, value in pattern.findall(text)}
  return skills

def row_to_monster(row):
    languages = (
        row.get("Languages").lower().split(", ")
        if pd.notnull(row.get("Languages"))
        else []
    )
    return {
        "source": json_source,
        "name": row.get("Name"),
        "size": [row.get("Size")[:1].upper()],
        "type": row.get("Type").lower(),
        "alignment": [row.get("Alignment")[:1].upper()],
        "ac": [{
          "ac": row.get("Armor Class"),
          "from": [row.get("Armor Type")],
        }],
        "hp": {
            "average": row.get("Hit Points"),
            "formula": f"{row.get('Hit Dice').lower()} + {row.get('CON Mod')}",
        },
        "save:": parse_saves(row.get("Saving Throws")),
        "passive": row.get("Passive Perception"),
        "speed": {
            **(
                {"walk": row.get("Speed (Walking)")}
                if pd.notnull(row.get("Speed (Walking)"))
                else {}
            ),
            **(
                {"fly": row.get("Speed (Flying)")}
                if pd.notnull(row.get("Speed (Flying)"))
                else {}
            ),
            **(
                {"swim": row.get("Speed (Swimming)")}
                if pd.notnull(row.get("Speed (Swimming)"))
                else {}
            ),
            **(
                {"burrow": row.get("Speed (Burrowing)")}
                if pd.notnull(row.get("Speed (Burrowing)"))
                else {}
            ),
        },
        "str": row.get("STR"),
        "dex": row.get("DEX"),
        "con": row.get("CON"),
        "int": row.get("INT"),
        "wis": row.get("WIS"),
        "cha": row.get("CHA"),
        "actions": parse_entries(row.get("Actions")),
        "traits": parse_entries(row.get("Traits")),
        "skills": parse_skills(row.get("Skills")),
        **(
          {"immnue": row.get("Damage Immunities").lower().split(", ")}
          if pd.notnull(row.get("Damage Immunities"))
          else {}
        ),
        **(
            {"conditionImmune": row.get("Condition Immunities").lower().split(", ")}
            if pd.notnull(row.get("Condition Immunities"))
            else {}
        ),
        # **({"languages":
        #       (languages[0] if len(languages) == 1 else languages[0])
        # } if pd.notnull(row.get("Languages")) else {}),
        "cr": f"{row.get('CR (Challenge Rating)')}",
        "fluff": {
          "entries": [
            row.get("Description")
          ],
      }
    }


monster_list = [
    row_to_monster(row)
    for index, row in df_monster.iterrows()
    if pd.notnull(row.get("Name")) and row.get("Source") == source
]
