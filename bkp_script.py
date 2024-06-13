#Configurar google API
#Criar credenciais e dar autorizações
#ler arquivos do disco
#comparar com o drive
#copiar os que forem diferentes

import os
import google.auth
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from googleapiclient.http import MediaFileUpload


#insira aqui a pasta alvo
folder_path = "C:\\Users\\felip\\Teste de backup"

files = os.listdir(folder_path)

file_path = [os.path.join(folder_path, file) for file in files]


# Escopos necessários para acessar o Google Drive
SCOPES = ['https://www.googleapis.com/auth/drive']

# Caminho para o arquivo de credenciais JSON
CREDENTIALS_FILE = 'D:\\Felipe\\defesa_cibernetica\\Estacio\\trabalho_python\\credentials.json'

#authentication
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



def folder_create():

  try:

    creds = authenticate()
    service = build('drive', 'v3', credentials=creds)

    response = service.files().list(q="name='TESTEBKP'", spaces='drive').execute()

    if not response['files']:

      file_metadata = {
        "name": "TESTEBKP",
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




def upload_file(service, file_path, folder_id):

  file_metadata = {
    'name': os.path.basename(file_path),
    'parents': [folder_id],
    'moveToNewOwnersRoot': 'false'
  }

  media = MediaFileUpload(file_path, resumable=True)

  file = (
    service.files()
    .create(body=file_metadata, media_body=media, fields='id')
    .execute()
  )

  return file.get('id')




def list_folder():

  creds = authenticate()

  service = build('drive', 'v3', credentials=creds)

  query = f"'{folder_id}' in parents"

  results = service.files().list(q=query, pageSize=100, fields="nextPageToken, files(id, name)").execute()

  drive_files = [file['name'] for file in results['files']]

  return drive_files

drive_files = list_folder()

set_files_to_upload = set(files) - set(drive_files)

files_to_upload = list(set_files_to_upload)

ftup_path = [os.path.join(folder_path, file) for file in files_to_upload]



def main():

    for local_file_path in ftup_path:

      creds = authenticate()

      service = build('drive', 'v3', credentials=creds)

      file_id = upload_file(service, local_file_path, folder_id)

      print(f'File uploaded successfully with ID: {file_id}')

main()


