import pandas as pd
from src.sources import json_source
import re
from fractions import Fraction

monster_url = "https://docs.google.com/spreadsheets/d/1NBZGu29IfE1ZfAWO1Z6ShR5GMLMMbaSyS0m-46PSYm4/export?format=csv&gid=736393386"
df_monster = pd.read_csv(monster_url)
df_monster.head()

def parse_entries(raw_text):
  pattern = re.compile(r"([A-Z][^.]+?)\.\s+(.*?)(?=(?:[A-Z][^.]+?\.)|$)", re.S)
  entries = []

  for text in raw_text.split("\n"):
    name, entry = (text.split(":: ") + ["", ""])[:2]
    entries.append({
      "name": name,
      "entries": [entry]
    })
  return entries

DMG = {
  "acid","cold","fire","force","lightning","necrotic",
  "poison","psychic","radiant","thunder"
}

BPS = {"bludgeoning","piercing","slashing"}

def parse_immunities(raw_text):
  immunities = []
  for immunity in DMG:
    if immunity in raw_text.lower():
      immunities.append(immunity)
      
  if "from" in raw_text.lower():
    special_immunities = []
    fluff = raw_text.split(" from ")[1]
    for immunity in BPS:
      if immunity in raw_text.lower():
        special_immunities.append(immunity)
    immunities.append({
      "immune": special_immunities,
      "note": f"from {fluff.lower()}"
    })

def parse_skills(raw_text):
  # Matches:
  #  - "STR +13"
  #  - "Sleight of Hand +7"
  #  - "Animal Handling -1"
  # Works across commas/newlines: "Perception +4, Stealth +5"
  pattern = re.compile(
    r"(?:^|[,\n;]\s*)"
    r"([A-Z]{3}|[A-Za-z][A-Za-z'/-]*(?:\s+[A-Za-z'/-]+)*)"
    r"\s*([+-]\d+)",
    re.IGNORECASE
  )

  skills = {}
  for m in pattern.finditer(raw_text):
    name = m.group(1).strip().lower()
    skills[name] = m.group(2)
  return skills

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

def row_to_monster(row):
    name = row.get("Name")
    languages = (
        row.get("Languages").lower().split(", ")
        if pd.notnull(row.get("Languages"))
        else []
    )
    return {
        "source": json_source,
        "name": name,
        "size": [row.get("Size")[:1].upper()],
        "type": row.get("Type").lower(),
        "alignment": [row.get("Alignment")[:1].upper()],
        "ac": [{
          "ac": row.get("Armor Class"),
          "from": [row.get("Armor Type") if pd.notnull(row.get("Armor Type"))
          else "natural armor"]
        }],
        "hp": {
            "average": row.get("Hit Points"),
            "formula": f"{row.get('Hit Dice').lower()} + {row.get('CON Mod')}",
        },
        "save": parse_saves(row.get("Saving Throws")),
        "passive": row.get("Passive Perception"),
        "speed": {
            **(
                {"walk": int(row.get("Speed (Walking)"))}
                if pd.notnull(row.get("Speed (Walking)"))
                else {}
            ),
            **(
                {"fly": int(row.get("Speed (Flying)"))}
                if pd.notnull(row.get("Speed (Flying)"))
                else {}
            ),
            **(
                {"swim": int(row.get("Speed (Swimming)"))}
                if pd.notnull(row.get("Speed (Swimming)"))
                else {}
            ),
            **(
                {"burrow": int(row.get("Speed (Burrowing)"))}
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
        **(
          {"action": parse_entries(row.get("Actions"))}
          if pd.notnull(row.get("Actions"))
          else {}
        ),
        **(
          {"reaction": parse_entries(row.get("Reactions"))}
          if pd.notnull(row.get("Reactions"))
          else {}
        ),
        **(
          {
            "legendaryActions": 3,
            "legendaryHeader": [
              f"The {name} can take 3 legendary actions, choosing from the options below. Only one legendary action can be used at a time and only at the end of another creature's turn. The {name} regains spent legendary actions at the start of its turn."
            ],
            "legendary": parse_entries(row.get("Legendary Actions"))
           }
          if pd.notnull(row.get("Legendary Actions"))
          else {}
        ),
        **(
          {"trait": parse_entries(row.get("Traits"))}
          if pd.notnull(row.get("Traits"))
          else {}
        ),
        **(
          {"skill": parse_skills(row.get("Skills"))}
          if pd.notnull(row.get("Skills"))
          else {}
        ),
        **(
          {"immune": parse_immunities(row.get("Damage Immunities"))}
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
        "cr": f"{Fraction(row.get('CR (Challenge Rating)'))}",
        "tokenUrl": row.get("Tokens URL"),
        "fluff": {
          "entries": [
            row.get("Description")
          ],
          "images": [
            {
              "type": "image",
              "href": {
                "type": "external",
                "url": row.get("Image URL"),
              }
            }
          ]
      }
    }


monster_list = [
    row_to_monster(row)
    for index, row in df_monster.iterrows()
    if pd.notnull(row.get("Name"))
]
