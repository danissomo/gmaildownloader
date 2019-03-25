from __future__ import print_function
import plyer
import configparser
import os.path
import pickle
import json
from google.auth.transport.requests import Request
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
import base64
import email
from apiclient import errors
SCOPES = ['https://www.googleapis.com/auth/gmail.readonly', 'https://mail.google.com/',
'https://www.googleapis.com/auth/gmail.modify',
'https://www.googleapis.com/auth/gmail.labels']
PATH= 'C:\\\\rob\\'
NOTIFICATIONS=True
MAXSIZE= 200
KEYWORD= ''
def GetMessage(service, user_id, msg_id):
  try:
    message = service.users().messages().get(userId=user_id, id=msg_id).execute()
    return message['snippet']
  except errors.HttpError:
    print ('An error occurred: %s' % error)

def GetAttachments(service, user_id, msg_id, store_dir):
  try:
    find=False
    message = service.users().messages().get(userId=user_id, id=msg_id).execute()
    for part in message['payload']['parts']:
      if 'attachmentId'in part['body']:
        attID = part['body']['attachmentId']
        try:
          file_database=open('assets\\database.json','r' )
        except:
          open("assets\\database.json",'w')
          download_file(service,user_id, msg_id,attID, part)
          break
        raw_data=file_database.read()
        data= raw_data.split("\n")
        data.remove('')
        for file_meta in data:
          file_meta= file_meta.replace("'","\"")
          file_meta=dict(json.loads(file_meta))
        for file_meta in data:
          file_meta= file_meta.replace("'","\"")
          file_meta=dict(json.loads(file_meta))
          if part['filename'] == file_meta['name']:
            find=True
            break
        if find:
          find=False
          break
        download_file(service, user_id, msg_id,attID, part)
  except errors.HttpError:
    print ('An error occurred: %s' % error)
def download_file(service, user_id, msg_id ,attID, part, deleted= False):
  if int(part['body']['size']) < MAXSIZE*1024*1024:
    file_data = service.users().messages().attachments().get(userId=user_id, messageId=msg_id ,id=attID).execute()
    doc_file=base64.urlsafe_b64decode(file_data['data'].encode('UTF-8'))
    path = PATH + part['filename']
    f = open(path, 'wb')
    f.write(doc_file)
    f.close()
    if NOTIFICATIONS:
      plyer.notification.notify( message='в '+PATH+part['filename'],
        app_name='gmail downloader',
        app_icon='assets\\logo.ico',
        title='скачан новый файл' )
    if not deleted:
      update_database(part['filename'],part['body']['size'], msg_id, attID, PATH+part['filename'])
  else: 
    print('file size > max file size, you can change it in '+ os.path.abspath('assets\\database.json'))

def update_database(filename, fsize, msg_id,  attID, trace):
  file_database=open('assets\\database.json','r' )
  raw_data=file_database.read()
  file_database.close()
  data= raw_data.split("\n")
  if '' in data:
    data.remove('')
  if len(data)!=0:
    for file_meta in data:
      file_meta =file_meta.replace("'","\"")
      file_meta=json.loads(file_meta)
      if file_meta['path'] != PATH + file_meta['name']:
        data=[]
        break
  data.append({'name':filename, 'size':fsize,'msgid':msg_id, 'id':attID, 'path':trace})
  file_database.close()
  file_database= open('assets\\database.json','w')
  for file_meta in data:
    file_database.write(str(file_meta)+'\n')


def check_downloads(service):
  file_database=open('assets\\database.json','r' )
  raw_data=file_database.read()
  data= raw_data.split("\n")
  if '' in data:
    data.remove('')
  if len(data)!=0:
    for file_meta in data:
      file_meta =file_meta.replace("'","\"")
      file_meta=json.loads(file_meta)
      try:
        open(file_meta['path'],'r')
      except:
        message = service.users().messages().get(userId='me', id=file_meta['msgid']).execute()
        for part in message['payload']['parts']:
          if part['filename']==file_meta['name']:
            download_file(service,'me', file_meta['msgid'],file_meta['id'],part, True)

def main():
    creds = None
    if os.path.exists('assets\\token.pickle'):
        with open('assets\\token.pickle', 'rb') as token:
            creds = pickle.load(token)
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file('assets\\credentials.json', SCOPES)
            creds = flow.run_local_server()
        with open('assets\\token.pickle', 'wb') as token:
            pickle.dump(creds, token)

    service = build('gmail', 'v1', credentials=creds)
    return service