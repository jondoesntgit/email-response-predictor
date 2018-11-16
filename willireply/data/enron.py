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
import datetime
from dateutil import parser
from tqdm.autonotebook import tqdm # progress bars
import logging


# find .env automagically by walking up directories until it's found
dotenv_path = find_dotenv()

# load up the entries as environment variables
load_dotenv(dotenv_path)

ENRON_FOLDER = Path(os.environ.get("ENRON_FOLDER")).expanduser()
ENRON_INDEX_FOLDER = Path(os.environ.get("ENRON_INDEX_FOLDER")).expanduser()
ENRON_LOG = Path(os.environ.get("ENRON_LOG")).expanduser()
logging.basicConfig(filename=str(ENRON_LOG), filemode='w', level=logging.DEBUG)

def get_connection(user):
    filename = ENRON_INDEX_FOLDER / (user + '.sqlite3')
    if not filename.is_file():
        raise ValueError(user, 'is not in index folder')
    return sqlite3.connect(str(filename))

def get_dataframe(user, received_only=False):
    conn = get_connection(user)
    df = pd.read_sql_query('select * from emails;', conn, index_col='id')
    df['thread'] = df['body'][:]
    df['body'] = df['body'].apply(lambda x: re.split(r'-----Original Message-----|on\s[0-1][0-9]/[0-3][0-9]/[0-9]{2,4}', x)[0])

    # Caste the columns into the correct types
    type_dict = {
        str: ['user', 'folder', 'filename', 'm_from', 'm_to', 'm_cc', 'subject', 'body'],
        bool: ['did_reply'],
    }
    for key, columns in type_dict.items():
        df[columns] = df[columns].astype(key)
    df['date'] = pd.to_datetime(df.date * 1e9)

    if not received_only:
        return df
    # Filter out any row where folder contains the word 'sent'
    return df[~df.folder.str.contains('sent', flags=re.IGNORECASE)]

def index_folder(user, folder, cursor):
    for email_file in (ENRON_FOLDER/user/folder).glob('*'):
        assert email_file.exists()
        if email_file.is_dir():
            # Recurse to look for more emails
            index_folder(user, str(folder) + '/' + str(email_file), cursor)
            continue
        with open(email_file) as f:
            try:
                m = email.message_from_file(f)
            except:
                logging.info('Couldnt open %s' % f)
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
            "m_cc": m['cc'],
            "subject": m['Subject'],
            "body": body
        }
        cursor.execute(f'INSERT INTO emails({",".join(data.keys())})'
                  f'VALUES ({",".join("?"*len(data))});',
                  tuple(data.values()))

def make_empty_index(filename):
    conn = sqlite3.connect(str(ENRON_INDEX_FOLDER/filename))
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
        m_cc TEXT,
        subject TEXT,
        body TEXT,
        did_reply INT,
        reply_id INTEGER
        );''')
    return conn

def index(*users):
    """
    Creates indicies for the users specified.

    If none, all users will be indexed
    If a list, only the users in the list will be indexed
    If a string, only that user will be indexed
    Otherwise, raise a value error
    """
    if not users:
        users = list(f.stem for f in ENRON_FOLDER.iterdir())

    if len(users) > 1:
        # if we will fail, fail early
        for user in users:
            if not (ENRON_FOLDER / user).is_dir():
                raise ValueError(user, 'is not in corpus')

        user_bar = tqdm(users, desc='users', leave=False)
        for user in user_bar:
            user_bar.set_description("{:<15}".format(user))
            index(user)
        user_bar.close()

    elif len(users) == 1:
        user = users[0]
        if not (ENRON_FOLDER / user).is_dir():
            raise ValueError(user, 'is not in corpus')
        filename = user + '.sqlite3'
        conn = make_empty_index(filename)
        c = conn.cursor()

        folders = [f.stem for f in (ENRON_FOLDER/user).iterdir() if f.is_dir()]
        folder_bar = tqdm(folders, leave=False, desc='folders')
        for folder in folder_bar:
            index_folder(user=user, folder=folder, cursor=c)
        folder_bar.close()
        conn.commit()

    else:        
        assert False, 'length of args should be positive. Perhaps ENRON_FOLDER is empty'

def label(*users):
    """Labels the datasets.

    if users is none, it labels everything in ENRON_INDEX_FOLDER

    if it's a specific user, then it labels that specific user's index
    """

    if not users:
        users = list(f.stem for f in ENRON_INDEX_FOLDER.iterdir())

    if len(users) > 1:
        # if we will fail, fail early
        for user in users:
            if not (ENRON_INDEX_FOLDER / (user + '.sqlite3')).is_file():
                raise ValueError(user, 'is not in index folder')

        user_bar = tqdm(users, desc='users', leave=False)
        for user in user_bar:
            user_bar.set_description("{:<15}".format(user))
            label(user)
        user_bar.close()

    elif len(users) == 1:
        user = users[0]
        conn = get_connection(user)
        c = conn.cursor()

        emails_df = pd.read_sql_query(f'select * from emails where user="{user}";', conn)
        sent_folders = [f for f in  np.unique(emails_df.folder.values) if ('sent' in f.lower())]
        received_emails = emails_df.query(f'folder not in {sent_folders}')
        sent_emails = emails_df.query(f'folder in {sent_folders}')

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
        emails_bar.close()
        c.execute(f'UPDATE emails SET did_reply=0 WHERE did_reply IS NULL;')
        conn.commit()
    else:
        assert False, 'length of args should be positive. Perhaps ENRON_FOLDER is empty'

def is_labeled(user):
    c = get_connection(user).cursor()
    to_be_labeled = c.execute('select count(*) from emails where did_reply IS NULL LIMIT 1;').fetchone()[0]
    return to_be_labeled == 0

def delete_indices():
    for f in ENRON_INDEX_FOLDER.iterdir():
        f.unlink()



if __name__ == "__main__":
    index()
    label()
