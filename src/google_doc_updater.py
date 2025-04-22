from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload
from google.oauth2 import service_account

def publish(file_name, file_id):
  # Setup
  SCOPES = ['https://www.googleapis.com/auth/drive']
  SERVICE_ACCOUNT_FILE = 'key.json'
  credentials = service_account.Credentials.from_service_account_file(
    SERVICE_ACCOUNT_FILE, scopes=SCOPES)
  
  drive_service = build('drive', 'v3', credentials=credentials)

  media = MediaFileUpload(file_name, mimetype='text/plain', resumable=True)
  # This replaces the file content, creating a new version
  updated_file = drive_service.files().update(
    fileId=file_id,
    media_body=media
  ).execute()
  
  print(f"File updated: {updated_file['name']} (ID: {file_id})")