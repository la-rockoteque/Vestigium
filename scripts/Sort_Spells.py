import re

def read_spells(file_path):
    """Reads spells while keeping their entire content intact."""
    with open(file_path, 'r', encoding='utf-8') as file:
        lines = file.readlines()

    spells = []
    current_spell = []
    current_name = None
    current_level = None

    for line in lines:
        match = re.match(r'^####\s+\*\*(.*?)\*\*', line.strip())
        if match:
            # Store previous spell
            if current_spell and current_name:
                spells.append({
                    "name": current_name,
                    "level": current_level,
                    "content": current_spell[:],  # Preserve full formatting
                })

            # Start a new spell
            current_name = match.group(1).strip()
            current_spell = [line]
            current_level = None  # Reset level

        else:
            current_spell.append(line)
            # Extract level when found in description
            if not current_level:
                level_match = re.search(r'\b(Cantrip|\d+)[stndrdth]*[-\s]?level\b', line, re.IGNORECASE)
                if level_match:
                    current_level = -1 if "cantrip" in level_match.group(1).lower() else int(level_match.group(1))

    # Store the last spell
    if current_spell and current_name:
        spells.append({
            "name": current_name,
            "level": current_level if current_level is not None else 100,
            "content": current_spell[:],
        })

    return spells

def write_sorted_spells(spells, output_path):
    """Writes sorted spells while ensuring content remains unchanged."""
    with open(output_path, 'w', encoding='utf-8') as file:
        for spell in spells:
            file.writelines(spell["content"])
            file.write("\n")  # Keep spacing intact

# Define file paths
input_path = "Vestigium_Spells_Corrected.md"  # Ensure correct file reference
output_path = "Vestigium_Spells_Sorted.md"

# Read, sort, and write spells
spells = read_spells(input_path)
spells.sort(key=lambda spell: (spell["level"], spell["name"].lower()))
write_sorted_spells(spells, output_path)

print(f"✅ Sorting complete. The final sorted file is saved as: {output_path}")