#!/usr/bin/env python3
"""
batch_generate_phonetics.py

Batch-generates IPA phonetic notation for all words in all languages.
Reads lexemes from the Dictionary sheet and writes phonetics to the Phonetics sheet.

Usage:
  python batch_generate_phonetics.py                    # Generate for all languages
  python batch_generate_phonetics.py --lang=Ashen       # Generate for specific language
  python batch_generate_phonetics.py --offline          # Use local XLSX file
  python batch_generate_phonetics.py --force            # Overwrite existing cells
"""

import sys
import math

from gsheets_client import gsheets, OfflineSheetsClient
import pandas as pd

updates = []


def get_client():
  """Choose online or offline client based on flags."""
  offline = "--offline" in sys.argv
  if offline:
    print("Using OFFLINE XLSX client")
    return OfflineSheetsClient("Language.xlsx")
  else:
    print("Using ONLINE Google Sheets client")
    return gsheets


def get_target_languages(df: pd.DataFrame, lang_flag: str | None):
  """
  Determine which language columns to process.

  We treat Category, Word, key as non-language.
  Everything else is considered a language column.
  """
  non_lang = {"Category", "Word", "key"}
  all_langs = [c for c in df.columns if c not in non_lang]

  if lang_flag is None:
    return all_langs

  # Case-insensitive matching for language name
  lookup = {c.lower(): c for c in all_langs}
  wanted = lang_flag.lower()
  if wanted not in lookup:
    raise SystemExit(
      f"Language '{lang_flag}' not found. "
      f"Available: {', '.join(all_langs)}"
    )
  return [lookup[wanted]]


def llm_phonetics(word, language):
  """
  Generate IPA phonetic notation for a word using LLM.

  Args:
    word: The lexeme to generate phonetics for
    language: The name of the language

  Returns:
    IPA phonetic transcription string
  """
  try:
    from llm_wordgen.prompts import phonetics_prompt
    import ollama

    # Build the prompt
    prompt = phonetics_prompt(word, language)

    print(f"[LLM] Generating phonetics for {word!r} in {language}")

    # Use the LLM to generate phonetics
    result = ollama.generate(model="llama3", prompt=prompt)

    # Extract the response
    response = result['response'].strip()

    print(f"[DEBUG] Raw LLM response: {response!r}")

    # Clean up the response - remove quotes, extra spaces
    phonetics = response.strip('"\'` \t\n')

    # If the response doesn't have slashes, add them
    if not phonetics.startswith('/'):
      phonetics = '/' + phonetics
    if not phonetics.endswith('/'):
      phonetics = phonetics + '/'

    print(f"[INFO] Generated phonetics: {phonetics!r}")
    return phonetics

  except Exception as e:
    print(f"[ERROR] LLM failed to generate phonetics for {word!r} in {language}: {e}")
    # Return a placeholder
    return f"/{word}/"


def main():
  # Parse optional flags
  lang_flag = None
  force = False
  args = sys.argv[1:]
  i = 0
  while i < len(args):
    arg = args[i]
    if arg.startswith("--lang="):
      lang_flag = arg.split("=", 1)[1].strip()
      i += 1
    elif arg == "--lang" and i + 1 < len(args):
      lang_flag = args[i + 1].strip()
      i += 2
    elif arg == "--force":
      force = True
      i += 1
    else:
      i += 1

  client = get_client()

  # Load dictionary sheet (source of words/lexemes)
  dict_df = client.get_df("dictionary")

  # Load or create phonetics sheet (destination)
  try:
    phonetics_df = client.get_df("phonetics")
  except Exception as e:
    print(f"[WARN] Could not load phonetics sheet: {e}")
    print("[INFO] Creating new phonetics sheet with same structure as dictionary")
    # Create empty phonetics sheet with same structure
    phonetics_df = dict_df.copy()
    # Clear all language columns (keep only structure)
    for col in phonetics_df.columns:
      if col not in {"Category", "Word", "key"}:
        phonetics_df[col] = ""

  # Ensure both sheets have the same columns
  # Add any missing columns from dict to phonetics
  for col in dict_df.columns:
    if col not in phonetics_df.columns:
      phonetics_df[col] = ""

  # Ensure 'key' column exists in both
  if "key" not in dict_df.columns:
    dict_df["key"] = dict_df["Word"].astype(str).str.lower().str.replace(" ", "_")
  if "key" not in phonetics_df.columns:
    phonetics_df["key"] = phonetics_df["Word"].astype(str).str.lower().str.replace(" ", "_")

  target_langs = get_target_languages(dict_df, lang_flag)

  print("Target languages:", ", ".join(target_langs))

  # Walk through each word and each target language
  for idx, dict_row in dict_df.iterrows():
    english_word = str(dict_row["Word"]).strip()
    if not english_word:
      continue

    # Sheet row index (header is row 1, df starts at row 0)
    row_index = idx + 2

    for lang in target_langs:
      # Get the lexeme from dictionary
      lexeme = dict_row.get(lang, "")

      # Treat NaN as empty
      if isinstance(lexeme, float) and math.isnan(lexeme):
        print(f"[SKIP] {english_word!r} [{lang}] → No lexeme in dictionary")
        continue

      # Skip if no lexeme
      if not isinstance(lexeme, str) or not lexeme.strip():
        print(f"[SKIP] {english_word!r} [{lang}] → No lexeme in dictionary")
        continue

      lexeme = lexeme.strip()

      # Check if phonetics already exists
      if idx < len(phonetics_df):
        phonetics_row = phonetics_df.iloc[idx]
        current_phonetics = phonetics_row.get(lang, "")

        # Treat NaN as empty
        if isinstance(current_phonetics, float) and math.isnan(current_phonetics):
          current_phonetics = ""

        # Skip already-filled cells (unless --force is used)
        if isinstance(current_phonetics, str) and current_phonetics.strip():
          if not force:
            print(f"[SKIP] {english_word!r} [{lang}] → Phonetics already filled (use --force to overwrite)")
            continue
          else:
            print(f"[INFO] {english_word!r} [{lang}] → Overwriting existing phonetics: {current_phonetics!r}")

      # Generate phonetics via LLM
      try:
        phonetics = llm_phonetics(lexeme, lang)
        print(f"[INFO] {english_word!r} [{lang}] → Lexeme: {lexeme!r} → Phonetics: {phonetics!r}")
      except Exception as e:
        print(f"[ERROR] {english_word!r} [{lang}] → Phonetics generation failed: {e}")
        continue

      # Compute sheet column (1-based)
      col_index = dict_df.columns.get_loc(lang) + 1

      print(f"{english_word!r} [{lang}] → {phonetics!r}  (row {row_index}, col {col_index})")

      # Write back to phonetics sheet
      updates.append((row_index, col_index, phonetics))

  # Apply batched updates
  if updates:
    print(f"\nApplying {len(updates)} updates to phonetics sheet...")
    try:
      client.batch_update("phonetics", updates)
      print("✓ All updates applied successfully")
    except AttributeError:
      # Fallback if batch_update is not implemented: apply individually
      print("Batch update not available, applying individually...")
      for r, c, v in updates:
        client.update_cell("phonetics", r, c, v)
      print("✓ All updates applied")
  else:
    print("\nNo updates needed - all cells already filled or no lexemes found")


if __name__ == "__main__":
  main()