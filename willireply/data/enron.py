#!/usr/bin/env python3
"""Creates an sqlite3 database of the enron dataset and tags the email response

.. moduleauthor:: Jonathan Wheeler

"""

import os
import email
import imaplib
from dotenv import load_dotenv, find_dotenv
from pathlib import Path
import pandas as pd
import numpy as np
import re
import sqlite3
from tqdm.autonotebook import tqdm # progress bars

# find .env automagically by walking up directories until it's found
dotenv_path = find_dotenv()

# load up the entries as environment variables
load_dotenv(dotenv_path)

ENRON_FOLDER = Path(os.environ.get("ENRON_FOLDER")).expanduser()
ENRON_INDEX = Path(os.environ.get("ENRON_INDEX")).expanduser()

def index():
    conn = sqlite3.connect(str(ENRON_INDEX))
    c = conn.cursor()
    c.execute('''DROP TABLE IF EXISTS emails;''')

    # to and from are reserved keywords. Add a m_ before so we can work with the variables
    c.execute('''CREATE TABLE emails
        (id INTEGER PRIMARY KEY AUTOINCREMENT,
        user TEXT,
        folder TEXT,
        filename TEXT,
        message_id TEXT,
        date INT,
        m_from TEXT,
        m_to TEXT,
        subject TEXT,
        body TEXT,
        did_reply INT,
        reply_id INTEGER
        );''')

    import datetime
    from dateutil import parser

    users = list(f.stem for f in ENRON_FOLDER.iterdir())

    user_bar = tqdm(users, desc='users', leave=False)
    for user in user_bar:
        user_bar.set_description("{:<15}".format(user))
        folders = [f.stem for f in (ENRON_FOLDER/user).iterdir() if f.is_dir()]
        folder_bar = tqdm(folders, leave=False, desc='folders')
        for folder in folder_bar:
        #    folder_bar.set_description("{:<15}".format(folder))
            for email_file in (ENRON_FOLDER/user/folder).glob('*'):
                assert email_file.exists()
                if not email_file.is_file():
                    print(email_file, "is not a file")
                    continue
                with open(email_file) as f:
                    try:
                        m = email.message_from_file(f)
                    except:
                        print('Couldnt open %s' % f)
                        continue
                body = None
                for part in m.walk():
                    body = part.get_payload()
                    break
                if body is None:
                    continue
                data = {
                    "user": user,
                    "folder": folder,
                    "filename": str(email_file),
                    "message_id": m['Message-ID'],
                    "date": int(parser.parse(m['Date']).timestamp()),
                    "m_from": m['From'],
                    "m_to": m['To'],
                    "subject": m['Subject'],
                    "body": body
                }
                c.execute(f'INSERT INTO emails({",".join(data.keys())})'
                          f'VALUES ({",".join("?"*len(data))});',
                          tuple(data.values()))
    conn.commit()

def label():
    conn = sqlite3.connect(str(ENRON_INDEX))
    c = conn.cursor()
    users = [res[0] for res in c.execute('SELECT DISTINCT user FROM emails')]
    user_bar = tqdm(users, leave=False)
    for user in user_bar:
        user_bar.set_description('{:<15}'.format(user))
        emails_df = pd.read_sql_query(f'select * from emails where user="{user}";', conn)
        sent_folders = [f for f in  np.unique(emails_df.folder.values) if ('sent' in f.lower())]
        received_emails = emails_df.query(f'folder not in {sent_folders}')
        sent_emails = emails_df.query(f'folder in {sent_folders}')

        emails_with_responses = []
        emails_bar = tqdm(list(received_emails.iterrows()), leave=False, desc='emails')
        for received_idx, email in emails_bar:
            date = email['date']
            subject = email['subject']
            body = email['body']
            search_filter = f'date > {date}' # && subject in subject'
            search_df = sent_emails.query(search_filter)
            search_df = search_df[search_df['subject'].str.contains(re.escape(subject))]
            if len(search_df) == 0:
                continue
            search_df = search_df[search_df['body'].str.contains(re.escape(body))]
            if len(search_df) == 0:
                continue
            reply_id = float(search_df.iloc[0]['id'])
            this_id = email['id']
            c.execute(f'UPDATE emails SET did_reply=1, reply_id= ? WHERE id=?;', (reply_id, this_id,))
            conn.commit()

if __name__ == "__main__":
#    index()
    label()
