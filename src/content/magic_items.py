import pandas as pd
from src.sources import source, json_source
from src.image_generator import generate_icon
import inflection

magic_items_url = "https://docs.google.com/spreadsheets/d/1I4FHncl40_xx1Udc_Q2rWWWvpL6xaMlpJyY90WBftag/export?format=csv&gid=695912920"
df_magic_items = pd.read_csv(magic_items_url)
df_magic_items.head()


def row_to_magic_item(row):
    properties = row.get("Property") if not pd.isnull(row.get("Property")) else []
    attached_spells = (
        row.get("Attached Spells") if not pd.isnull(row.get("Attached Spells")) else []
    )
    item = {
        "name": row.get("Name", "Magic Item"),
        "source": json_source,
        "type": row.get("Type ABRV", "") or "OTH",
        "rarity": row.get("Rarity", "").lower(),
        "value": row.get("Value", ""),
        "weight": row.get("Weight", ""),
        "page": 0,
        # "currencyConversion": "credit",
        "wondrous": True,
        **(
            {"recharge": row.get("Recharge", "")}
            if not pd.isnull(row.get("Recharge"))
            else {}
        ),
        **(
            {"reqAttunement": row.get("Require Attunement", "")}
            if not pd.isnull(row.get("Require Attunement"))
            else {}
        ),
        **(
            {"attachedSpells": [spell for spell in attached_spells.split(", ")]}
            if not pd.isnull(row.get("Attached Spells"))
            else {}
        ),
        **(
            {"baseItem": row.get("Base Item", "")}
            if not pd.isnull(row.get("Base Item"))
            else {}
        ),
        **({"tier": row.get("Tier", "")} if not pd.isnull(row.get("Tier")) else {}),
        **(
            {"weaponCategory": row.get("Category", "")}
            if not pd.isnull(row.get("Category"))
            else {}
        ),
        **(
            {"properties": [f"VS{property[2:]}" for property in properties]}
            if not pd.isnull(row.get("Property"))
            else {}
        ),
        **(
            {"dmg1": row.get("Damage 1", "")}
            if not pd.isnull(row.get("Damage 1"))
            else {}
        ),
        **(
            {"dmg2": row.get("Damage 2", "")}
            if not pd.isnull(row.get("Damage 2"))
            else {}
        ),
        **(
            {"dmgType": row.get("Damage Type", "")}
            if not pd.isnull(row.get("Damage Type"))
            else {}
        ),
        **(
            {"range": row.get("Extracted Range", "")}
            if not pd.isnull(row.get("Extracted Range"))
            else {}
        ),
        **(
            {
                "entries": [row.get("Description", "")],
            }
            if not pd.isnull(row.get("Description"))
            else {}
        ),
        # "images": [
        #   {
        #     "type": "image",
        #     "href": {
        #       "type": "external",
        #       "url": generate_icon("Magic Item", row.get("Name", "Magic Item"))
        #     }
        #   }
        # ]
    }
    return item


magic_items_list = [
    row_to_magic_item(row)
    for index, row in df_magic_items.iterrows()
    if pd.notnull(row.get("Name"))
    and str(row.get("Name")).strip() != ""
    and row.get("Source") == source
]
