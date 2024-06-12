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
'''
#ler a pasta de origem dos arquivos
folder_path = "C:/Users/felip/Teste de backup"
def pc_folder(folder_path):
  files = os.listdir(folder_path)
  for item in files:
    #TRANSFORMAR ESSE PRINT NA SAÍDA DA VARIAVEL A SER COPIADA
    print(f"{item}")


pc_folder(folder_path)
'''


# Escopos necessários para acessar o Google Drive
SCOPES = ['https://www.googleapis.com/auth/drive.file']

# Caminho para o arquivo de credenciais JSON
CREDENTIALS_FILE = 'D:/Felipe/defesa_cibernetica/Estacio/trabalho_python/credentials.json'

#authentication
def authenticate():
  """Shows basic usage of the Drive v3 API.
  Prints the names and ids of the first 10 files the user has access to.
  """
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


def upload_file(service, file_path):
  file_metadata = {'name': os.path.basename(file_path)}
  media = MediaFileUpload(file_path, resumable=True)
  file = (
    service.files()
    .create(body=file_metadata, media_body=media, fields='id')
    .execute()
  )
  return file.get('id')


def main():
  creds = authenticate()
  service = build('drive', 'v3', credentials=creds)

  # Caminho do arquivo local
  local_file_path = "C:/Users/felip/Teste de backup/arquivotxt.txt"


  file_id = upload_file(service, local_file_path)
  print(f'File uploaded successfully with ID: {file_id}')

main()

