#!/usr/bin/env python3
import os

import time
import imaplib
import email
import sqlite3
from pathlib import Path
from tqdm import tqdm

OUTPUT_DIRECTORY = Path('../../data/raw')
SQLITE3_PATH = OUTPUT_DIRECTORY / 'data.sqlite3'

WILLIREPLY_EMAIL = os.getenv('WILLIREPLY_EMAIL')
if not WILLIREPLY_EMAIL:
    WILLIREPLY_EMAIL = input('Email: ')
WILLIREPLY_PASSWORD = os.getenv('WILLIREPLY_PASSWORD')
if not WILLIREPLY_PASSWORD:
    WILLIREPLY_PASSWORD = input('Password: ')

SMTP_SERVER = "imap.gmail.com"
SMTP_PORT   = 993

EMAIL_FOLDERS = {
    #'received' : 'inbox',
    'received' : '[Gmail]/Archive',
    'sent' : '"[Gmail]/Sent Mail"'
}

def download_emails_from_gmail():
    mail = imaplib.IMAP4_SSL(SMTP_SERVER)

    mail.login(WILLIREPLY_EMAIL,WILLIREPLY_PASSWORD)

    for folder_type, folder_name in EMAIL_FOLDERS.items():

        save_to_directory = Path(OUTPUT_DIRECTORY) / folder_type
        save_to_directory.mkdir(parents=True, exist_ok=True)

        res = mail.select(folder_name)
        type_, data = mail.search(None, 'ALL')
        mail_ids = data[0]

        id_list = mail_ids.split()

        num2download = 200
        for file, i in tqdm(enumerate(id_list[-num2download:]), total=num2download, desc=folder_name):
            typ, data = mail.fetch(i, '(RFC822)' )
            for response_part in data:
                with open(f'{save_to_directory}/{file:06d}.eml', 'wb') as f:
                    f.write(data[0][1])

def index_emails():
    conn = sqlite3.connect(str(SQLITE3_PATH))
    c = conn.cursor()
    c.execute('''DROP TABLE IF EXISTS emails;''')
    c.execute('''CREATE TABLE emails
        (id INTEGER PRIMARY KEY AUTOINCREMENT, 
        filename text, 
        folder text, 
        sender text, 
        subject text, 
        body text, 
        bodytype text, 
        message_id text, 
        reply_id text, 
        did_reply bool);''')

    for folder in EMAIL_FOLDERS:
        folder_path = Path(OUTPUT_DIRECTORY) / folder
        for email_file in folder_path.glob('**/*.eml'):
            with open(email_file) as f:
                try:
                    m = email.message_from_file(f)
                except:
                    continue

            body = ''
            body_type = 'html'
            for part in m.walk():
                # each part is a either non-multipart, or another multipart message
                # that contains further parts... Message is organized like a tree
                if part.get_content_type() == 'text/plain':
                    body = part.get_payload()
                    body_type = 'plain'

            reply_id = ''
            if 'In-Reply-To' in m:
                reply_id = m['In-Reply-To']

            fields = (str(email_file.name), str(email_file.parent.name), 
                m['from'], m['subject'], body, body_type,
                m['Message-Id'], reply_id, 0)
            c.execute('''INSERT INTO emails (filename, folder, sender, subject, body, bodytype, message_id, reply_id, did_reply)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)''', fields)

    conn.commit()

def flag_emails_with_responses():
    conn = sqlite3.connect(str(SQLITE3_PATH))
    c = conn.cursor()
    c.execute('''
    UPDATE emails 
    SET did_reply = 1 
    WHERE id in (
        SELECT e_received.id 
        FROM emails as e_received 
        INNER JOIN emails as e_sent 
        WHERE e_sent.reply_id = e_received.message_id
        );
    ''')
    conn.commit()

if __name__ == "__main__":
    download_emails_from_gmail()
    index_emails()
    flag_emails_with_responses()
