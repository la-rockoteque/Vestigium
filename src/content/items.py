import pandas as pd
from src.sources import source, json_source
import inflection
from src.image_generator import generate_icon
item_properties_url = "https://docs.google.com/spreadsheets/d/1I4FHncl40_xx1Udc_Q2rWWWvpL6xaMlpJyY90WBftag/export?format=csv&gid=1064461316"
df_item_properties = pd.read_csv(item_properties_url)
df_item_properties.head()

def row_to_property(row):
  return {
    "name": row.get("Name", "Generic Property"),
    "abbreviation": f"VS|{row.get("Name", "")[:2]}".upper(),
    "source": json_source,
    **({"entries": [row.get("Entry", "")] } if not pd.isnull(row.get("Entry")) else {}),
  }

item_property_list = [
  row_to_property(row)
  for index, row in df_item_properties.iterrows()
  if pd.notnull(row.get("Name")) and str(row.get("Name")).strip() != ""
]
#%%
items_url = "https://docs.google.com/spreadsheets/d/1I4FHncl40_xx1Udc_Q2rWWWvpL6xaMlpJyY90WBftag/export?format=csv&gid=876046336"
df_items = pd.read_csv(items_url)
df_items.head()

def row_to_item(row):
  properties = row.get("Property") if not pd.isnull(row.get("Property")) else []
  attached_spells = row.get("Attached Spells") if not pd.isnull(row.get("Attached Spells")) else []
  type = row.get("Type ABRV") if not pd.isnull(row.get("Attached Spells")) else "OTH"
  item = {
    "name": row.get("Name", "Generic Item"),
    "source": "VestigiumGuidetoConcordCity",
    "type": type,
    "rarity": row.get("Rarity", ""),
    "value": row.get("Value", ""),
    "weight": row.get("Weight", ""),
    "page": row.get("Page", ""),
    "wondrous": True,
    **({"recharge": row.get("Recharge", "") } if not pd.isnull(row.get("Recharge")) else {}),
    **({"reqAttunement": row.get("Require Attunement", "") } if not pd.isnull(row.get("Require Attunement")) else {}),
    **({"attachedSpells": [
      spell
      for spell in attached_spells.split(", ")
    ]} if not pd.isnull(row.get("Attached Spells")) else {}),
    **({"baseItem": row.get("Base Item", "") } if not pd.isnull(row.get("Base Item")) else {}),
    **({"tier": row.get("Tier", "") } if not pd.isnull(row.get("Tier")) else {}),
    # "currencyConversion": "credit",
    **({"weaponCategory": row.get("Category", "") } if not pd.isnull(row.get("Category")) else {}),
    **({"property": [property for property in properties.split(", ") ]} if not pd.isnull(row.get("Property")) else {}),
    **({"dmg1": row.get("Damage 1", "") } if not pd.isnull(row.get("Damage 1")) else {}),
    **({"dmg2": row.get("Damage 2", "") } if not pd.isnull(row.get("Damage 2")) else {}),
    **({"dmgType": row.get("Damage Type", "") } if not pd.isnull(row.get("Damage Type")) else {}),
    **({"range": row.get("Range", "") } if not pd.isnull(row.get("Range")) else {}),
    **({"bonusWeapon": row.get("Bonus Weapon", "") } if not pd.isnull(row.get("Bonus Weapon")) else {}),
    **({"entries": [
      row.get("Description", "")
    ], } if not pd.isnull(row.get("Description")) else {}),
    # "images": [
    #   {
    #     "type": "image",
    #     "href": {
    #       "type": "external",
    #       "url": generate_icon("Item", row.get("Name", "Magic Item"))
    #     }
    #   }
    # ]
  }
  return item

items_list = [
  row_to_item(row)
  for index, row in df_items.iterrows()
  if pd.notnull(row.get("Name")) and str(row.get("Name")).strip() != "" and row.get("Source") == source
]