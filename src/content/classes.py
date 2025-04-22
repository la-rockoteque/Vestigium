import pandas as pd
from src.sources import source, json_source
import inflection
from collections import defaultdict
from itertools import count
import string

spells_url = "https://docs.google.com/spreadsheets/d/1I4FHncl40_xx1Udc_Q2rWWWvpL6xaMlpJyY90WBftag/export?format=csv&gid=625265890"
df_spells = pd.read_csv(spells_url)
df_spells.head()

classes_url = "https://docs.google.com/spreadsheets/d/1I4FHncl40_xx1Udc_Q2rWWWvpL6xaMlpJyY90WBftag/export?format=csv&gid=1924660120"
class_tables_url = "https://docs.google.com/spreadsheets/d/1I4FHncl40_xx1Udc_Q2rWWWvpL6xaMlpJyY90WBftag/export?format=csv&gid=193036738"
class_features_url = "https://docs.google.com/spreadsheets/d/1I4FHncl40_xx1Udc_Q2rWWWvpL6xaMlpJyY90WBftag/export?format=csv&gid=545140625"

subclasses_url = "https://docs.google.com/spreadsheets/d/1I4FHncl40_xx1Udc_Q2rWWWvpL6xaMlpJyY90WBftag/export?format=csv&gid=338247460"

df_subclasses = pd.read_csv(subclasses_url)
df_subclasses.head()

df_classes = pd.read_csv(classes_url, header=1)
df_classes.head()

df_class_tables = pd.read_csv(class_tables_url, header=1)
df_class_tables.head()

df_class_features = pd.read_csv(class_features_url, header=1)
df_class_features.head()


def get_features_for_class(class_name, subclass_title):
    def get_feature_label(row):
        name = row.get("Name")
        level = int(row.get("Level"))

        return f"{name}|{class_name}|{json_source}|{level}|{json_source}"

    return [
        *[
            get_feature_label(entry_row)
            for index, entry_row in df_class_features.iterrows()
            if pd.notnull(entry_row.get("Class"))
            and pd.notnull(entry_row.get("Name"))
            and pd.isnull(entry_row.get("Parent"))
            and str(entry_row.get("Class")) == class_name
        ]
    ]


def to_table(class_name: str):
    header = df_class_tables.loc[df_class_tables["Class"] == class_name].iloc[0]

    def process(row):
        proficiency = (
            int(row.get("Proficiency Bonus"))
            if not pd.isnull(row.get("Proficiency Bonus"))
            else ""
        )
        knownSpells = (
            int(row.get("Spells Known"))
            if not pd.isnull(row.get("Spells Known"))
            else ""
        )
        maxSpellLevel = (
            int(row.get("Max Spell Level"))
            if not pd.isnull(row.get("Max Spell Level"))
            else ""
        )
        Points = int(row.get("Points")) if not pd.isnull(row.get("Points")) else ""
        spellSlots = (
            int(row.get("Total spell slots"))
            if not pd.isnull(row.get("Total spell slots"))
            else ""
        )
        feature1 = (
            int(row.get("Feature 1")) if not pd.isnull(row.get("Feature 1")) else ""
        )
        return [
            *([proficiency] if not pd.isnull(row.get("Proficiency Bonus")) else []),
            *([knownSpells] if not pd.isnull(row.get("Spells Known")) else []),
            *([maxSpellLevel] if not pd.isnull(row.get("Max Spell Level")) else []),
            *([Points] if not pd.isnull(row.get("Points")) else []),
            *([spellSlots] if not pd.isnull(row.get("Total spell slots")) else []),
            *([feature1] if not pd.isnull(row.get("Feature 1")) else []),
        ]

    labels = [
        *(
            [f"{{@filter Proficiency Bonus|value|class={class_name}}}"]
            if not pd.isnull(header.get("Proficiency Bonus"))
            else []
        ),
        *(
            [f"{{@filter Spells Known|value|class={class_name}}}"]
            if not pd.isnull(header.get("Spells Known"))
            else []
        ),
        *(
            [f"{{@filter Max Spell Level|value|class={class_name}}}"]
            if not pd.isnull(header.get("Max Spell Level"))
            else []
        ),
        *(
            [f"{{@filter Points|value|class={class_name}}}"]
            if not pd.isnull(header.get("Points"))
            else []
        ),
        *(
            [f"{{@filter Total spell slots|value|class={class_name}}}"]
            if not pd.isnull(header.get("Total spell slots"))
            else []
        ),
        *(
            [f"{{@filter {header.get('Feature 1 Name')}|value|class={class_name}}}"]
            if not pd.isnull(header.get("Feature 1 Name"))
            else []
        ),
    ]
    tablish = [
        process(row)
        for index, row in df_class_tables.iterrows()
        if pd.notnull(row.get("Class")) and str(row.get("Class")).strip() == class_name
    ]

    return {"colLabels": labels, "rows": tablish}


