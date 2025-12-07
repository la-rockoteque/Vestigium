"""
generator.py
Generates new proto-roots for missing words and writes them back
into the Google Sheet dictionary.

Requires:
- key.json (your Google service account)
- The dictionary sheet must have a column named: Word
"""

import pandas as pd

import random
from gsheets_client import gsheets
from llm_wordgen.grammar_context import build_grammar_info, build_language_metadata

def random_lexeme(word, language):
  """
  Generate a fresh lexeme for this language.
  Option A: each language gets its own lexical word.
  Simple algorithm for now, can be replaced later per language profile.
  """
  consonants = "ptkmnsrlgv"
  vowels = "aeiou"

  syllables = []
  for _ in range(random.randint(1, 2)):
    c = random.choice(consonants)
    v = random.choice(vowels)
    syllables.append(c + v)
  # Make 2–4 letter roots + language signature letter
  base = "".join(syllables)
  return base + language[0].lower()

def llm_lexeme(word, language):
  try:
    from llm_wordgen.local_llm_ollama import OllamaLexemeGenerator
    LLM = OllamaLexemeGenerator()

    df = load_dictionary()
    examples = df[language].dropna().tolist()[:20]
    grammar_info = build_grammar_info(language)
    language_metadata = build_language_metadata(language)
    return LLM.generate(word, language, grammar_info, examples, language_metadata)
  except Exception as e:
    print(f"LLM failed to generate a lexeme for {word} in {language}")
    print(f"Exception: {e}")
    return random_lexeme(word, language)


# ------------------------------------------
# CORE LOGIC
# ------------------------------------------

def load_dictionary():
  df = gsheets.get_df("dictionary")
  df["key"] = df["Word"].str.lower().str.replace(" ", "_")
  return df

def find_or_generate(word, language):
  """
  Returns the lexeme for a word in a specific language.
  If the lexeme is missing, it is generated and written to the sheet.
  """
  df = load_dictionary()

  # Columns that actually exist in the sheet (exclude the synthetic 'key' column)
  sheet_columns = [c for c in df.columns if c != "key"]

  # Make sure the language column exists in the sheet
  if language not in sheet_columns:
    # Add a new header cell for this language at the end
    header_col = len(sheet_columns) + 1  # 1-based index
    gsheets.update_cell("dictionary", 1, header_col, language)
    # Update our local view
    df[language] = ""
    sheet_columns.append(language)

  key = word.lower().replace(" ", "_")
  row = df[df["key"] == key]

  if not row.empty:
    value = row.iloc[0].get(language, "")
    row_index = row.index[0] + 2  # +2 for header and 0-based index
    # Treat "", None, NaN, or whitespace as missing
    if isinstance(value, str):
      if value.strip() == "":
        value = None
    
    if pd.isna(value) or value is None:
      # Generate new lexeme
      new_lexeme = llm_lexeme(word, language)
      col_index = sheet_columns.index(language) + 1
      gsheets.update_cell("dictionary", row_index, col_index, new_lexeme)
      return new_lexeme
    
    # Otherwise the lexeme is valid
    return value

  # Word is NOT in dictionary → append a new row
  new_lexeme = llm_lexeme(word, language)

  # Build a row aligned with actual sheet columns (no 'key')
  row_data = []
  for col in sheet_columns:
    if col.lower() == "category":
      row_data.append("")       # category blank for now
    elif col.lower() == "word":
      row_data.append(word)
    elif col == language:
      row_data.append(new_lexeme)
    else:
      row_data.append("")

  gsheets.append_row("dictionary", row_data)
  return new_lexeme


# ------------------------------------------
# TEST
# ------------------------------------------

if __name__ == "__main__":
  print("Testing lexeme generator for per-language entries.")
  while True:
    w = input("Enter word: ")
    if w.lower() in ("exit", "quit"):
      break
    lang = input("Language column name: ")
    print(find_or_generate(w, lang))