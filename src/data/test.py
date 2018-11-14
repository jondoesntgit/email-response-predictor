import pandas as pd
import sqlite3
from collections import Counter
from sklearn.linear_model import LinearRegression, Ridge, Lasso,SGDClassifier,SGDRegressor
from sklearn.neural_network import MLPClassifier,MLPRegressor
from sklearn.svm import SVC,SVR
from sklearn.tree import DecisionTreeClassifier
from sklearn.ensemble import RandomForestClassifier, AdaBoostClassifier
from sklearn.neighbors import KNeighborsClassifier
from sklearn.metrics import classification_report, fbeta_score
import numpy as np
from textblob import TextBlob

conn = sqlite3.connect("../../data/raw/data_with_fw.sqlite3")
df = pd.read_sql_query("SELECT * FROM emails WHERE folder='received'", conn)
print("Percentage w/ replies", len(df.query('did_reply==1')) / len(df))
print("Percentage w/ Fwd: in subject", len(df.query('fw_in_subject==1')) / len(df))
print("Percentage w/ Re: in subject", len(df.query('re_in_subject==1')) / len(df))
print("Percentage w/ Many recipients", len(df.query('multiple_recipients==1')) / len(df))
train_slice = slice(0, 100)
test_slice = slice(100, 200)

favorites = list(Counter(df.iloc[train_slice].query('did_reply == 1')['sender'].values).keys())
#re_includes_subject = list(Counter(df.iloc[train_slice].query('re_in_subject == 1')['subject'].values).keys())
#recipients = list(Counter(df.iloc[train_slice].query('multiple_recipients == 1')['multiple_recipients'].values).keys())
len(favorites)

def favoritesExtractor(row):
    favorites_vector = [favorite in row['sender'] for favorite in favorites]
    return favorites_vector

def recipientsExtractor(row):
    feature_vector = [row['multiple_recipients'] == 1]
    return feature_vector

def reExtractor(row):
    re_vector = [row['re_in_subject'] == 1]
    return  re_vector

def fwdExtractor(row):
    fw_vector = [row['fw_in_subject'] == 1]
    return fw_vector

def sentimentExtractor(row):
    sentiment = [TextBlob(row['body']).sentiment[0]]
    polarity = [TextBlob(row['body']).sentiment[1]]
    return sentiment + polarity

def label(row):
    return row['did_reply']

print("Sender only features")
print("------------------------------------------------------------------------------------")
#X = np.array([favoritesExtractor(row) + recipientsExtractor(row) + reExtractor(row) + fwdExtractor(row) +  sentimentExtractor(row) for idx, row in df.iterrows()]) #favoritesExtractor(row)+ recipientsExtractor(row) + reExtractor(row) + fwdExtractor(row) + sentimentExtractor(row)
X = np.array([favoritesExtractor(row)
              + recipientsExtractor(row)
              + reExtractor(row)
              + fwdExtractor(row)
              + sentimentExtractor(row)
              for idx, row in df.iterrows()])
y_true = np.array([label(row) for idx, row in df.iterrows()])
print(len(X[test_slice]))
print(len(y_true[test_slice]))
print("Linear Regressor")
model = LinearRegression()
model.fit(X[train_slice], y_true[train_slice])
y_pred = model.predict(X[test_slice]) > .5
print(classification_report(y_true[test_slice], y_pred, target_names=["no reply", "reply"]))
print('f_2 = %s' % fbeta_score(y_true[test_slice], y_pred, 2, labels=['no reply', 'reply'], pos_label=1))

print("SGDClassifier")
model = SGDClassifier()
model.fit(X[train_slice], y_true[train_slice])
y_pred = model.predict(X[test_slice]) > .5
print(classification_report(y_true[test_slice], y_pred, target_names=["no reply", "reply"]))
print('f_2 = %s' % fbeta_score(y_true[test_slice], y_pred, 2, labels=['no reply', 'reply'], pos_label=1))

'''
print("DecisionTreeClassifier")
model = DecisionTreeClassifier()
model.fit(X[train_slice], y_true[train_slice])
y_pred = model.predict(X[test_slice]) > .5
#print(classification_report(y_true[test_slice], y_pred, target_names=["no reply", "reply"]))
print('f_2 = %s' % fbeta_score(y_true[test_slice], y_pred, 2, labels=['no reply', 'reply'], pos_label=1))


print("MLPClassifier")
model = MLPClassifier(hidden_layer_sizes=(100,100,100))
model.fit(X[train_slice], y_true[train_slice])
y_pred = model.predict(X[test_slice]) > .5
print(classification_report(y_true[test_slice], y_pred, target_names=["no reply", "reply"]))
print('f_2 = %s' % fbeta_score(y_true[test_slice], y_pred, 2, labels=['no reply', 'reply'], pos_label=1))

print("SGDClassifier")
model = SGDClassifier()
model.fit(X[train_slice], y_true[train_slice])
y_pred = model.predict(X[test_slice]) > .5
print(classification_report(y_true[test_slice], y_pred, target_names=["no reply", "reply"]))
print('f_2 = %s' % fbeta_score(y_true[test_slice], y_pred, 2, labels=['no reply', 'reply'], pos_label=1))

print("RandomForestClassifier")
model = RandomForestClassifier()
model.fit(X[train_slice], y_true[train_slice])
y_pred = model.predict(X[test_slice]) > .5
print(classification_report(y_true[test_slice], y_pred, target_names=["no reply", "reply"]))
print('f_2 = %s' % fbeta_score(y_true[test_slice], y_pred, 2, labels=['no reply', 'reply'], pos_label=1))

print("Ridge")
model = Ridge()
model.fit(X[train_slice], y_true[train_slice])
y_pred = model.predict(X[test_slice]) > .5
print(classification_report(y_true[test_slice], y_pred, target_names=["no reply", "reply"]))
print('f_2 = %s' % fbeta_score(y_true[test_slice], y_pred, 2, labels=['no reply', 'reply'], pos_label=1))
'''