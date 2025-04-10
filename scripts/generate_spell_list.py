import re
from collections import defaultdict

# Define file paths
file_path = "/Users/rocko/Downloads/Vestigium_Spells.md"
output_path = "/Users/rocko/Downloads/Vestigium_Spells_List.md"

# Regular expressions to match spell names and levels
spell_pattern = re.compile(r"^\s*#{3,4}\s*\*\*(.+?)\*\*", re.MULTILINE)
level_pattern = re.compile(r"\*(\d+)(?:st|nd|rd|th)?-level", re.IGNORECASE)  # Detect spell levels
cantrip_pattern = re.compile(r"\*Cantrip\b", re.IGNORECASE)  # Detect cantrips explicitly

# Dictionary to hold spells sorted by level
spells_by_level = defaultdict(list)

# Read the file content
with open(file_path, "r", encoding="utf-8") as file:
    content = file.read()

# Find all spell names
spell_names = spell_pattern.findall(content)

if not spell_names:
    print("ERROR: No spell names detected! Check markdown format.")

# Find levels for each spell
for spell_name in spell_names:
    spell_header_match = re.search(rf"### \*\*{re.escape(spell_name)}\*\*", content)

    if spell_header_match:
        spell_start = spell_header_match.start()
        spell_end = content.find("### ", spell_start + 1)  # Find next spell to limit search range
        spell_block = content[spell_start:spell_end] if spell_end != -1 else content[spell_start:]

        # Search for level explicitly within spell block
        match = level_pattern.search(spell_block)
        if match:
            spell_level = f"{match.group(1)}th Level"
        elif cantrip_pattern.search(spell_block):
            spell_level = "Cantrips (0 Level)"  # Properly categorize cantrips
        else:
            spell_level = "Unknown Level"

    else:
        spell_level = "Unknown Level"

    # Store the spell under the appropriate level
    spells_by_level[spell_level].append(spell_name)
    print(f"Detected: {spell_name} -> {spell_level}")  # DEBUG PRINT

# Convert levels to numeric format for sorting
def level_sort_key(level):
    if "Cantrip" in level:
        return -1  # Ensure cantrips appear first
    numeric_part = re.sub(r"(st|nd|rd|th)", "", level.split()[0])  # Remove ordinal suffix
    return int(numeric_part) if numeric_part.isdigit() else 100  # Default high value for "Unknown Level"

# Sort levels numerically, keeping "Cantrips (0 Level)" at the top
sorted_levels = sorted(spells_by_level.keys(), key=level_sort_key)

# Generate formatted output
output = ["{{spellList,wide"]  # Start the structured output
for level in sorted_levels:
    output.append(f"##### {level}")
    for spell in sorted(spells_by_level[level]):  # Sort spells alphabetically
        output.append(f"- {spell}")
    output.append("")  # Add space between levels

output.append("}}")  # Close the structured output

# Write to a new markdown file
with open(output_path, "w", encoding="utf-8") as file:
    file.write("\n".join(output))

print(f"Formatted spell list saved to: {output_path}")