#!/usr/bin/env python
# Abstract base classes
import abc
import random
import numpy as np

from pathlib import Path

from willireply.features import features
from willireply.features.feature_extractor import FeatureExtractor

from sklearn.linear_model import LinearRegression
from sklearn.linear_model import SGDClassifier

from sklearn.metrics import classification_report, fbeta_score

from dotenv import find_dotenv, load_dotenv
load_dotenv(find_dotenv())
import os
from jinja2 import Template
from tqdm import tqdm
import pandas as pd
from willireply.data import enron
import dill

RESULTS_DIRECTORY = Path(os.environ.get('RESULTS_DIRECTORY')).expanduser()
SPLIT_FILE = os.environ.get('SPLIT_FILE')
SPLIT_FILE = Path(SPLIT_FILE).expanduser()

df_test = pd.read_pickle(SPLIT_FILE.parent / 'test_set.pkl')

class BaseModel(abc.ABC):

    def __init__(self):
        pass

    @abc.abstractmethod
    def train(self, train_x, train_y):
        pass

    @abc.abstractmethod
    def test(self, test_x, test_y):
        pass

    def test(self, test_x, test_y):
        pred_y = self.predict(test_x)
        true_positives = np.where(test_y & pred_y)[0]
        false_positives = np.where(test_y < pred_y)[0]
        true_negatives = np.where(~test_y ^ ~pred_y)[0]
        false_negatives = np.where(test_y > pred_y)[0]

        destination = RESULTS_DIRECTORY
        destination.mkdir(parents=True, exist_ok=True)

        template_file = Path(__file__).parent / 'results_template.html'
        with template_file.open('r') as f:
            template = Template(f.read())

        with (destination / self.name).with_suffix('.html').open('w') as f:
            f.write(
                template.render(
                    false_positives = df_test.iloc[false_positives],
                    false_negatives = df_test.iloc[false_negatives],
                    total = len(df_test),
                    classification = classification_report(test_y, pred_y, target_names=['no_reply', 'reply']),
                    title=self.name)
                )

    def serialize(self):
        destination = RESULTS_DIRECTORY
        destination.mkdir(parents=True, exist_ok=True)
        with (destination / self.name ).with_suffix('.pkl').open('wb') as f:
            dill.dump(self, f)



class LeastSquares(BaseModel):
    def __init__(self, name='LeastSquares'):
        self._model = LinearRegression()
        self.name = name

    def train(self, train_x, train_y):
        self._model.fit(train_x, train_y)

    def predict(self, test_x):
        return self._model.predict(test_x) > 0


class HingeLoss(BaseModel):
    def __init__(self, name='HingeLoss'):
        self._model = SGDClassifier(loss="hinge", penalty="l2", max_iter=1000)
        self.name = name

    def train(self, train_x, train_y):
        self._model.fit(train_x, train_y)

    def predict(self, test_x):
        return self._model.predict(test_x)     

if __name__ == '__main__':

    model = LeastSquares()

    fe = FeatureExtractor.from_pickle('simple')

    model.train(*fe.get_dataset('train'))
    model.test(*fe.get_dataset('test'))
    model.serialize()

#    model = HingeLoss()
#    model.train(*fe.get_dataset('train'))
#    model.visualize(*fe.get_dataset('test'))