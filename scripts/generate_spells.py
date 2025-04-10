import pandas as pd

def generate_spell_markdown(csv_file_path):
    df = pd.read_csv(csv_file_path)
    print("Available columns in CSV:", df.columns)
    markdown_output = ""

    for _, row in df.iterrows():
        spell_name = row["Spell Name"].strip()
        level = row["Level"].strip()
        school = row["School"].strip()
        casting_time = row["Casting Time"].strip()
        spell_range = row["Range"].strip()
        components = row["Component"] if pd.notna(row["Component"]) else "V, S, M"
        duration = row["Duration"].strip()
        description = row["Description"].strip()

        markdown_output += f"""
#### {spell_name}
*{level} {school}*

**Casting Time:** :: {casting_time}
**Range:**        :: {spell_range}
**Components:**   :: {components}
**Duration:**     :: {duration}

{description}

---
"""
    return markdown_output

# Example usage
csv_file_path = "/Users/rocko/Downloads/Mispelled_Spells.csv"
spell_markdown = generate_spell_markdown(csv_file_path)

# Save the output to a markdown file
output_file_path = "/Users/rocko/Downloads/Mispelled_Spells.md"
with open(output_file_path, "w", encoding="utf-8") as file:
    file.write(spell_markdown)

output_file_path
