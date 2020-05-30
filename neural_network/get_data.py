import sys

sys.path.append('.')
sys.path.append('/Users/joelewig/projects/driftlon')

import pymongo
import random
import numpy as np
from driftlon_utils import *
import tensorflow as tf
from datetime import datetime, timedelta



def get_player_ids_in_timespan(batch_size, timespan):
    db, collection = get_connection_for_collection_name('processed_matches')
    timestamp_for_span = int((datetime.utcnow() - timespan).timestamp())
    players = list(collection.find({'timestamp': {'$gt': timestamp_for_span}}).distinct('player_id'))
    db.close()
    return players[:batch_size]

def get_matches_batch(player_ids, batch_size=1, timespan=timedelta(weeks=2)):
    db, collection = get_connection_for_collection_name('processed_matches')
    timestamp_for_span = int((datetime.utcnow() - timespan).timestamp())
    result = []
    for player_id in player_ids:
        db_result = collection.find({'timestamp': {'$gt': timestamp_for_span}, 'player_id': player_id})
        result.append(list(db_result))
    db.close()
    random.shuffle(result)
    return result[:batch_size]

def get_batch(batch_size, timespan=timedelta(weeks=2)):
    players = get_player_ids_in_timespan(batch_size, timespan)
    player_ids = get_player_ids_in_timespan(batch_size, timespan)
    db_result = get_matches_batch(player_ids, batch_size, timespan)
    data, target = [], []
    for i in range(len(db_result)):
        data.append([match['data'] for match in db_result[i]])
        target.append(db_result[i][0]['target'])
    #todo make proper matrix
    return data, target

def get_data_batch(batch_size, matches_count=50, timespan=timedelta(weeks=2)):
    data, target = get_batch(batch_size)
    for index in range(len(data)):
        data[index] = data[index][-matches_count:]
        if len(data[index]) < matches_count:
            data[index].extend([[0] * 35 for _ in range(matches_count - len(data[index]))])
    return data, target


if __name__ == '__main__':
    batch_size = 10
    timespan = timedelta(weeks=2)
    data, target = get_batch(batch_size, timespan)
    for match_list in data:
        for match in match_list:
            # print(len(match))
            if (len(match)!=31):
                print(match)


    # print(type(data))
    # print(type(target))
