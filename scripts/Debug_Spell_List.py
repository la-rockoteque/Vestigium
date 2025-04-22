import re

# Define file paths
input_file = "Vestigium_Spells.md"  # Change this if needed
output_file = "Vestigium_Spells_Corrected.md"

# Load the file content
with open(input_file, "r", encoding="utf-8") as file:
    text = file.read()

# Define regex to detect both variations of cantrip formatting
cantrip_pattern = re.compile(r"\*(?:Cantrip\s+(\w+)|(\w+)\s+Cantrip)\*", re.IGNORECASE)


# Standardize to "*Cantrip, Illusion*" format
def standardize_cantrip(match):
    if match.group(1):  # Matches "*Cantrip Illusion*"
        return f"*Cantrip {match.group(1).capitalize()}*"
    if match.group(2):  # Matches "*Illusion Cantrip*"
        return f"*Cantrip {match.group(2).capitalize()}*"
    return match.group(0)  # Default fallback


# Apply correction to the text
corrected_text = re.sub(cantrip_pattern, standardize_cantrip, text)

# Save the corrected file
with open(output_file, "w", encoding="utf-8") as file:
    file.write(corrected_text)

print(f"✅ Cantrip formatting corrected! The new file is saved as '{output_file}'.")
