import pandas as pd
from src.sources import source, json_source

background_url = "https://docs.google.com/spreadsheets/d/1I4FHncl40_xx1Udc_Q2rWWWvpL6xaMlpJyY90WBftag/export?format=csv&gid=1186398440"
df_background = pd.read_csv(background_url)
df_background.head()

background_list = [
    {
        "name": row.get("Background"),
        "source": json_source,
        "skillProficiencies": [
            {skill.lower(): True for skill in row.get("Skills").split(", ")}
        ],
        "entries": [
            {
                "type": "list",
                "style": "list-hang-notitle",
                "items": [
                    {
                        "type": "item",
                        "name": "Skill Proficiencies",
                        "entry": ", ".join(
                            [
                                f"{{@skill {skill}}}"
                                for skill in row.get("Skills").split(", ")
                            ]
                        ),
                    },
                    {
                        "type": "item",
                        "name": "Tool Proficiencies",
                        "entry": row.get("Tools"),
                    },
                    {
                        "type": "item",
                        "name": "Languages",
                        "entry": ", ".join(
                            [
                                f"{{@language {language}}}"
                                for language in row.get("Languages").split(", ")
                            ]
                        ),
                    },
                    {
                        "type": "item",
                        "name": "Equipment",
                        "entry": "A small banner with your symbol of nobility, a scroll of pedigree, an item you always carry on you with a symbol of your nobility or family, a set of fine travel clothes, a set of meditation clothes, and a purse containing 25 gold.",
                    },
                ],
            },
            {
                "name": "Samuraihood:",
                "type": "entries",
                "entries": [
                    "Samurai are a different class of nobility from others, with their own hierarchy and structure. Others tend to view them with respect, acting as stalwart judges and defenders of the people, though some can become terrifying in their cold logic and strict lawfulness.",
                    "You may consider adding to your equipment a small banner carrying a symbol of your nobility, such as a sheet of paper with a crest drawn in ink or a wooden scroll with a crest burned into the surface. You may also consider noting that one piece of your equipment is embellished with the same symbol, or a more personal one, such as a crest on your chest armor or hilt of your sword.",
                    "You may choose to take the Judgement of the Wise feature over the Position of Privilege.",
                ],
            },
            {
                "name": row.get("Feature Name"),
                "type": "entries",
                "entries": [row.get("Feature")],
                "data": {"isFeature": True},
            },
        ],
        "startingEquipment": [
            {"_": [{"special": item} for item in row.get("Items").split(", ")]}
        ],
    }
    for index, row in df_background.iterrows()
    if pd.notnull(row.get("Background")) and row.get("Source") == source
]
