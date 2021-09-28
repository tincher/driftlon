import re
import numpy as np
from driftlon_utils import *
from data_fetcher.get_from_db import *
from sklearn.base import BaseEstimator, TransformerMixin


def transform_data_to_np(data):
    values = list(data.values())[1:]
    keys = list(data.keys())[1:]
    return values, keys

def get_data_for_keys(common_keys, X):
    values_list = []
    for key in common_keys:
        values = [element[key] for element in X]
        values_list.append(values)
    return values_list


def get_common_keys(X):
    keys = []
    for element in X:
        keys.extend(element.keys())

    keys = list(set(keys))
    result_keys = sorted(list(filter(lambda x: all(x in element.keys() for element in X), keys)))
    return result_keys


def get_all_keys(X):
    keys = []
    for element in X:
        keys.extend(element.keys())

    keys = list(set(keys))
    result_keys = sorted(list(filter(lambda x: any(x in element.keys() for element in X), keys)))
    return result_keys
