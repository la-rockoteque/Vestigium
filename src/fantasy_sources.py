import pandas as pd
import inflection

pd.options.display.float_format = "{:,.0f}".format
sources_url = "https://docs.google.com/spreadsheets/d/1NBZGu29IfE1ZfAWO1Z6ShR5GMLMMbaSyS0m-46PSYm4/export?format=csv&gid=340852453"

df_source = pd.read_csv(sources_url)
df_source.head()

source = "ORIO"
source_row = df_source[df_source["Source"] == source].iloc[0]

full_source = source_row["Full"]
json_source = source_row["json"]

sources = [
    {
        "json": row["json"],
        "abbreviation": row["Source"],
        "full": row["Full"],
        "url": f"https://raw.githubusercontent.com/la-rockoteque/Vestigium/refs/heads/main/Velum_Cineris;{inflection.underscore(full_source)}.json",
        "authors": ["Velum Cineris"],
        "version": "1.0",
    }
    for index, row in df_source.iterrows()
    if pd.notnull(row.get("Full"))
]
