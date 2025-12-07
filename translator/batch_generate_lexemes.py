#!/usr/bin/env python3
"""
batch_generate_lexemes.py

Batch-generates lexemes for all words in all languages.

Usage:
  python batch_generate_lexemes.py                    # Generate for all languages
  python batch_generate_lexemes.py --lang=Ashen       # Generate for specific language
  python batch_generate_lexemes.py --offline          # Use local XLSX file
  python batch_generate_lexemes.py --force            # Overwrite existing cells
"""

import sys
import math

from gsheets_client import gsheets, OfflineSheetsClient
from generator import llm_lexeme
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
  return [lang_flag]


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

  # Load dictionary
  df = client.get_df("dictionary")

  # Ensure 'key' column exists
  if "key" not in df.columns:
    df["key"] = df["Word"].astype(str).str.lower().str.replace(" ", "_")

  target_langs = get_target_languages(df, lang_flag)

  print("Target languages:", ", ".join(target_langs))

  # Walk through each word and each target language
  for idx, row in df.iterrows():
    word = str(row["Word"]).strip()
    if not word:
      continue

    # Sheet row index (header is row 1, df starts at row 0)
    row_index = idx + 2

    for lang in target_langs:
      current = row.get(lang, "")

      # Treat NaN as empty
      if isinstance(current, float) and math.isnan(current):
        print(f"[WARN] {word!r} [{lang}] → NaN detected")
        current = ""

      # Skip already-filled cells (unless --force is used)
      if isinstance(current, str) and current.strip():
        if not force:
          print(f"[SKIP] {word!r} [{lang}] → Already filled (use --force to overwrite)")
          continue
        else:
          print(f"[INFO] {word!r} [{lang}] → Overwriting existing value: {current!r}")

      # Generate lexeme via LLM
      try:
        lexeme = llm_lexeme(word, lang)
        print(f"[INFO] {word!r} [{lang}] → LLM generated {lexeme!r}")
      except Exception as e:
        print(f"[ERROR] {word!r} [{lang}] → LLM failed: {e}")
        continue

      # Compute sheet column (1-based)
      col_index = df.columns.get_loc(lang) + 1

      print(f"{word!r} [{lang}] → {lexeme!r}  (row {row_index}, col {col_index})")

      # Write back
      updates.append((row_index, col_index, lexeme))

  # Apply batched updates
  if updates:
    try:
      client.batch_update("dictionary", updates)
    except AttributeError:
      # Fallback if batch_update is not implemented: apply individually
      for r, c, v in updates:
        client.update_cell("dictionary", r, c, v)


if __name__ == "__main__":
  main()