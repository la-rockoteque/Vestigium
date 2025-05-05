#!/usr/bin/env python3
import re
import sys
from google.oauth2.service_account import Credentials
from googleapiclient.discovery import build

def extract_deities(input_path):
    """
    Parse a markdown file for level-2 headings ("## Name") immediately
    followed by a table (line beginning with '|'), and extract
    Name, Alignment, Symbol, Description, and optionally a Quote.
    Returns a list of dictionaries.
    """
    deities = []
    with open(input_path, 'r', encoding='utf-8') as f:
        lines = f.readlines()

    idx = 0
    while idx < len(lines):
        line = lines[idx]
        m = re.match(r'^##\s*(.+)$', line)
        if not m:
            idx += 1
            continue
        name = m.group(1).strip().strip('*')
        # Look ahead past blank lines to see if next meaningful line is a table row
        j = idx + 1
        while j < len(lines) and not lines[j].strip():
            j += 1
        if j >= len(lines) or not lines[j].lstrip().startswith('|'):
            idx += 1
            continue
        # Found a deity section
        deity = {'Name': name, 'Alignment': '', 'Symbol': '', 'Description': '', 'Quote': ''}
        # Parse table rows for Alignment and Symbol
        table_end = j
        while table_end < len(lines) and lines[table_end].lstrip().startswith('|'):
            row = lines[table_end]
            # Match something like | **Alingment** | Lawful-Good |
            align_match = re.match(r'\|\s*\*\*Alingment\*\*\s*\|\s*([^\|]+)\|', row, re.IGNORECASE)
            if not align_match:
                align_match = re.match(r'\|\s*\*\*Alignment\*\*\s*\|\s*([^\|]+)\|', row, re.IGNORECASE)
            if align_match:
                deity['Alignment'] = align_match.group(1).strip()
            symbol_match = re.match(r'\|\s*\*\*Symbol\*\*\s*\|\s*([^\|]+)\|', row, re.IGNORECASE)
            if symbol_match:
                deity['Symbol'] = symbol_match.group(1).strip()
            table_end += 1
        # After table, look for description and quote
        desc = []
        quote = []
        found_quote = False
        found_attribution = False
        k = table_end
        # Skip blank lines
        while k < len(lines) and not lines[k].strip():
            k += 1
        # Check for quote block
        if k < len(lines) and lines[k].lstrip().startswith('{{quote'):
            found_quote = True
            # Consume lines until we see {{attribution or end of quote
            while k < len(lines):
                qline = lines[k].rstrip('\n')
                quote.append(qline)
                if qline.strip().startswith('{{attribution'):
                    found_attribution = True
                    quote[-1] = qline  # include attribution
                    k += 1
                    break
                k += 1
            # Remove {{quote and {{attribution lines from quote text
            if quote:
                # Remove first line if it starts with {{quote
                if quote[0].lstrip().startswith('{{quote'):
                    quote = quote[1:]
                # Remove last line if it starts with {{attribution
                if quote and quote[-1].lstrip().startswith('{{attribution'):
                    quote = quote[:-1]
            deity['Quote'] = '\n'.join([q.lstrip() for q in quote]).strip()
            # Skip blank lines after quote
            while k < len(lines) and not lines[k].strip():
                k += 1
            # Skip any remaining '}}' lines or blank lines after quote block
            while k < len(lines) and (lines[k].strip() == '}}' or not lines[k].strip()):
                k += 1
        # Now, next paragraph is the description
        desc_lines = []
        while k < len(lines):
            dline = lines[k]
            # Stop at next heading or table or block
            if dline.strip().startswith('#') or dline.lstrip().startswith('|') or dline.strip().startswith('{{'):
                break
            desc_lines.append(dline.rstrip('\n'))
            k += 1
        # Strip trailing blank lines
        while desc_lines and not desc_lines[-1].strip():
            desc_lines.pop()
        # Remove leading blank lines as well
        while desc_lines and not desc_lines[0].strip():
            desc_lines.pop(0)
        deity['Description'] = '\n'.join(desc_lines).strip()
        deities.append(deity)
        idx = k if k > idx else idx + 1
    return deities

def upload_to_sheets(deities, spreadsheet_id, range_name, credentials_file):
    """
    Upload a list of deity dictionaries to a Google Sheets spreadsheet.
    """
    scopes = ['https://www.googleapis.com/auth/spreadsheets']
    creds = Credentials.from_service_account_file(credentials_file, scopes=scopes)
    service = build('sheets', 'v4', credentials=creds)
    sheet = service.spreadsheets()
    # Header row
    header = ['Name', 'Alignment', 'Symbol', 'Description', 'Quote']
    values = [header]
    for deity in deities:
        row = [
            deity.get('Name', ''),
            deity.get('Alignment', ''),
            deity.get('Symbol', ''),
            deity.get('Description', ''),
            deity.get('Quote', ''),
        ]
        values.append(row)
    body = {'values': values}
    # Clear existing content in the sheet
    sheet.values().clear(spreadsheetId=spreadsheet_id, range=range_name).execute()
    # Write new data
    sheet.values().update(
        spreadsheetId=spreadsheet_id,
        range=range_name,
        valueInputOption='RAW',
        body=body
    ).execute()

# https://docs.google.com/spreadsheets/d/1I4FHncl40_xx1Udc_Q2rWWWvpL6xaMlpJyY90WBftag/edit?gid=1410134136#gid=1410134136
if __name__ == '__main__':
    if len(sys.argv) != 5:
        print(f"Usage: {sys.argv[0]} <input_markdown> <spreadsheet_id> <range_name> <credentials.json>")
        sys.exit(1)
    input_md, spreadsheet_id, range_name, credentials_file = sys.argv[1:]
    deities = extract_deities(input_md)
    upload_to_sheets(deities, spreadsheet_id, range_name, credentials_file)
    print(f"Uploaded {len(deities)} deities to Google Sheet {spreadsheet_id} (range {range_name})")