import pandas as pd
import inflection
from src.sources import source, json_source

class_features_url = "https://docs.google.com/spreadsheets/d/1I4FHncl40_xx1Udc_Q2rWWWvpL6xaMlpJyY90WBftag/export?format=csv&gid=545140625"


def row_to_feature_entries(row):
    name = row.get("Name")
    classes = inflection.humanize(row.get("Class"))
    parent = row.get("Parent")
    type = row.get("Type", "entries")
    entry = row.get("Entry")
    attribute = row.get("Attributes")

    sub_entries = [
        row_to_feature_entries(entry_row)
        for index, entry_row in df_class_features.iterrows()
        if pd.notnull(entry_row.get("Class"))
        and pd.notnull(entry_row.get("Parent"))
        and str(entry_row.get("Parent")) == name
        and str(entry_row.get("Class")) == classes
        and str(entry_row.get("Parent")) != str(entry_row.get("Name"))
    ]

    entries = [
        *(
            [entry]
            if not pd.isnull(row.get("Entry"))
            and not any(x["type"] == "abilityDc" for x in sub_entries)
            else []
        ),
        *(
            (
                [
                    {
                        "type": "entries",
                        "name": "Spellcasting Ability",
                        "entries": [entry] + sub_entries,
                    }
                ]
                if any(x["type"] == "abilityDc" for x in sub_entries)
                else [sub_entries]
            )
            if len(sub_entries) > 0
            else []
        ),
    ]

    return {
        **({"type": type} if not pd.isnull(row.get("Type")) else {"type": "entries"}),
        **({"name": name} if not pd.isnull(row.get("Parent")) else {}),
        **({"entries": entries} if len(entries) > 0 else {}),
        **(
            {"attributes": attribute.split(", ")}
            if not pd.isnull(row.get("Attributes"))
            else {}
        ),
    }


def row_to_subclass_features(row):
    feature = row_to_features(row)
    feature["classSource"] = json_source
    feature["subclassSource"] = json_source
    feature["subclassShortName"] = row.get("Subclass")
    return feature


def row_to_features(row):
    name = row.get("Name")
    classes = inflection.humanize(row.get("Class"))
    level = int(row.get("Level"))
    type = row.get("Type")
    entry = row.get("Entry")
    sub_entries = [
        row_to_feature_entries(entry_row)
        for index, entry_row in df_class_features.iterrows()
        if pd.notnull(entry_row.get("Class"))
        and pd.notnull(entry_row.get("Parent"))
        and str(entry_row.get("Parent")).strip() == name
        and str(entry_row.get("Class")).strip() == classes
    ]
    entries = [
        *([entry] if not pd.isnull(row.get("Entry")) else ["Apparition unearthly spectral creepy uncanny wraith preternatural with"]),
        *(
            (
                [
                    {
                        "type": "entries",
                        "name": "Spellcasting Ability",
                        "entries": [entry] + sub_entries,
                    }
                ]
                if len(sub_entries) > 0
                else [sub_entries]
            )
            if len(sub_entries) > 0
            else []
        ),
    ]
    return {
        **({"className": classes} if not pd.isnull(row.get("Class")) else {}),
        **({"name": name} if not pd.isnull(row.get("Name")) else {}),
        **({"level": level} if not pd.isnull(row.get("Level")) else {}),
        "source": json_source,
        "classSource": json_source,
        **({"entries": entries} if len(entries) > 0 else {}),
    }


df_class_features = pd.read_csv(class_features_url, header=1)
df_class_features.head()

features_list = list({f"{item.get("className")}\0{item.get("name")}\1{item.get("level")}": item for item in [
    row_to_features(row)
    for index, row in df_class_features.iterrows()
    if pd.notnull(row.get("Name"))
       and pd.isnull(row.get("Parent"))
       and row.get("Source") == source
       and pd.isnull(row.get("Subclass"))
]}.values())

sub_class_features_list = [
    row_to_subclass_features(row)
    for index, row in df_class_features.iterrows()
    if pd.notnull(row.get("Name"))
    and pd.isnull(row.get("Parent"))
    and row.get("Source") == source
    and pd.notnull(row.get("Subclass"))
]
