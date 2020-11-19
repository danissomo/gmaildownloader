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
NOTIFICATIONS=False
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
    
    message = service.users().messages().get(userId=user_id, id=msg_id).execute()
    if message['payload'].get('parts'):
      for part in message['payload']['parts']:
        if 'attachmentId'in part['body']:
          attID = part['body']['attachmentId']
          try:
            file_database=open( 'database.json','r' )
          except:
            file_database= open("database.json",'w')
            file_database.write('{}')
            file_database.close()
            download_file(service,user_id, msg_id,attID, part, store_dir)
            break
          data=json.load(open("database.json",'r'))
          find=False
          for file_meta in data.values():
            if part['filename'] ==file_meta['name']:
              find=True
              break
          if find:
            find=False
            break
          download_file(service, user_id, msg_id,attID, part, store_dir)
          print('Downloaded %s' %part['filename'] )
  except errors.HttpError:
    print ('An error occurred: %s' % error)


def download_file(service, user_id, msg_id ,attID, part, store_dir, deleted= False):
  if int(part['body']['size']) < MAXSIZE*1024*1024:
    file_data = service.users().messages().attachments().get(userId=user_id, messageId=msg_id ,id=attID).execute()
    doc_file=base64.urlsafe_b64decode(file_data['data'].encode('UTF-8'))
    path =store_dir+"\\"+part['filename']
    f = open(path, 'wb')
    f.write(doc_file)
    f.close()
    if NOTIFICATIONS:
      plyer.notification.notify( message='в '+ part['filename'],
        app_name='gmail downloader',
        app_icon='assets\\logo.ico',
        title='скачан новый файл' )
    if not deleted:
      update_database(part['filename'],part['body']['size'], msg_id, attID, store_dir+"\\" + part['filename'])
  else: 
    print('file size > max file size, you can change it in '+ os.path.abspath('database.json'))


def update_database(filename, fsize, msg_id,  attID, trace):

  file_database= open('database.json','r' )
  data=json.load(file_database)
  data[len(data)]={'name':filename, 'size':fsize,'msgid':msg_id, 'id':attID, 'path':trace}
  file_database.close()
  file_database= open('database.json','w')
  json.dump(data, file_database)
  file_database.close()


def check_downloads(service):
  file_database=open('database.json','r' )
  data=json.load(file_database)
  if len(data)!=0:
    for file_meta in data:
      try:
        open(data[file_meta]['path'],'r')
      except:
        message = service.users().messages().get(userId='me', id=file_meta['msgid']).execute()
        for part in message['payload']['parts']:
          if part['filename']==data[file_meta]['name']:
            download_file(service,'me', file_meta['msgid'],file_meta['id'],part, True)


def main():
    creds = None
   
    if os.path.exists('token.pickle'):
        with open('token.pickle', 'rb') as token:
            creds = pickle.load(token)
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file('assets\\credentials.json', SCOPES)
            creds = flow.run_local_server()
        with open('token.pickle', 'wb') as token:
            pickle.dump(creds, token)

    service = build('gmail', 'v1', credentials=creds)
    return service