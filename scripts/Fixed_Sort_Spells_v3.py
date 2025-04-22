import re


def read_spells(file_path):
    with open(file_path, "r", encoding="utf-8") as file:
        content = file.read()

    # Preserve all content while ensuring proper separation
    spells = re.split(r"(####\s+\*\*.*?\*\*\n)", content)

    spell_entries = []
    for i in range(1, len(spells), 2):
        spell_name = spells[i].strip()
        spell_description = spells[i + 1] if i + 1 < len(spells) else ""

        # Preserve original formatting and ensure no lines are skipped
        spell_entries.append(f"{spell_name}\n{spell_description.strip()}")

    # Extract spell level with improved regex for variations
    def extract_level(spell):
        match = re.search(
            r"\b(Cantrip|\d+)[stndrdth]*[-\s]?level\b", spell, re.IGNORECASE
        )
        return (
            -1
            if "cantrip" in match.group(1).lower()
            else int(match.group(1))
            if match
            else 100
        )

    # Extract spell names correctly, ensuring no misclassification
    def extract_spell_name(spell):
        match = re.match(r"####\s+\*\*(.*?)\*\*", spell)
        return match.group(1).strip().lower() if match else "zzzz"

    # Sort spells by level first, then alphabetically
    spell_entries.sort(
        key=lambda spell: (extract_level(spell), extract_spell_name(spell))
    )

    # Preserve exact formatting by keeping all original line breaks
    sorted_spells_text = "\n\n".join(spell_entries)

    return sorted_spells_text


def write_sorted_spells(sorted_spells, output_path):
    with open(output_path, "w", encoding="utf-8") as file:
        file.write(sorted_spells)  # Ensure all lines are preserved


# Define file paths
input_path = "Vestigium_Spells_Cleaned.md"  # Ensure correct file reference
output_path = "Vestigium_Spells_Sorted_Fixed_v3.md"

# Execute sorting with enhanced line retention
sorted_spells = read_spells(input_path)
write_sorted_spells(sorted_spells, output_path)

print(f"✅ Sorting complete. The improved file is saved as: {output_path}")
