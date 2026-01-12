"""
Upload generated videos to Google Drive for mobile access.
Uses OAuth for personal Drive storage.
"""
import os
from pathlib import Path
from datetime import datetime
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload

# Project paths
PROJECT_ROOT = Path(__file__).parent.parent
CONFIG_PATH = PROJECT_ROOT / "config"
OUTPUT_PATH = PROJECT_ROOT / "output"

# Load environment variables
from dotenv import load_dotenv
load_dotenv(CONFIG_PATH / ".env")

SCOPES = ['https://www.googleapis.com/auth/drive.file']
FOLDER_NAME = "BookieBenchmark Videos"


def get_drive_service():
    """Initialize Google Drive service using OAuth."""
    creds = None
    token_path = CONFIG_PATH / "drive_token.json"
    creds_path = CONFIG_PATH / "credentials.json"

    # Check for existing token
    if token_path.exists():
        creds = Credentials.from_authorized_user_file(str(token_path), SCOPES)

    # If no valid credentials, authenticate
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            if not creds_path.exists():
                print("credentials.json not found in config/")
                print("Download OAuth credentials from Google Cloud Console:")
                print("  1. Go to APIs & Services > Credentials")
                print("  2. Create OAuth 2.0 Client ID (Desktop app)")
                print("  3. Download JSON and save as config/credentials.json")
                return None

            flow = InstalledAppFlow.from_client_secrets_file(str(creds_path), SCOPES)
            creds = flow.run_local_server(port=0)

        # Save token for future use
        with open(token_path, 'w') as token:
            token.write(creds.to_json())

    return build('drive', 'v3', credentials=creds)


def get_or_create_folder(service, folder_name):
    """Get or create a folder in Google Drive."""
    # Search for existing folder
    query = f"name='{folder_name}' and mimeType='application/vnd.google-apps.folder' and trashed=false"
    results = service.files().list(q=query, spaces='drive', fields='files(id, name)').execute()
    files = results.get('files', [])

    if files:
        return files[0]['id']

    # Create folder
    folder_metadata = {
        'name': folder_name,
        'mimeType': 'application/vnd.google-apps.folder'
    }
    folder = service.files().create(body=folder_metadata, fields='id').execute()
    print(f"Created folder: {folder_name}")
    return folder['id']


def upload_video(service, file_path, folder_id):
    """Upload a video file to Google Drive."""
    file_name = os.path.basename(file_path)

    # Check if file already exists in folder
    query = f"name='{file_name}' and '{folder_id}' in parents and trashed=false"
    results = service.files().list(q=query, spaces='drive', fields='files(id)').execute()

    if results.get('files'):
        print(f"  Already uploaded: {file_name}")
        return results['files'][0]['id']

    file_metadata = {
        'name': file_name,
        'parents': [folder_id]
    }

    media = MediaFileUpload(
        file_path,
        mimetype='video/mp4',
        resumable=True
    )

    file = service.files().create(
        body=file_metadata,
        media_body=media,
        fields='id, webViewLink'
    ).execute()

    print(f"  Uploaded: {file_name}")
    return file.get('id')


def upload_todays_videos():
    """Upload all videos generated today to Google Drive."""
    service = get_drive_service()
    if not service:
        return False

    # Get or create the videos folder
    folder_id = get_or_create_folder(service, FOLDER_NAME)

    # Find today's videos (format: YYYYMMDD_*)
    today = datetime.now().strftime("%Y%m%d")
    video_files = list(OUTPUT_PATH.glob(f"{today}*.mp4"))

    if not video_files:
        # Also check for tomorrow's date (morning pipeline generates for next day)
        from datetime import timedelta
        tomorrow = (datetime.now() + timedelta(days=1)).strftime("%Y%m%d")
        video_files = list(OUTPUT_PATH.glob(f"{tomorrow}*.mp4"))

    if not video_files:
        print("No videos to upload for today")
        return True

    print(f"Uploading {len(video_files)} videos to Google Drive...")

    for video_path in video_files:
        upload_video(service, str(video_path), folder_id)

    print(f"Upload complete! Check '{FOLDER_NAME}' folder in Google Drive")
    return True


def upload_all_videos():
    """Upload all videos in output folder to Google Drive."""
    service = get_drive_service()
    if not service:
        return False

    folder_id = get_or_create_folder(service, FOLDER_NAME)
    video_files = list(OUTPUT_PATH.glob("*.mp4"))

    if not video_files:
        print("No videos to upload")
        return True

    print(f"Uploading {len(video_files)} videos to Google Drive...")

    for video_path in sorted(video_files):
        upload_video(service, str(video_path), folder_id)

    print(f"Upload complete!")
    return True


if __name__ == "__main__":
    import sys
    if len(sys.argv) > 1 and sys.argv[1] == "--all":
        upload_all_videos()
    else:
        upload_todays_videos()
