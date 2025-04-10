import re
import pandas as pd

def extract_spells(file_path, output_file):
    # Read the file content
    with open(file_path, "r", encoding="utf-8") as file:
        spells_text = file.read()

    # Splitting spells based on title patterns (e.g., ### **Spell Name**)
    spell_entries = re.split(r"\n### \*\*(.*?)\*\*", spells_text)[1:]

    # Prepare a list to store structured spell data
    spells_list = []

    for i in range(0, len(spell_entries), 2):
        spell_name = spell_entries[i].strip()
        spell_details = spell_entries[i + 1]

        # Extract key attributes using regex
        level_match = re.search(r"\*(\d+(st|nd|rd|th)?-level) (.*?)\*", spell_details)
        cantrip_match = re.search(r"\*(Cantrip) (.*?)\*", spell_details)
        ritual_match = re.search(r"\(Ritual\)", spell_details)
        casting_time_match = re.search(r"\*\*Casting Time:\*\*.*?::(.*)", spell_details)
        range_match = re.search(r"\*\*Range:\*\*.*?::(.*)", spell_details)
        components_match = re.search(r"\*\*Components:\*\*.*?::(.*)", spell_details)
        duration_match = re.search(r"\*\*Duration:\*\*.*?::(.*)", spell_details)
        class_match = re.search(r"\*\*Class:\*\* (.*)", spell_details)
        cost_match = re.search(r"\*\*Cost:\*\* (.*?)\n", spell_details)
        permit_match = re.search(r"\*\*Permit:\*\* (.*?)\n", spell_details)
        blood_pact_match = re.search(r"\*\*Blood Pact:\*\* (.*?)\n", spell_details)
        beauty_cost_match = re.search(r"\*\*Beauty Cost:\*\* (.*?)\n", spell_details)
        concentration_match = re.search(r"\(Concentration\)", spell_details)
        acquisition_note_match = re.search(r"\*\*Acquisition Note:\*\* (.*?)\n", spell_details, re.DOTALL)
        arcane_strain_match = re.search(r"\*\*Arcane Strain:\*\* (.*?)\n", spell_details, re.DOTALL)
        tag_match = re.search(r"\*\*Tag:\*\* (.*?)\n", spell_details)

        # Extract full description first
        description_match = re.search(
            r"\*\*Duration:\*\*.*?\n([\s\S]*?)(?=\n(?:\*\*Scaling \(Upcast Effect\):\*\*|\*\*Arcane Strain:\*\*|\*\*Acquisition Note:\*\*|\*\*Permit & Cost:\*\*|\*\*Class:\*\*))",
            spell_details
        )

        full_description = description_match.group(1).strip() if description_match else ""

        # Extract Scaling separately
        scaling_match = re.search(r"(?:\*\*Scaling \(Upcast Effect\):\*\*\n([\s\S]*?))?(?:\nAt Higher Levels\..*?)?(?=\n(?:\*\*Class:\*\*|\*\*Arcane Strain:\*\*|\*\*Acquisition Note:\*\*|\*\*Permit & Cost:\*\*))", spell_details)
        scaling = scaling_match.group(1).strip() if scaling_match and scaling_match.group(1) else ""

        # Clean extracted values
        level = level_match.group(1).strip() if level_match else (cantrip_match.group(1).strip() if cantrip_match else "")
        school = level_match.group(3).strip() if level_match else (cantrip_match.group(2).strip() if cantrip_match else "")
        is_ritual = "Yes" if ritual_match else "No"
        casting_time = casting_time_match.group(1).strip() if casting_time_match else ""
        spell_range = range_match.group(1).strip() if range_match else ""
        duration = duration_match.group(1).strip() if duration_match else ""
        spell_class = class_match.group(1).strip() if class_match else ""
        cost = cost_match.group(1).strip() if cost_match else ""
        permit = permit_match.group(1).strip() if permit_match else ""
        blood_pact = blood_pact_match.group(1).strip() if blood_pact_match else ""
        beauty_cost = beauty_cost_match.group(1).strip() if beauty_cost_match else ""
        is_concentration = "Yes" if concentration_match else "No"
        acquisition_note = acquisition_note_match.group(1).strip() if acquisition_note_match else ""
        arcane_strain = arcane_strain_match.group(1).strip() if arcane_strain_match else ""
        tag = tag_match.group(1).strip() if tag_match else ""

        # Extract components and component description
        components_text = components_match.group(1).strip() if components_match else ""
        component_parts = components_text.split("(", 1)
        components = component_parts[0].strip()
        component_description = f"({component_parts[1].strip()}" if len(component_parts) > 1 else ""

        # Store spell entry
        spells_list.append([
            spell_name, level, school, is_ritual, casting_time, is_concentration, spell_range, components, component_description, duration,
            cost, permit, blood_pact, beauty_cost, full_description, scaling, acquisition_note, arcane_strain, spell_class, tag
        ])

    # Convert to DataFrame
    spells_df = pd.DataFrame(spells_list, columns=[
        "Spell Name", "Level", "School", "Ritual", "Casting Time", "Concentration", "Range", "Component", "Component Description", "Duration",
        "Cost", "Permit", "Blood Pact", "Beauty Cost", "Description", "Scaling", "Acquisition Note", "Arcane Strain", "Class", "Tag"
    ])

    # Save as Excel file
    spells_df.to_excel(output_file, index=False)
    print(f"Spells extracted successfully to {output_file}")

# Example usage
extract_spells("Spells.md", "Vestigium_Spells.xlsx")