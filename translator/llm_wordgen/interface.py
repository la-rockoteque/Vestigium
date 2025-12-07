# llm_wordgen/interface.py

class LexemeGenerator:
  """
  Base interface for any lexeme generator.
  Swap backends (Ollama, LM Studio, llama.cpp) without touching core logic.
  """
  def generate(self, concept, language, grammar_info, examples, language_metadata=None):
    """
    Return a lexeme string.
    concept:    English word meaning
    language:   Name of language column ("Brimic", "Concordian", etc.)
    grammar_info: phonology or rules from Grammar sheet
    examples:   list of existing words in this language
    language_metadata: metadata about the language from the Language sheet
    """
    raise NotImplementedError