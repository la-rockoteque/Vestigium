# gsheets_client.py
"""
Centralized Google Sheets access:
- Hardcoded master sheet ID
- Registry of tab names (dictionary, grammar, profiles, etc.)
- Unified authentication
- Convenience wrappers for reading and writing
"""

import gspread
import pandas as pd
from google.oauth2.service_account import Credentials
from gspread.utils import rowcol_to_a1
from typing import Literal

TabKey = Literal["dictionary", "grammar", "scripts", "languages", "phonetics"]

class GSheetsClient:
  def __init__(
      self,
      creds_path="key.json",
      scopes=("https://www.googleapis.com/auth/spreadsheets",),
      sheet_id="11tldmRm7Ggx2a0dDdQuPxmxkANDyWjdffRGgvhvJEl0"
  ):
    """
    Create a Sheets client tied to a single master sheet.
    You should use one spreadsheet for:
        - Dictionary
        - Grammar
        - Scripts
        - Profiles
        - Anything language-related
    """
    self.creds_path = creds_path
    self.scopes = scopes
    self.sheet_id = sheet_id
    self._df_cache = {}
    # Tab registry (all editable by you)
    self.tabs: dict[TabKey, str] = {
      "dictionary": "Dictionary",
      "grammar": "Grammar",
      "scripts": "Scripts",
      "languages": "Language",
      "phonetics": "Phonetics",
    }

    self._client = None

  # -------------------------------------------------------
  # AUTHENTICATION
  # -------------------------------------------------------

  @property
  def client(self):
    """Authenticate lazily and reuse the session."""
    if self._client is None:
      creds = Credentials.from_service_account_file(
        self.creds_path, scopes=self.scopes
      )
      self._client = gspread.authorize(creds)
    return self._client

  # -------------------------------------------------------
  # WORKSHEET HANDLING
  # -------------------------------------------------------

  def ws(self, tab_key: TabKey):
    """
    Return a Worksheet given a logical key ("dictionary", "grammar", etc.)
    """
    tab_name = self.tabs.get(tab_key)
    if not tab_name:
      raise KeyError(f"Unknown sheet tab '{tab_key}'")

    sheet = self.client.open_by_key(self.sheet_id)
    return sheet.worksheet(tab_name)

  # -------------------------------------------------------
  # READ OPERATIONS
  # -------------------------------------------------------

  def get_records(self, tab_key: TabKey):
    ws = self.ws(tab_key)
    return ws.get_all_records()

  def get_df(self, tab_key: TabKey) -> pd.DataFrame:
    # Return cached version if available
    if tab_key in self._df_cache:
      return self._df_cache[tab_key].copy()
  
    # Otherwise load from Google Sheets
    data = self.get_records(tab_key)
    df = pd.DataFrame(data)
    df.columns = [str(c).strip() for c in df.columns]
  
    # Cache it
    self._df_cache[tab_key] = df.copy()
  
    return df

  # -------------------------------------------------------
  # WRITE OPERATIONS
  # -------------------------------------------------------

  def invalidate(self, tab_key: TabKey):
    if tab_key in self._df_cache:
      del self._df_cache[tab_key]

  def update_cell(self, tab_key: TabKey, row: int, col: int, value):
    ws = self.ws(tab_key)
    ws.update_cell(row, col, value)
    self.invalidate(tab_key)

  def update_range(self, tab_key: TabKey, cell_range: str, values):
    ws = self.ws(tab_key)
    ws.update(cell_range, values)
    self.invalidate(tab_key)

  def append_row(self, tab_key: TabKey, row_values: list):
    ws = self.ws(tab_key)
    ws.append_row(row_values)
    self.invalidate(tab_key)

  def batch_update(self, tab_key: TabKey, updates: list[tuple[int, int, str]]):
    """Perform many cell updates in one Google Sheets values_batch_update call.
    updates = [(row, col, value), ...]
    """
    ws = self.ws(tab_key)
    tab_name = self.tabs.get(tab_key)
    if not tab_name:
      raise KeyError(f"Unknown sheet tab '{tab_key}'")

    data = []
    for row, col, value in updates:
      a1 = rowcol_to_a1(row, col)
      rng = f"{tab_name}!{a1}"
      data.append({
        "range": rng,
        "values": [[value]],
      })

    body = {
      "valueInputOption": "RAW",
      "data": data,
    }

    ws.spreadsheet.values_batch_update(body)
    self.invalidate(tab_key)


    
