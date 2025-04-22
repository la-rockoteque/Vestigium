from __future__ import print_function
import os
import io
from googleapiclient.discovery import build
from googleapiclient.http import MediaIoBaseDownload
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
import pickle
import json

# Setup the Drive v3 API
SCOPES = ['https://www.googleapis.com/auth/drive.readonly']
FOLDER_ID = '1ktMUyZkHwCaO5ixIWNv6DPuh9pa-srpR'  # Replace with your folder ID
DESTINATION = 'markdown'  # Folder where files will be saved

def authenticate():
  creds = None
  # Load previously saved credentials
  if os.path.exists('token.pickle'):
    with open('token.pickle', 'rb') as token:
      creds = pickle.load(token)
  # If no credentials or expired
  if not creds or not creds.valid:
    if creds and creds.expired and creds.refresh_token:
      creds.refresh(Request())
    else:
      flow = InstalledAppFlow.from_client_secrets_file('credentials.json', SCOPES)
      creds = flow.run_local_server(port=0)
    # Save credentials
    with open('token.pickle', 'wb') as token:
      pickle.dump(creds, token)
  return creds

def download_folder_files(service, folder_id, dest_folder):
  query = f"'{folder_id}' in parents and trashed = false"
  results = service.files().list(q=query, fields="files(id, name, mimeType)").execute()
  files = results.get('files', [])

  if not os.path.exists(dest_folder):
    os.makedirs(dest_folder)

  manifesto = {}

  for file in files:
    file_id = file['id']
    file_name = file['name']
    mime_type = file['mimeType']
    filepath = os.path.join(dest_folder, file_name)

    manifesto[file_name] = file_id

    try:
      if mime_type.startswith('application/vnd.google-apps.'):
        # Export Google Docs files (choose desired export format)
        export_mime = 'text/plain'  # or 'application/pdf', 'application/vnd.openxmlformats-officedocument.wordprocessingml.document'
        request = service.files().export_media(fileId=file_id, mimeType=export_mime)
        # Append .txt if necessary
        if not filepath.endswith('.txt'):
          filepath += '.txt'
      else:
        # Download binary file
        request = service.files().get_media(fileId=file_id)

      with io.FileIO(filepath, 'wb') as fh:
        downloader = MediaIoBaseDownload(fh, request)
        done = False
        while not done:
          status, done = downloader.next_chunk()
          print(f"Downloading {file_name} ({int(status.progress() * 100)}%)")

    except Exception as e:
      print(f"Failed to download {file_name}: {e}")

  with open(os.path.join(dest_folder, "manifesto.json"), "w", encoding="utf-8") as f:
    json.dump(manifesto, f, ensure_ascii=False, indent=4)

if __name__ == '__main__':
  creds = authenticate()
  drive_service = build('drive', 'v3', credentials=creds)
  download_folder_files(drive_service, FOLDER_ID, DESTINATION)