def to_spell_progression_table(class_name: str):
    labels = [
        f"{{@filter {level}|spells|level={level[0]}|class={class_name}}}"
        for level in ["1st", "2nd", "3rd", "4th", "5th", "6th", "7th", "8th", "9th"]
    ]

    tablish = [
        [
            row.get("1"),
            row.get("2"),
            row.get("3"),
            row.get("4"),
            row.get("5"),
            row.get("6"),
            row.get("7"),
            row.get("8"),
            row.get("9"),
        ]
        for index, row in df_class_tables.iterrows()
        if pd.notnull(row.get("Class")) and str(row.get("Class")).strip() == class_name
    ]

    return {
        "title": "Spell Slots per Spell Level",
        "colLabels": labels,
        "rows": tablish,
    }


def row_to_class(row):
    class_name = (
        row.get("Name") if not pd.isnull(row.get("Name", "Generic Class")) else ""
    )
    subclass_title = (
        row.get("Subclass Title") if not pd.isnull(row.get("Subclass Title")) else ""
    )
    skills = row.get("Skills") if not pd.isnull(row.get("Skills")) else ""
    armors = row.get("Armor") if not pd.isnull(row.get("Armor")) else ""
    weapons = row.get("Weapons") if not pd.isnull(row.get("Weapons")) else ""
    tools = row.get("Tools") if not pd.isnull(row.get("Tools")) else ""
    proficiency = (
        row.get("Saving Throws") if not pd.isnull(row.get("Saving Throws")) else ""
    )
    class_spells = [
        row.get("Spell Name")
        for index, row in df_spells.iterrows()
        if pd.notnull(row.get("Class")) == class_name
    ]
    cantrip_progression = [
        int(row.get("0"))
        for index, row in df_class_tables.iterrows()
        if pd.notnull(row.get("Class")) == class_name
    ]
    equipmentA = {
        string.ascii_lowercase[i]: [f"{item.strip()}|{source}"]
        for i, item in enumerate(row.get("A", "").split(", "))
    }

    equipmentB = {
        string.ascii_lowercase[i]: [f"{item.strip()}|{source}"]
        for i, item in enumerate(row.get("B", "").split(", "))
    }

    default_equipment = [
        ", ".join(
            [f"{{@item {item}|{source}}}" for item in row.get("A", "").split(", ")]
        ),
        ", ".join(
            [f"{{@item {item}|{source}}}" for item in row.get("B", "").split(", ")]
        ),
        ", ".join(
            [f"{{@item {item}|{source}}}" for item in row.get("Common", "").split(", ")]
        ),
    ]

    common = {
        "_": [f"{item.strip()}|{source}" for item in row.get("Common", "").split(", ")]
    }

    def get_subclasses(subclass):
        return {"name": subclass.get("Name"), "source": json_source}

    subclasses = [
        get_subclasses(subclass)
        for idx, subclass in df_subclasses.iterrows()
        if subclass.get("Class") == class_name
    ]

    classes = {
        "source": json_source,
        "name": class_name,
        **({"hd": {"faces": row.get("Hit Points ar 1st Level", ""), "number": 1}}),
        "proficiency": [prof[:3].lower() for prof in proficiency.split(", ")],
        "startingProficiencies": {
            "armor": [armor.lower() for armor in armors.split(", ")],
            "weapons": [
                *[
                    f"{{@item {weapon.lower()}|VSTGCC|{weapon.lower()}}}"
                    for weapon in weapons.split(", ")
                    if weapon not in ["simple", "martial"]
                ],
                "simple",
            ],
            "skills": [
                {
                    "choose": {
                        "from": [skill.lower() for skill in skills.split(", ")],
                        "count": 3,
                    }
                }
            ],
        },
        "startingEquipment": {
            "additionalFromBackground": True,
            "default": default_equipment,
            "defaultData": [equipmentA, equipmentB, common],
        },
        **(
            {"spellcastingAbility": row.get("Spellcasting Ability")[:3].lower()}
            if not pd.isnull(row.get("Spellcasting Ability"))
            else {}
        ),
        **(
            {"casterProgression": row.get("Caster Progression")}
            if not pd.isnull(row.get("Caster Progression"))
            else {}
        ),
        **(
            {
                "preparedSpells": f"<$level$> + <${row.get('Spellcasting Ability')[:3].lower()}_mod$>"
            }
            if pd.isnull(row.get("Prepares Spells")) == "TRUE"
            else {}
        ),
        **(
            {"cantripProgression": cantrip_progression}
            if not pd.isnull(row.get("spellcastingAbility"))
            else {}
        ),
        "classTableGroups": [
            to_table(class_name),
            *(
                [to_spell_progression_table(class_name)]
                if not pd.isnull(row.get("spellcastingAbility"))
                else []
            ),
        ],
        **(
            {"subclassTitle": row.get("Subclass Title")}
            if not pd.isnull(row.get("Subclass Title"))
            else {}
        ),
        "classFeatures": get_features_for_class(class_name, subclass_title),
        "subclasses": subclasses,
        **(
            {"classSpells": class_spells}
            if not pd.isnull(row.get("spellcastingAbility"))
            else {}
        ),
    }
    return classes


classes_list = [
    row_to_class(row)
    for index, row in df_classes.iterrows()
    if pd.notnull(row.get("Name"))
    and str(row.get("Name")).strip() != ""
    and row.get("Source") == source
]