# -------------------------------------------------------
# OfflineSheetsClient class added here
# -------------------------------------------------------

class OfflineSheetsClient:
  """
  Drop-in replacement for GSheetsClient when running with --offline.
  Uses a local XLSX file instead of gspread.
  """

  def __init__(self, path="Language.xlsx"):
    import os
    self.path = path
    if not os.path.exists(path):
      raise FileNotFoundError(f"Offline sheet not found: {path}")
    self._df_cache = {}
    # Same tab registry

    self.tabs: dict[TabKey, str] = {
      "dictionary": "Dictionary",
      "grammar": "Grammar",
      "scripts": "Scripts",
      "languages": "Language",
      "phonetics": "Phonetics",
    }

  def get_df(self, tab_key: TabKey):
    import pandas as pd
    if tab_key in self._df_cache:
      return self._df_cache[tab_key].copy()

    sheet_name = self.tabs.get(tab_key)
    if not sheet_name:
      raise KeyError(f"Unknown sheet tab '{tab_key}'")

    df = pd.read_excel(self.path, sheet_name=sheet_name)
    df.columns = [str(c).strip() for c in df.columns]
    self._df_cache[tab_key] = df.copy()
    return df

  def invalidate(self, tab_key: TabKey):
    if tab_key in self._df_cache:
      del self._df_cache[tab_key]

  def ws(self, tab_key: TabKey):
    raise NotImplementedError("Offline mode does not provide worksheet handles.")

  def update_cell(self, tab_key: TabKey, row: int, col: int, value):
    import pandas as pd
    df = self.get_df(tab_key)
    df.iat[row - 2, col - 1] = value  # adjust for header
    self._df_cache[tab_key] = df.copy()
    self._write_xlsx()

  def update_range(self, tab_key: TabKey, cell_range: str, values):
    import pandas as pd
    import re
    df = self.get_df(tab_key)

    # Basic range parser: "A2:C4"
    m = re.match(r"([A-Z]+)(\d+):([A-Z]+)(\d+)", cell_range)
    if not m:
      raise ValueError(f"Invalid cell range: {cell_range}")
    col1, row1, col2, row2 = m.groups()

    def col_to_idx(c):
      idx = 0
      for ch in c:
        idx = idx*26 + (ord(ch) - 64)
      return idx - 1

    r1 = int(row1) - 2
    r2 = int(row2) - 2
    c1 = col_to_idx(col1)
    c2 = col_to_idx(col2)

    v_idx = 0
    for r in range(r1, r2 + 1):
      for c in range(c1, c2 + 1):
        df.iat[r, c] = values[v_idx // (c2 - c1 + 1)][c - c1]
      v_idx += 1

    self._df_cache[tab_key] = df.copy()
    self._write_xlsx()

  def append_row(self, tab_key: TabKey, row_values: list):
    import pandas as pd
    df = self.get_df(tab_key)
    df.loc[len(df)] = row_values
    self._df_cache[tab_key] = df.copy()
    self._write_xlsx()

  def _write_xlsx(self):
    import pandas as pd
    with pd.ExcelWriter(self.path, engine="openpyxl", mode="w") as writer:
      for key, sheet_name in self.tabs.items():
        if key in self._df_cache:
          self._df_cache[key].to_excel(writer, sheet_name=sheet_name, index=False)

  def batch_update(self, tab_key: TabKey, updates: list[tuple[int, int, str]]):
    import pandas as pd
    df = self.get_df(tab_key)

    for row, col, value in updates:
      df.iat[row - 2, col - 1] = value

    # Update cache and write the whole file once
    self._df_cache[tab_key] = df.copy()
    self._write_xlsx()

    
# -------------------------------------------------------
# Optional global singleton
# -------------------------------------------------------

gsheets = GSheetsClient()