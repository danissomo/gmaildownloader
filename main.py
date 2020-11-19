
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

import funcs

if __name__ == '__main__':
    config = configparser.ConfigParser()
    config.read('assets\\settings.cfg')
    PATH= config['DEFAULT']['path']
    KEYWORD = config['DEFAULT']['get_msgs_from']
    KEYWORD = KEYWORD.replace(" ", '')
    KEYWORD = KEYWORD.split(',')
    print(KEYWORD)
    token = funcs.main()
    for keyword in  KEYWORD:
      print(keyword)
      if not os.path.exists(PATH+ "\\" +keyword):
          os.makedirs(PATH+"\\"+keyword)
      if config['DEFAULT']['notify']=='yes':
        NOTIFICATIONS=True
      else:
        NOTIFICATIONS=False
      MAXSIZE= int(config['DEFAULT']['max_file_size'])
      msgs=token.users().messages().list(userId='me',q='from:'+keyword).execute()
      for msg in msgs['messages'] :  
          funcs.GetAttachments(token,'me',msg['id'], PATH+"\\"+keyword)
    
    funcs.check_downloads(token)