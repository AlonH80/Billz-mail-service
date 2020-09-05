from variables import *
import pickle
import os.path
import os
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
import base64
import logging
from datetime import datetime as dt
import json

logger = None
LOGGING_LEVEL = logging.INFO
gmail_service = None


def init_service():
    init_logger()
    init_gmail_service()
    if not os.path.exists(PDFS_PATH):
        os.makedirs(PDFS_PATH)


def init_logger():
    global logger
    if logger is None:
        log_name = '{}.log'.format(dt.now().strftime("%y_%m_%d__%H_%M"))
        logger = logging.getLogger(log_name)
        logger.setLevel(LOGGING_LEVEL)
        fh = logging.FileHandler(log_name)
        ch = logging.StreamHandler()
        formatter = logging.Formatter('[%(asctime)s]  {%(filename)s} - %(levelname)s - %(message)s')
        fh.setFormatter(formatter)
        ch.setFormatter(formatter)
        ch.setLevel(LOGGING_LEVEL)
        fh.setLevel(LOGGING_LEVEL)
        logger.addHandler(fh)
        logger.addHandler(ch)
        logger.info("Logger initialized")


def init_gmail_service():
    global gmail_service
    creds = None
    if os.path.exists('token.pickle'):
        with open('token.pickle', 'rb') as token:
            creds = pickle.load(token)
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_config(json.loads(os.environ.get("gmail_credentials")), SCOPES)
            creds = flow.run_local_server(host='https://billz-mail-service.herokuapp.com/', port=80)
        # Save the credentials for the next run
        with open('token.pickle', 'wb') as token:
            pickle.dump(creds, token)
    gmail_service = build('gmail', 'v1', credentials=creds)


class MailGetter:

    def __init__(self):
        if gmail_service is None:
            init_gmail_service()
        self.msgs = []

    def get_messages(self):
        msgs_lst = gmail_service.users().messages().list(userId='me').execute()
        msgs_ids = msgs_lst.get('messages', [])
        self.msgs = list(
            map(
                lambda m_id:
                gmail_service.users().messages().get(userId="me", id=m_id["id"]).execute(),
                msgs_ids
            )
        )

    def get_files_from_msg(self, msg):
        msg_parts = msg.get("payload").get("parts")
        for part in msg_parts:
            if part['filename']:
                if 'data' in part['body']:
                    data = part['body']['data']
                else:
                    att_id = part['body']['attachmentId']
                    att = gmail_service.users().messages().attachments().get(userId="me", messageId=msg["id"], id=att_id).execute()
                    data = att['data']
                file_data = base64.urlsafe_b64decode(data.encode('UTF-8'))
                path = "{}/{}".format(PDFS_PATH, part['filename'])
                if not os.path.exists(path):
                    with open(path, 'wb') as f:
                        f.write(file_data)
                        logger.info("Download file {}".format(part['filename']))

    def get_all_files_from_msgs(self):
        if self.msgs.__len__() == 0:
            self.get_messages()
        list(map(lambda m: self.get_files_from_msg(m), self.msgs))


