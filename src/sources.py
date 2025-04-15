import pandas as pd
pd.options.display.float_format = '{:,.0f}'.format
sources_url = "https://docs.google.com/spreadsheets/d/1I4FHncl40_xx1Udc_Q2rWWWvpL6xaMlpJyY90WBftag/export?format=csv&gid=340852453"

df_source = pd.read_csv(sources_url)
df_source.head()

source = "VSTGCC"
source_row = df_source[df_source["Source"] == source].iloc[0]

full_source = source_row["Full"]
json_source = source_row["json"]