#!/usr/bin/env python3

#!/usr/bin/env python

from willireply.data import enron
from willireply.features.feature_extractor import FeatureExtractor
from willireply.features import features
import numpy as np
from dotenv import find_dotenv, load_dotenv
import os
import random
from pathlib import Path
import pandas as pd
from tqdm import tqdm
import json

# find .env automagically by walking up directories until it's found
dotenv_path = find_dotenv()

# load up the entries as environment variables
load_dotenv(dotenv_path)

SPLIT_FILE = os.environ.get('SPLIT_FILE')
SPLIT_FILE = Path(SPLIT_FILE).expanduser()

PROCESSED_DATA_DIRECTORY = Path(os.environ.get('PROCESSED_DATA_DIRECTORY')).expanduser()

df_train = pd.DataFrame()
df_validate = pd.DataFrame()
df_test = pd.DataFrame()

with open(SPLIT_FILE, 'r') as f:
    data_subsets =  json.load(f)

for user, splits in tqdm(data_subsets.items()):
    df = enron.get_dataframe(user, received_only=True)
    email_indices = list(df.index)
    random.shuffle(email_indices)

    partial_df_train    = df.loc[splits['train']]
    partial_df_validate = df.loc[splits['validate']]
    #partial_df_test     = df.loc[splits['test']]

    df_train = df_train.append(partial_df_train)
    df_validate = df_validate.append(partial_df_validate)
    #df_test = df_test.append(partial_df_test)

def save(path, object):
    path = Path(path).with_suffix('.npy')
    with path.open('wb') as f:
        np.save(f, object)

for file in tqdm(list(Path('.').glob('*.pkl'))):
    destination = PROCESSED_DATA_DIRECTORY / file.stem
    destination.mkdir(parents=True, exist_ok=True)

    feature_extractor = FeatureExtractor.from_pickle(file)

    x_train = feature_extractor.extract(df_train)
    x_validate = feature_extractor.extract(df_validate)
    x_test = feature_extractor.extract(df_test)

    y_train = feature_extractor.get_labels(df_train)
    y_validate = feature_extractor.get_labels(df_validate)
    y_test = feature_extractor.get_labels(df_test)

    save(destination / 'x_train', x_train)
    save(destination / 'x_validate', x_validate)
    save(destination / 'x_test', x_test)
    save(destination / 'y_train', y_train)
    save(destination / 'y_validate', y_validate)
    save(destination / 'y_test', y_test)