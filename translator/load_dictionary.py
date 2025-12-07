from gsheets_client import gsheets

def load_dictionary():
  df = gsheets.get_df("dictionary")
  df["key"] = df["Word"].str.lower().str.replace(" ", "_")
  return df


if __name__ == "__main__":
  d = load_dictionary()
  print(list(d.keys())[:20])