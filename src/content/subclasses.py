import pandas as pd
from src.sources import source, json_source
import inflection
from collections import defaultdict
from itertools import count
import string

subclasses_url = "https://docs.google.com/spreadsheets/d/1I4FHncl40_xx1Udc_Q2rWWWvpL6xaMlpJyY90WBftag/export?format=csv&gid=338247460"
class_features_url = "https://docs.google.com/spreadsheets/d/1I4FHncl40_xx1Udc_Q2rWWWvpL6xaMlpJyY90WBftag/export?format=csv&gid=545140625"

df_subclasses = pd.read_csv(subclasses_url)
df_subclasses.head()

df_class_features = pd.read_csv(class_features_url, header=1)
df_class_features.head()


def get_features_for_subclass(class_name, subclass_name):
    def get_feature_label(row):
        name = row.get("Name")
        level = int(row.get("Level"))

        return f"{name}|{class_name}|{json_source}|{subclass_name}|{json_source}|{level}|{json_source}"

    return [
        *[
            get_feature_label(entry_row)
            for index, entry_row in df_class_features.iterrows()
            if pd.notnull(entry_row.get("Class"))
            and pd.notnull(entry_row.get("Name"))
            and str(entry_row.get("Subclass")) == subclass_name
        ]
    ]


def row_to_subclass(row):
    subclass_name = row.get("Name")
    class_name = row.get("Class")
    features = get_features_for_subclass(class_name, subclass_name)
    subclass = {
        "name": subclass_name,
        "source": json_source,
        "className": class_name,
        "classSource": json_source,
        "shortName": subclass_name,
        "subclassFeatures": features,
    }
    return subclass


subclasses_list = [
    row_to_subclass(row)
    for index, row in df_subclasses.iterrows()
    if pd.notnull(row.get("Name"))
    and str(row.get("Name")).strip() != ""
    and row.get("Source") == source
]
