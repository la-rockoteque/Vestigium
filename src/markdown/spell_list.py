import pandas as pd

spells_url = "https://docs.google.com/spreadsheets/d/1I4FHncl40_xx1Udc_Q2rWWWvpL6xaMlpJyY90WBftag/export?format=csv&gid=625265890"
df_spells = pd.read_csv(spells_url)
df_spells.head()

df_sorted = df_spells.sort_values(['Level', 'Spell Name'])
grouped = df_sorted.groupby('Level')

def row_to_markdown(level, group):
    list = "\n".join([f"- {row['Spell Name']}" for _, row in group.iterrows()])
    return f"##### {level}\n\n{list}"

markdown = [row_to_markdown(level, group) for level, group in grouped]

spell_list = "\n\n".join(markdown)
