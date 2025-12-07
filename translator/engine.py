# engine.py
from generator import find_or_generate

from profiles import LANG_PROFILES
from lexicon import concept_for

def generate_lexeme(lang, key):
  return find_or_generate(key, lang.name)

def translate_word(lang, word):
  key = concept_for(word)
  form = generate_lexeme(lang, key)
  if lang.profile == "F":
    return f"<scent:{key}>"
  return form

def translate_sentence(lang, words):
  # Special Florathic case
  if lang.profile == "F":
    return " ".join(f"<scent:{w}>" for w in words)

  # Generic language: translate each word independently
  translated = [translate_word(lang, w) for w in words]
  return " ".join(translated)

def translate(text, target):
  lang = LANG_PROFILES[target]
  words = text.split()
  if len(words) < 2:
    return translate_word(lang, text)
  return translate_sentence(lang, words)