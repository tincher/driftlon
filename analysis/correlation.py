import scipy.stats
from driftlon_utils import *
import numpy as np
import math
import pandas as pd
from data_fetcher.get_from_db import *
import pickle
import argparse

def get_pearson_rs(X, Y, common_keys):
    pearsonrs = []
    values_list = []
    for key in common_keys:
        values = [element[key] for element in X]
        values_list.append(values)
        if type(values[0]) is int or type(values[0]) is float:
            result = (scipy.stats.pearsonr(values, Y), key)
            if not math.isnan(result[0][0]):
                pearsonrs.append(result)
    return pearsonrs, values_list

def remove_outliers(df, column_name):
    low = np.quantile(df[column_name], 0.05)
    high = np.quantile(df[column_name], 0.95)
    return df[df[column_name].between(low, high, inclusive=True)]

def main(load_from_file=True):
    if load_from_file:
        X, Y = get_data()

        pickle.dump(X, open('X.pkl', 'wb+'))
        pickle.dump(Y, open('Y.pkl', 'wb+'))
    else:
        X = pickle.load(open('X.pkl', 'rb+'))
        Y = pickle.load(open('Y.pkl', 'rb+'))

    common_keys = get_common_keys(X)
    pearsonrs, values = get_pearson_rs(X, Y, common_keys)

    result = sorted(pearsonrs, key=lambda elem: elem[0][0])
    result_pd = pd.DataFrame(result)

    pdb.set_trace()
    # print(pd.DataFrame(zip(X,Y)).describe())

    # print(result_pd.to_string())

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Analyze dataset')
    parser.add_argument('--load_from_file', action='store_false')

    args = parser.parse_args()

    main(args.load_from_file)
