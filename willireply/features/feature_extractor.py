import numpy as np
from pathlib import Path
import dill
import os

from dotenv import find_dotenv, load_dotenv
dotenv_path = find_dotenv()
load_dotenv(dotenv_path)

FEATURE_EXTRACTOR_DIRECTORY = Path(os.environ.get('FEATURE_EXTRACTOR_DIRECTORY')).expanduser()
PROCESSED_DATA_DIRECTORY = Path(os.environ.get('PROCESSED_DATA_DIRECTORY')).expanduser()

class FeatureExtractor():
    """A creates an object that can turn a DataFrame into a feature matrix"""

    def __init__(self, *features, **kwargs):
        """
        Accepts a list of features.
        Each feature takes a dataframe with M rows, and returns a matrix with M rows and N columns
        """
        if 'name' in kwargs:
            self.name = kwargs['name']
        else:
            self.name = None
        self.features = features

    @classmethod
    def from_pickle(cls, name):
        file = (FEATURE_EXTRACTOR_DIRECTORY / name).with_suffix('.pkl')
        with file.open('rb') as f:
            feature_extractor = dill.load(f)
        return feature_extractor

    def to_pickle(self):

        if not isinstance(self.name, str):
            raise ValueError('The name of this feature extractor must be set to a string')

        file = (FEATURE_EXTRACTOR_DIRECTORY / self.name).with_suffix('.pkl')
        with file.open('wb') as f:
            dill.dump(self, f)

    def extract(self, df):
        # merges all the columns together. Still has M rows
        return np.column_stack(f(df) for f in self.features)

    def get_labels(self, df):
        return df.did_reply.values

    def get_dataset(self, data_type):

        if data_type not in ['train', 'test', 'validate']:
            raise ValueError('Datatype should be either train, test, or validate')

        if self.name is None:
            raise Exception(
                'I cannot find my cached dataset because I don\'t have a name.')

        destination = PROCESSED_DATA_DIRECTORY
        x_file = (destination / self.name / f'x_{data_type}').with_suffix('.npy')
        y_file = (destination / self.name / f'y_{data_type}').with_suffix('.npy')

        with x_file.open('rb') as f:
            x = np.load(f)
        with y_file.open('rb') as f:
            y = np.load(f)

        return x, y