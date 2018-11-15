'''
Stuffed full of yummy features
'''

import re
import pandas as pd

def was_forwarded(df):
    """Looks to see if something like fw or fwd is in the subject.
    Uses regular expressions
    """

    return df['subject'].str.contains('fwd?\:?\s', flags=re.IGNORECASE).values

def was_replied(df):
    """Looks to see if something like Re or RE: is in the subject. Uses regular expressions
    """
    return df['subject'].str.contains('re?\:?\s', flags=re.IGNORECASE).values

def number_of_recipients(df):
    """Counts the number of recipients"""
    return df['m_to'].apply(lambda x: len(x.split(','))).values

def common_words(df, words):
    """Given a list of common words (length N), returns an MxN matrix (M is length of df)
    Each cell is the number of times word[N] occurs in df[M].body (case insensitive"""
    return df[['body']].apply(lambda x: pd.Series([x['body'].lower().count(word.lower()) for word in words]), axis=1).values


def number_of_recipients(df):
    """Counts the number of recipients"""
    return df['m_to'].apply(lambda x: len(x.split(','))).values
