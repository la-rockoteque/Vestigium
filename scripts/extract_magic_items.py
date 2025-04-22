import pandas as pd
import re


def extract_magic_items(md_file, output_csv, output_excel):
    with open(md_file, "r", encoding="utf-8") as file:
        content = file.read()

    # Regular expression to capture magic items
    item_pattern = re.findall(
        r"### \*(.*?)\*\n\*(.*?)\*\n(.*?)(?=\n###|\Z)", content, re.DOTALL
    )

    # Extracted data
    data = []
    for name, type_rarity, description in item_pattern:
        type_rarity_parts = type_rarity.split(", ")
        if len(type_rarity_parts) == 2:
            full_type, rarity = type_rarity_parts
        else:
            full_type, rarity = type_rarity, "Unknown"

        # Split full type into magic item type and specific item type
        if "(" in full_type and ")" in full_type:
            magic_item_type, specific_item_type = re.match(
                r"(.*?) \((.*?)\)", full_type
            ).groups()
        else:
            magic_item_type, specific_item_type = full_type, "General"

        # Clean up the description text
        description = description.strip().replace("\n", " ")

        data.append(
            [
                name,
                magic_item_type.strip(),
                specific_item_type.strip(),
                rarity.strip(),
                description,
            ]
        )

    # Create a DataFrame
    df = pd.DataFrame(
        data,
        columns=[
            "Name",
            "Magic Item Type",
            "Specific Item Type",
            "Rarity",
            "Description",
        ],
    )

    # Save to CSV and Excel
    df.to_csv(output_csv, index=False)
    df.to_excel(output_excel, index=False)

    print(
        f"Extraction complete. Files saved as:\nCSV: {output_csv}\nExcel: {output_excel}"
    )


# Example usage
md_file = "Magic_Items.md"  # Change to your Markdown file path
output_csv = "Magic_Items.csv"
output_excel = "Magic_Items.xlsx"

extract_magic_items(md_file, output_csv, output_excel)
