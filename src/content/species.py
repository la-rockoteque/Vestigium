import pandas as pd
from src.sources import source, json_source
import inflection

species_url = "https://docs.google.com/spreadsheets/d/1I4FHncl40_xx1Udc_Q2rWWWvpL6xaMlpJyY90WBftag/export?format=csv&gid=993815941"
df_species = pd.read_csv(species_url)
df_species.head()


def row_to_species(row):
    language_known = (
        [f"{{@language {lang}|VSTGCC}}" for lang in row.get("Languages").split(",")]
        if pd.notnull(row.get("Languages"))
        else []
    )
    language_list_pretext = (
        f"and {row.get('Number of Languages')} additional languages"
        if pd.notnull(row.get("Languages"))
        else "You know 2 standard languages of your choice"
    )
    formated_language_known = [language_list_pretext, *language_known]
    language_list = (
        [
            f"{{@language {lang}|VSTGCC}}"
            for lang in row.get("Language Choices").split(",")
        ]
        if pd.notnull(row.get("Language Choices"))
        else []
    )
    language_list_pretext = (
        f"You may choose from the list of"
        if pd.notnull(row.get("Language Choices"))
        else ""
    )
    formated_language_list = [
        language_list_pretext,
        *list(set(language_list) - set(language_known)),
    ]
    exotic_language_known = (
        f"You may choose up to {row.get('Number of Exotic Language')} exotic language instead"
        if pd.notnull(row.get("Number of Exotic Language"))
        else None
    )

    return {
        "name": row.get("Name"),
        **(
            {"traitTags": row.get("Tag").split(", ")}
            if pd.notnull(row.get("Tag"))
            else {}
        ),
        **({"alias": [row.get("Alias")]} if pd.notnull(row.get("Alias")) else {}),
        "source": row.get("Source"),
        "ability": [
            {
                f"{row.get('Ability 1')[:3].lower()}": row.get("Score 1"),
                f"{row.get('Ability 2')[:3].lower()}": row.get("Score 2"),
            }
        ],
        "size": [row.get("Size ABRV")[:1].upper()],
        "speed": {
            "walk": row.get("Walk Speed"),
            **(
                {"fly": row.get("Fly Speed")}
                if pd.notnull(row.get("Fly Speed"))
                else {}
            ),
        },
        "entries": [
            f"{row.get('Name')} Traits",
            {"type": "entries", "name": "Age", "entries": [row.get("Age") if pd.notnull(row.get("Age")) else ""]},
            {"type": "entries", "name": "Size", "entries": [row.get("Size") if pd.notnull(row.get("Size")) else ""]},
            {"type": "entries", "name": "Speed", "entries": [row.get("Speed") if pd.notnull(row.get("Speed")) else ""]},
            {"type": "entries", "name": "Vision", "entries": [row.get("Vision") if pd.notnull(row.get("Vision")) else ""]},
            *(
                {
                    "name": row.get(f"Trait {index}").split("|")[0],
                    "entries": [row.get(f"Trait {index}").split("|")[1]],
                    "type": "entries",
                }
                for index in [1, 2, 3, 4, 5, 6]
                if pd.notnull(row.get(f"Trait {index}"))
            ),
            {
                "name": "Languages",
                "entries": [
                    *(
                        [", ".join(formated_language_known)]
                        if not language_known
                        else []
                    ),
                    *([", ".join(formated_language_list)] if not language_list else []),
                    *(
                        [exotic_language_known]
                        if exotic_language_known is not None
                        else []
                    ),
                ],
                "type": "entries",
            },
        ],
        "languageProficiencies": [
            {
                **(
                    {"any": row.get("Number of Exotic Language")}
                    if pd.notnull(row.get("Number of Exotic Language"))
                    else {}
                ),
                "anyStandard": row.get("Number of Languages"),
            }
        ],
        "fluff": {
            "entries": [
                {
                    "name": col,
                    "entries": [row[col]],
                    "type": "entries",
                }
                for col in df_species.columns[
                    df_species.columns.get_loc("Intro") : df_species.columns.get_loc(
                        "Life in the City"
                    )
                    + 1
                ]
                if pd.notnull(row[col])
            ],
            **(
                {
                    "images": [
                        {
                            "type": "image",
                            "href": {"type": "external", "url": row.get("Image")},
                        }
                    ]
                }
                if pd.notnull(row.get("Image"))
                else {}
            ),
        },
    }


species_list = [
    row_to_species(row)
    for index, row in df_species.iterrows()
    if pd.notnull(row.get("Name"))
]
