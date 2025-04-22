import pandas as pd

species_url = "https://docs.google.com/spreadsheets/d/1I4FHncl40_xx1Udc_Q2rWWWvpL6xaMlpJyY90WBftag/export?format=csv&gid=993815941"
df_species = pd.read_csv(species_url)
df_species.head()

def row_to_species(row):
  return f"""# {row.get("Name")} - {row.get("Slogan")}
>*\"{row.get("Quote")}\"

{row.get("Intro")}

## Origins & History
{row.get("Origin")}

## Appearance
{row.get("Appearance")}

## Culture & Identity
{row.get("Culture & Identity")}

## Naming Conventions
{row.get("Naming Conventions")}

## {row.get("Name")} Traits
You {row.get("Name")} character has the following traits.

### Ability Score Increases
- Your **{row.get("Ability 1")}** score increases by **{row.get("Score 1")}**.
- Your **{row.get("Ability 2")}** score increases by **{row.get("Score 2")}**.

### Age
{row.get("Age")}

### Size
{row.get("Size")}

### Speed
{row.get("Speed")}

### Senses
{row.get("Vision")}

### Racial Traits
- **{row.get("Trait 1").split("|")[0]}**. {row.get("Trait 1").split("|")[1]}
- **{row.get("Trait 2").split("|")[0]}**. {row.get("Trait 2").split("|")[1]}
- **{row.get("Trait 3").split("|")[0]}**. {row.get("Trait 3").split("|")[1]}
- **{row.get("Trait 4").split("|")[0]}**. {row.get("Trait 4").split("|")[1]}
- **{row.get("Trait 5").split("|")[0]}**. {row.get("Trait 5").split("|")[1]}

### {row.get("Name")} in Concord City
{row.get("Life in the City")}

### Playstyle & Roleplaying
{row.get("Playstyle & Roleplaying Hooks")}
"""

species= [
  row_to_species(row)
  for index, row in df_species.iterrows()
  if pd.notnull(row.get("Name"))
]