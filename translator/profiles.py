import re
from gsheets_client import gsheets

class LanguageProfile:
  def __init__(self, name, profile, word_order, morphology, particles, sound_changes, representation="spoken"):
    self.name = name
    self.profile = profile
    self.word_order = word_order
    self.morphology = morphology
    self.particles = particles
    self.sound_changes = sound_changes
    self.representation = representation

  def apply_sound_changes(self, proto):
    form = proto
    for pattern, repl in self.sound_changes:
      form = re.sub(pattern, repl, form)
    return form

  def shape_noun(self, base, plural=False, ergative=False):
    if self.profile == "A":
      form = base
      if plural:
        form += self.morphology.get("plural_suffix", "")
      if ergative:
        form += self.morphology.get("ergative", "")
      return form

    if self.profile == "B":
      form = base
      parts = []
      if plural:
        parts.append(self.morphology.get("plural_particle", ""))
      return " ".join([form] + parts).strip()

    if self.profile == "F":
      return f"<scent:{base}>"

    return base

  def shape_verb(self, base):
    return base

  def negate(self, words):
    neg = self.particles.get("neg")
    if self.profile == "A":
      verb_index = 1 if len(words) > 1 else 0
      words[verb_index] = words[verb_index] + "-neg"
      return words

    if neg:
      return [neg] + words

    return words

def load_grammar_profiles():
    df = gsheets.get_df("grammar")

    profiles = {}
    # Languages are columns except the first column which is 'Grammar Category'
    languages = df.columns[1:]

    for lang in languages:
        word_order_row = df[df['Grammar Category'] == "Basic Word Order"]
        if not word_order_row.empty:
            word_order = word_order_row[lang].values[0]
        else:
            word_order = None

        profile_code_row = df[df['Grammar Category'] == "Profile Code"]
        if not profile_code_row.empty:
            profile_code = profile_code_row[lang].values[0]
            if not profile_code:
                profile_code = "A"
        else:
            profile_code = "A"

        morphology = {}
        particles = {}
        sound_changes = []

        profiles[lang] = LanguageProfile(
            name=lang,
            profile=profile_code,
            word_order=word_order,
            morphology=morphology,
            particles=particles,
            sound_changes=sound_changes
        )
    return profiles

try:
    LANG_PROFILES = load_grammar_profiles()
except Exception as e:
    print("Failed to load Grammar sheet profiles, falling back to empty:", e)
    LANG_PROFILES = {}