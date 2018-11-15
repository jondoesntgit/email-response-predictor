import numpy as np

class FeatureExtractor():
    """A creates an object that can turn a DataFrame into a feature matrix"""

    def __init__(self, *features):
        """
        Accepts a list of features.
        Each feature takes a dataframe with M rows, and returns a matrix with M rows and N columns
        """
        self.features = features

    def extract(self, df):
        # merges all the columns together. Still has M rows
        return np.column_stack(f(df) for f in self.features)

    def get_labels(self, df):
        return df.did_reply.values
