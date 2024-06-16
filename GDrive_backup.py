import os
import google.auth
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from googleapiclient.http import MediaFileUpload
from datetime import datetime
import time
import pytz

# insert target folder path here
folder_path = "C:\\path\\to_your\\backup_folder"

files = os.listdir(folder_path)

file_path = [os.path.join(folder_path, file) for file in files]

# Escopes for Google Drive
SCOPES = ['https://www.googleapis.com/auth/drive']

# Path do credentials JSON file downloaded from google console
CREDENTIALS_FILE = 'C:\\Path\\to_your_creds_file\\credentials.json'


# autentication
def authenticate():
    creds = None

    # The file token.json stores the user's access and refresh tokens, and is
    # created automatically when the authorization flow completes for the first
    # time.
    if os.path.exists("token.json"):
        creds = Credentials.from_authorized_user_file("token.json", SCOPES)

    # If there are no (valid) credentials available, let the user log in.
    if not creds or not creds.valid:

        if creds and creds.expired and creds.refresh_token:

            creds.refresh(Request())

        else:

            flow = InstalledAppFlow.from_client_secrets_file(
                "credentials.json", SCOPES
            )

            creds = flow.run_local_server(port=0)

        # Save the credentials for the next run
        with open("token.json", "w") as token:

            token.write(creds.to_json())

    return creds

#Google drive folder creation and/or id gather
def folder_create():
    try:

        creds = authenticate()
        service = build('drive', 'v3', credentials=creds)

        response = service.files().list(q="name='Auto_backup'", spaces='drive').execute()

        if not response['files']:

            file_metadata = {
                "name": "Auto_backup",
                "mimeType": "application/vnd.google-apps.folder"
            }

            file = service.files().create(body=file_metadata, fields="id").execute()

            folder_id = file.get('id')

        else:
            folder_id = response['files'][0]['id']

    except HttpError as error:
        print("Error: " + str(error))

    return folder_id


folder_id = folder_create()

#upload params
def upload_file(service, file_path, folder_id):
    file_metadata = {
        'name': os.path.basename(file_path),
        'parents': [folder_id],
    }

    media = MediaFileUpload(file_path, resumable=True)

    file = (
        service.files()
        .create(body=file_metadata, media_body=media, fields='id')
        .execute()
    )

    return file.get('id')

#Google drive folder enumeration
def list_folder():
    creds = authenticate()
    service = build('drive', 'v3', credentials=creds)

    query = f"'{folder_id}' in parents"

    results = service.files().list(q=query, pageSize=200, fields="nextPageToken, files(id, name)").execute()

    drive_files = [file['name'] for file in results['files']]

    return drive_files


drive_files = list_folder()

#Determine which files will be uploaded
set_files_to_upload = set(files) - set(drive_files)

files_to_upload = list(set_files_to_upload)

ftup_path = [os.path.join(folder_path, file) for file in files_to_upload]


#Determine wich files will be updated
local_recent = []
def get_last_modified():
    global local_recent
    creds = authenticate()
    service = build('drive', 'v3', credentials=creds)

    query = f"'{folder_id}' in parents"
    results = service.files().list(q=query, pageSize=100, fields="files(id, name, modifiedTime)").execute()
    files = results.get('files', [])

    drive_file_info = []
    for file in files:
        id = file.get('id')
        name = file.get('name')
        date = file.get('modifiedTime')
        if date:
            utc_date = datetime.strptime(date, "%Y-%m-%dT%H:%M:%S.%fZ").replace(tzinfo=pytz.UTC) #UTC transform for timezone issues
            epoch_date = int(utc_date.timestamp())
            drive_file_info.append((id, name, epoch_date))

    local_file_info = []
    for file in os.listdir(folder_path):
        file_path = os.path.join(folder_path, file)
        if os.path.isfile(file_path):
            date = int(os.path.getmtime(file_path))
            local_file_info.append((file, date))

    # compare timestamps
    for local_file, local_date_modif in local_file_info:
        for drive_id, drive_name, drive_date_modif in drive_file_info:
            if local_file == drive_name:
                if local_date_modif > drive_date_modif:
                    local_recent.append(local_file)
                break

get_last_modified()

#targeting files to overwrite
def find_file(service, file_name):
    results = service.files().list(q=f"name = '{file_name}'", fields="files(id)").execute()
    items = results.get('files', [])
    if items:
        return items[0]['id']
    else:
        return None

#
def update_file(service, file_id, file_path):
    file_metadata = {'name': os.path.basename(file_path)}
    media = MediaFileUpload(file_path, resumable=True)
    file = service.files().update(fileId=file_id, body=file_metadata, media_body=media, fields="id").execute()
    return file


def update():
    creds = authenticate()
    service = build('drive', 'v3', credentials=creds)

    for files in local_recent:
        file_id = find_file(service, files)
        updated_file_path = os.path.join(folder_path, files)

        if file_id:
            updated_file = update_file(service, file_id, updated_file_path)
            print(f'File Updated: {updated_file}')


def upload():
    creds = authenticate()
    service = build('drive', 'v3', credentials=creds)

    for local_file_path in ftup_path:
        file_id = upload_file(service, local_file_path, folder_id)

        print(f'File uploaded ID: {file_id}')




# Write log file
def write_backup_log():
    now = datetime.now()
    timestamp = now.strftime("%Y-%m-%d %H:%M:%S")
    log_content = f"Data do ultimo backup: {timestamp}, Arquivos atualizados: \n"
    log_file_path = os.path.join(folder_path, 'backup.log')

    with open(log_file_path, "a") as log:
        log.write(log_content)

upload()
update()
write_backup_log()


