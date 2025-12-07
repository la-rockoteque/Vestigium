"""
script_generator.py
Generates script characters for phonemes using LLM and writes them back
to the Google Sheets Scripts tab.
"""

import pandas as pd
import random
from gsheets_client import gsheets


def random_char_from_range(unicode_range):
  """
  Parse a unicode range and return a random character.
  Supports single ranges (U+1D5D4–U+1D5EE) or comma-separated multiple ranges.
  """
  if not unicode_range or not isinstance(unicode_range, str):
    return "?"

  # Clean up the range string
  unicode_range = unicode_range.strip()

  # Handle multiple ranges separated by commas or newlines
  ranges = []
  for part in unicode_range.replace('\n', ',').split(','):
    part = part.strip()
    if not part or 'deduplication' in part.lower():
      continue

    # Parse individual range like "U+0020–U+002F" or "U+00B7" (single code point)
    if '–' in part or '—' in part or '-' in part:
      # Range format
      range_parts = part.replace("U+", "").replace("–", "-").replace("—", "-").split("-")
      if len(range_parts) == 2:
        try:
          start = int(range_parts[0].strip(), 16)
          end = int(range_parts[1].strip(), 16)
          ranges.append((start, end))
        except (ValueError, OverflowError):
          pass
    elif 'U+' in part:
      # Single code point
      try:
        code = int(part.replace("U+", "").strip(), 16)
        ranges.append((code, code))
      except (ValueError, OverflowError):
        pass

  if not ranges:
    return "?"

  # Pick a random range and then a random character from it
  start, end = random.choice(ranges)
  code_point = random.randint(start, end)
  return chr(code_point)


def parse_unicode_from_response(response_text):
  """
  Parse unicode code points from LLM response.
  Handles formats like: 'U+1D438', '1D438', '0x1D438', etc.

  Returns the character or None if parsing fails.
  """
  import re

  text = response_text.strip()

  # Try to find U+XXXX pattern
  match = re.search(r'U\+([0-9A-Fa-f]{4,6})', text)
  if match:
    try:
      code_point = int(match.group(1), 16)
      return chr(code_point)
    except (ValueError, OverflowError):
      pass

  # Try to find 0xXXXX pattern
  match = re.search(r'0x([0-9A-Fa-f]{4,6})', text)
  if match:
    try:
      code_point = int(match.group(1), 16)
      return chr(code_point)
    except (ValueError, OverflowError):
      pass

  # Try to parse as plain hex
  if len(text) >= 4 and len(text) <= 6 and all(c in '0123456789ABCDEFabcdef' for c in text):
    try:
      code_point = int(text, 16)
      return chr(code_point)
    except (ValueError, OverflowError):
      pass

  return None


def llm_script_char(phoneme, phoneme_info, script_name, unicode_range):
  """
  Generate a script character for a phoneme using LLM.

  Args:
    phoneme: The IPA symbol (e.g., 'p', 'b', 'm')
    phoneme_info: Dict with Category, Place_or_Height, Manner_or_Backness, Voicing, Notes
    script_name: Name of the script (e.g., 'Ashen', 'Choraline')
    unicode_range: Unicode range to use (e.g., 'U+1D5D4–U+1D5EE' or with 'deduplication' keyword)

  Returns:
    A single character or multi-character symbol from the unicode range
  """
  try:
    from llm_wordgen.local_llm_ollama import OllamaLexemeGenerator
    from llm_wordgen.prompts import script_symbol_prompt

    LLM = OllamaLexemeGenerator()

    # Check if deduplication is enabled
    allow_deduplication = 'deduplication' in unicode_range.lower()

    # Clean the range for display (remove deduplication keyword)
    display_range = unicode_range.replace('deduplication', '').replace('Deduplication', '').strip()

    # Build the prompt
    prompt = script_symbol_prompt(
      language=script_name,
      unicode_range=display_range,
      symbol=phoneme,
      category=phoneme_info.get('Category', ''),
      place_or_height=phoneme_info.get('Place_or_Height', ''),
      manner_or_backness=phoneme_info.get('Manner_or_Backness', ''),
      voicing=phoneme_info.get('Voicing', ''),
      allow_deduplication=allow_deduplication
    )

    print(f"LLM script char: {phoneme} in {script_name} (deduplication: {allow_deduplication})")

    # Use the LLM's generate method but pass the raw prompt
    import ollama
    result = ollama.generate(model="llama3", prompt=prompt)

    # Extract the response
    response = result['response'].strip()

    print(f"[DEBUG] Raw LLM response: {response!r}")

    # Try to parse as unicode code point first
    char = parse_unicode_from_response(response)

    if char:
      print(f"[INFO] Parsed unicode code point to character: {char!r}")
      return char

    # If it's already a character, accept longer responses when deduplication is enabled
    max_length = 10 if allow_deduplication else 5
    if len(response) >= 1 and len(response) <= max_length:
      print(f"[INFO] Using response as-is: {response!r}")
      return response

    # Otherwise, fall back to random
    print(f"[WARN] LLM returned unparseable response: {response!r}, using random")
    return random_char_from_range(display_range)

  except Exception as e:
    print(f"LLM failed to generate script char for {phoneme} in {script_name}")
    print(f"Exception: {e}")
    # Clean range for fallback
    display_range = unicode_range.replace('deduplication', '').replace('Deduplication', '').strip()
    return random_char_from_range(display_range)


def load_scripts():
  """Load the Scripts sheet as a DataFrame."""
  df = gsheets.get_df("scripts")
  return df


def find_or_generate_script_char(phoneme, phoneme_info, script_name, unicode_range):
  """
  Returns the script character for a phoneme in a specific script.
  If the character is missing, it is generated and written to the sheet.

  Args:
    phoneme: The IPA symbol
    phoneme_info: Dict with phoneme properties
    script_name: Name of the script column
    unicode_range: Unicode range for this script

  Returns:
    The script character
  """
  df = load_scripts()

  # Columns that actually exist in the sheet
  sheet_columns = [c for c in df.columns]

  # Make sure the script column exists
  if script_name not in sheet_columns:
    # Add a new header for this script
    header_col = len(sheet_columns) + 1
    gsheets.update_cell("scripts", 1, header_col, script_name)
    # Add unicode range in row 2
    gsheets.update_cell("scripts", 2, header_col, unicode_range)
    df[script_name] = ""
    sheet_columns.append(script_name)

  # Find the row for this phoneme (match on Symbol column)
  row = df[df["Symbol"] == phoneme]

  if not row.empty:
    value = row.iloc[0].get(script_name, "")
    row_index = row.index[0] + 2  # +2 for header row and 0-based index

    # Treat empty/NaN as missing
    if isinstance(value, str):
      if value.strip() == "":
        value = None

    if pd.isna(value) or value is None:
      # Generate new character
      new_char = llm_script_char(phoneme, phoneme_info, script_name, unicode_range)
      col_index = sheet_columns.index(script_name) + 1
      gsheets.update_cell("scripts", row_index, col_index, new_char)
      return new_char

    return value

  # Phoneme is NOT in scripts sheet - this shouldn't happen
  print(f"[ERROR] Phoneme {phoneme} not found in Scripts sheet")
  return "?"


if __name__ == "__main__":
  print("Testing script character generator")

  # Test with a sample phoneme
  phoneme_info = {
    'Category': 'Consonant',
    'Place_or_Height': 'Bilabial',
    'Manner_or_Backness': 'Plosive',
    'Voicing': 'Voiceless'
  }

  result = find_or_generate_script_char('p', phoneme_info, 'Ashen', 'U+1D5D4–U+1D5EE')
  print(f"Generated character: {result}")
