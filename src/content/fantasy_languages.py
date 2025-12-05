import pandas as pd
from src.sources import source, json_source
import inflection

languages_url = "https://docs.google.com/spreadsheets/d/1NBZGu29IfE1ZfAWO1Z6ShR5GMLMMbaSyS0m-46PSYm4/export?format=csv&gid=163123529"
df_language = pd.read_csv(languages_url)
df_language.head()

language_list = [
    {
        "name": row.get("Name"),
        "source": json_source,
        "type": row.get("Type").lower(),
        **(
            {
                "typicalSpeakers": [
                    f"{{@filter {inflection.pluralize(speaker)}|bestiary|type=humanoid|tag= any race;{speaker}}}"
                    for speaker in row.get("Races").split(", ")
                ]
            }
            if pd.notnull(row.get("Races"))
            else {}
        ),
        **(
            {"script": row.get("Script").lower()}
            if pd.notnull(row.get("Script"))
            else {}
        ),
        "page": 0,
        "entries": [
            row.get("Description"),
        ],
    }
    for index, row in df_language.iterrows()
    if pd.notnull(row.get("Name"))
]
