#!/usr/bin/env python3

import numpy as np
from dotenv import find_dotenv, load_dotenv

from willireply.features import features
from willireply.features.feature_extractor import FeatureExtractor


if __name__ == '__main__':
    dotenv_path = find_dotenv()
    load_dotenv(dotenv_path)

    my_common_words = ['ASAP', 'please', 'could you']

    subject_common_words_feature = lambda df: np.log(1 + features.common_words_subject(df, ['?' '!']))
    body_common_words_feature = lambda df: np.log(1+ features.common_words_body(df, ['?', '!']))
    body_length_feature = lambda df: np.log(1 + features.words_in_body(df))

    basic_fe = FeatureExtractor(
      subject_common_words_feature,
      body_common_words_feature,
      features.thread_length,
      features.words_in_subject,
      features.number_of_recipients,
      features.number_of_ccs,
      features.was_replied,
      features.was_forwarded,
      name="basic")
    basic_fe.to_pickle()