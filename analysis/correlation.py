import scipy.stats
from driftlon_utils import *
import numpy as np
import math
import pandas as pd
from data_fetcher.get_from_db import *
import pickle
import argparse

DBReader = DBReader(ip='85.214.100.20')

def get_particpant_id(match):
    participant_id = 0
    player = DBReader.get_player_for_id(match['player_id'])
    player_account_ids = []
    player_account_ids = [x['account_id']['accountId'] for x in player['soloq_ids'] if x['account_id'] is not None]
    for participant in match['data']['participantIdentities']:
        if participant['player']['accountId'] in player_account_ids:
            participant_id = participant['participantId']
    return participant_id

def filter_and_flatten_match(match):
    participant_id = get_particpant_id(match)
    participant_data = match['data']['participants'][participant_id-1]
    flattened_match = flatten_dict(participant_data)
    return flattened_match

def get_raw_data_batch(limit, offset=0, ip='localhost'):
    db, matches_collection = get_connection_for_collection_name('matches', ip)

    matches = list(matches_collection.find(projection=['pro_games_count', 'data', 'player_id'], limit=limit, skip=offset))

    data = [filter_and_flatten_match(element) for element in matches]

    target = [element['pro_games_count'] for element in matches]

    db.close()
    return data, target

def get_data(batch_size=10000, ip='localhost'):
    offset = 0
    data, target = [], []

    new_data, new_target = get_raw_data_batch(batch_size, offset, ip)

    while len(new_target) > 0:
        data.extend(new_data)
        target.extend(new_target)

        offset += batch_size
        new_data, new_target = get_raw_data_batch(batch_size, offset, ip)


        print(len(target))
    return data, target

def get_common_keys(X):
    keys = []
    for element in X:
        keys.extend(element.keys())

    keys = list(set(keys))
    result_keys = sorted(list(filter(lambda x: all(x in element.keys() for element in X), keys)))
    return result_keys


def get_data_for_keys(common_keys, X):
    data = []
    for key in common_keys:
        values = [element[key] for element in X]
        data.append(values)
    return data

def get_pearson_rs(X, Y, common_keys):
    pearsonrs = []
    for key in common_keys:
        values = [element[key] for element in X]
        if type(values[0]) is int or type(values[0]) is float:
            result = (scipy.stats.pearsonr(values, Y), key)
            if not math.isnan(result[0][0]):
                pearsonrs.append(result)
    return pearsonrs

def remove_outliers(df, column_name):
    low = np.quantile(df[column_name], 0.05)
    high = np.quantile(df[column_name], 0.95)
    return df[df[column_name].between(low, high, inclusive=True)]

def main(load_from_file=False, ip='localhost'):
    if load_from_file:
        X, Y = get_data(ip=ip)

        pickle.dump(X, open('X.pkl', 'wb+'))
        pickle.dump(Y, open('Y.pkl', 'wb+'))
        print('data written')
    else:
        X = pickle.load(open('X.pkl', 'rb+'))
        Y = pickle.load(open('Y.pkl', 'rb+'))
        print('data loaded')

    common_keys = get_common_keys(X)
    data = pd.DataFrame(get_data_for_keys(common_keys, X))
    data.describe()


    # pearsonrs = get_pearson_rs(X, Y, common_keys)
    #
    # result = sorted(pearsonrs, key=lambda elem: elem[0][0])
    # result_pd = pd.DataFrame(result)
    #
    # print(result_pd.to_string())

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Analyze dataset')
    parser.add_argument('--load_from_file', action='store_false')
    parser.add_argument('--ip', default='localhost')

    args = parser.parse_args()
    print(args)

    main(args.load_from_file, ip=args.ip)
