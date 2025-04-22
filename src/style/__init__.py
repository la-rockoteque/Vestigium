"""
Package providing CSS styles as module-level variables for VestigiumFoundrySpells.
"""

from pathlib import Path

__all__ = [
    "_meta",
    "base",
    "cheatsheet",
    "coffee_stain",
    "corrected",
    "covers",
    "doodle",
    "footnote",
    "header",
    "others",
    "paperclip",
    "polaroid",
    "post_it",
    "smudge",
    "spell_list",
    "table",
    "watermark",
]

_css_dir = Path(__file__).parent

for name in __all__:
    path = _css_dir / f"{name}.css"
    if not path.is_file():
        raise ImportError(f"CSS file '{name}.css' not found in the 'style' package")
    globals()[name] = path.read_text()

# Clean up namespace
del Path, _css_dir, name, path
