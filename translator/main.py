#!/usr/bin/env python3

from engine import translate
from gsheets_client import gsheets
import sys

from gsheets_client import gsheets, OfflineSheetsClient
import sys

import nltk

try:
  nltk.data.find("corpora/wordnet")
except LookupError:
  nltk.download("wordnet")

if "--offline" in sys.argv:
  print("Running in OFFLINE MODE (local XLSX)")
  gsheets = OfflineSheetsClient("Language.xlsx")

def main():
  print("Translator ready.")
  # Optional command‑line flag: --lang=<LanguageName>
  preselected_lang = None
  for arg in sys.argv[1:]:
    if arg.startswith("--lang="):
      preselected_lang = arg.split("=", 1)[1].strip()
      break

  preselected_text = None
  for arg in sys.argv[1:]:
    if arg.startswith("--text="):
      preselected_text = arg.split("=", 1)[1].strip()
      break

  df_lang = gsheets.get_df("languages")
  LANGUAGES = sorted(df_lang["Name"].dropna().unique().tolist())
  if preselected_lang:
    if preselected_lang not in LANGUAGES:
      print(f"Error: '{preselected_lang}' is not a valid language. Valid options: {', '.join(LANGUAGES)}")
      preselected_lang = None
    else:
      print(f"Prefilled language: {preselected_lang}")
  print(f"Available languages: {', '.join(LANGUAGES)}")
  while True:
    if preselected_text:
      txt = preselected_text
      preselected_text = None
      print(f"EN> {txt}")
    else:
      txt = input("EN> ")
    if txt.lower() in ("quit", "exit"):
      break

    if preselected_lang:
      tgt = preselected_lang
    else:
      print("Choose a target language:")
      for i, lang in enumerate(LANGUAGES, start=1):
        print(f"  {i}. {lang}")

      choice = input("Number> ").strip()
      if not choice.isdigit() or not (1 <= int(choice) <= len(LANGUAGES)):
        print("Invalid selection. Try again.")
        continue

      tgt = LANGUAGES[int(choice) - 1]
    out = translate(txt, tgt)
    print(f"{tgt}> {out}\n")

if __name__ == "__main__":
  main()