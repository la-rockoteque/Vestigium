import pandas as pd
from src.sources import source, json_source

background_url = "https://docs.google.com/spreadsheets/d/1I4FHncl40_xx1Udc_Q2rWWWvpL6xaMlpJyY90WBftag/export?format=csv&gid=1186398440"
df_background = pd.read_csv(background_url)
df_background.head()

background_list = [
    {
        "name": row.get("Background"),
        "source": json_source,
        **({
               "skillProficiencies": [
                   {skill.lower(): True for skill in row.get("Skills").split(", ")}
               ]
           } if pd.notnull(row.get("Skills")) and row.get("Skills") else {}),
        "entries": [
            {
                "type": "list",
                "style": "list-hang-notitle",
                "items": [
                    *([{
                        "type": "item",
                        "name": "Skill Proficiencies",
                        "entry": ", ".join(
                            f"{{@skill {skill}}}"
                            for skill in row.get("Skills").split(", ")
                        ),
                    }] if pd.notnull(row.get("Skills")) and row.get("Skills") else []),
                    *([{
                        "type": "item",
                        "name": "Tool Proficiencies",
                        "entry": row.get("Tools"),
                    }] if pd.notnull(row.get("Tools")) and row.get("Tools") else []),
                    *([{
                         "type": "item",
                         "name": "Languages",
                         "entry": ", ".join(
                                 f"{{@language {language}}}"
                                 for language in row.get("Languages").split(", ")
                             ),
                     }] if pd.notnull(row.get("Languages")) else []),
                    *([{
                        "type": "item",
                        "name": "Equipment",
                        "entry": ", ".join(row.get("Items").split(", ")),
                    }] if pd.notnull(row.get("Items")) and row.get("Items") else []),
                ],
            },
            *([{
                "name": row.get("Feature Name"),
                "type": "entries",
                "entries": [row.get("Feature")],
                "data": {"isFeature": True},
            }] if pd.notnull(row.get("Feature Name")) else []),
        ],
        **({
            "startingEquipment": [
                {"_": [{"special": item} for item in row.get("Starting Equipment").split(", ")]}
            ]
        } if pd.notnull(row.get("Starting Equipment")) and row.get("Starting Equipment") else {}),
    }
    for index, row in df_background.iterrows()
    if pd.notnull(row.get("Background")) and row.get("Source") == source
]
