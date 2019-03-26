
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
    try:
      config.read('assets\\settings.cfg')
      PATH= config['DEFAULT']['path']
      if not os.path.exists(PATH):
          os.makedirs(PATH)
      if config['DEFAULT']['notify']=='yes':
        NOTIFICATIONS=True
      else:
        NOTIFICATIONS=False
      MAXSIZE= int(config['DEFAULT']['max_file_size'])
      KEYWORD = config['DEFAULT']['get_msgs_from']
    except:
      print('settings.cfg deleted or corrupted')
    token = funcs.main()
    msgs=token.users().messages().list(userId='me',q='from:'+KEYWORD).execute()
    for msg in msgs['messages'] :  
        funcs.GetAttachments(token,'me',msg['id'],'')
    funcs.check_downloads(token)