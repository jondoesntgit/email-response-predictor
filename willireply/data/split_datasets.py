#!/usr/bin/env python3

#!/usr/bin/env python

from willireply.data import enron
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

TRAIN_RATIO = float(os.environ.get("TRAIN_RATIO"))
TEST_RATIO = float(os.environ.get("TEST_RATIO"))
VALIDATE_RATIO = float(os.environ.get("VALIDATE_RATIO"))
SPLIT_FILE = Path(os.environ.get("SPLIT_FILE")).expanduser()

if TRAIN_RATIO + TEST_RATIO + VALIDATE_RATIO != 1:
    raise ValueError(
        'TRAIN_RATIO, TEST_RATIO, and VALIDATE_RATIO should add to one. '
        f'{TRAIN_RATIO} + {TEST_RATIO} + {VALIDATE_RATIO}')

users = enron.get_all_users()

#df_train = enron.get_dataframe('skilling-j', received_only=True)

random.seed(42)

df_train = pd.DataFrame()
df_validate = pd.DataFrame()
df_test = pd.DataFrame()

subsets = {}

for user in tqdm(users):
    df = enron.get_dataframe(user, received_only=True)
    email_indices = list(df.index)
    random.shuffle(email_indices)

    break1 = int(len(df) * TRAIN_RATIO)
    break2 = int(len(df) * (VALIDATE_RATIO + TRAIN_RATIO))

    subsets[user] = {
        "train": email_indices[:break1],
        "validate": email_indices[break1:break2],
        "test": email_indices[break2:]
    }

    #partial_df_train    = df.loc[email_indices[:break1]]
    #partial_df_validate = df.loc[email_indices[break1:break2]]
    partial_df_test     = df.loc[email_indices[break2:]]

    df_validate = df_validate.append(partial_df_validate)

with open(SPLIT_FILE, 'w') as f:
    json.dump(subsets, f)

split_file_directory = SPLIT_FILE.parent

#df_train.to_pickle(split_file_directory / 'training_set.pkl')
#df_validate.to_pickle(split_file_directory / 'validation_set.pkl')
df_test.to_pickle(split_file_directory / 'test_set.pkl')
