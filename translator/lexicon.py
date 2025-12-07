# lexicon.py
from load_dictionary import load_dictionary
import re
from nltk.stem import WordNetLemmatizer
lemmatizer = WordNetLemmatizer()

DICTIONARY = load_dictionary()    # If this returns df, we need df, not dict

def clean_token(t):
  return re.sub(r"[^a-zA-Z_]", "", t).lower()

def concept_for(word):
  clean = clean_token(word)
  if not clean:
    return None
  lemma = lemmatizer.lemmatize(clean)
  return lemma