import re


def read_spells(file_path):
    with open(file_path, "r", encoding="utf-8") as file:
        lines = file.readlines()

    spells = []
    current_spell = []
    current_name = None

    for line in lines:
        # Identify spell headers (#### **Spell Name**)
        match = re.match(r"^####\s+\*\*(.*?)\*\*", line.strip())
        if match:
            # Save previous spell before starting a new one
            if current_spell and current_name:
                spells.append((current_name, current_spell))

            current_name = match.group(1).strip()
            current_spell = [line]  # Start a new spell entry
        else:
            current_spell.append(line)  # Add to the current spell description

    # Add the last spell if it exists and has a valid name
    if current_spell and current_name:
        spells.append((current_name, current_spell))

    # Function to extract spell level reliably
    def extract_level(spell_lines):
        full_text = "".join(spell_lines)
        match = re.search(
            r"\b(Cantrip|\d+)[stndrdth]*[-\s]?level\b", full_text, re.IGNORECASE
        )
        return (
            -1
            if match and "cantrip" in match.group(1).lower()
            else int(match.group(1))
            if match
            else 100
        )

    # Sort spells by level first, then alphabetically (handle None safely)
    spells.sort(
        key=lambda spell: (
            extract_level(spell[1]),
            spell[0].lower() if spell[0] else "zzz",
        )
    )

    return spells


def write_sorted_spells(sorted_spells, output_path):
    with open(output_path, "w", encoding="utf-8") as file:
        for _, spell_lines in sorted_spells:
            file.writelines(spell_lines)
            file.write("\n")  # Ensure spacing between spells


# Define file paths
input_path = "Vestigium_Spells_Corrected.md"  # Ensure correct file reference
output_path = "Vestigium_Spells_Sorted.md"

# Execute sorting with the new approach
sorted_spells = read_spells(input_path)
write_sorted_spells(sorted_spells, output_path)

print(f"✅ Sorting complete. The new sorted file is saved as: {output_path}")
