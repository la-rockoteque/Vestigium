import pandas as pd
from src.sources import source, json_source
import inflection

monster_url = "https://docs.google.com/spreadsheets/d/1I4FHncl40_xx1Udc_Q2rWWWvpL6xaMlpJyY90WBftag/export?format=csv&gid=371472904"
df_monster = pd.read_csv(monster_url)
df_monster.head()


def row_to_monster(row):
    languages = (
        row.get("Languages").lower().split(", ")
        if pd.notnull(row.get("Languages"))
        else []
    )
    return {
        "source": json_source,
        "name": f"{row.get("Name")}, {row.get("Variant")}" if pd.notnull(row.get("Variant")) else row.get("Name"),
        "size": [row.get("Size")[:1].upper()],
        "type": row.get("Classic 5e Type").lower(),
        "alignment": [row.get("Alignment")[:1].upper()],
        "ac": [row.get("Armor Class")],
        "hp": {
            "average": row.get("Hit Points"),
            "formula": f"{row.get('Hit Dice').lower()} + {row.get('CON Mod')}",
        },
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
        **(
            {"conditionImmune": row.get("Condition Immunities").lower().split(", ")}
            if pd.notnull(row.get("Condition Immunities"))
            else {}
        ),
        # **({"languages":
        #       (languages[0] if len(languages) == 1 else languages[0])
        # } if pd.notnull(row.get("Languages")) else {}),
        "cr": f"{row.get('CR (Challenge Rating)')}",
    }


monster_list = [
    row_to_monster(row)
    for index, row in df_monster.iterrows()
    if pd.notnull(row.get("Name")) and row.get("Source") == source
]
