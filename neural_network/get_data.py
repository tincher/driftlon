import sys

sys.path.append(".")
sys.path.append("/Users/joelewig/projects/driftlon")

import pymongo
import json
import random
import numpy as np
from driftlon_utils import *
import tensorflow as tf



def get_processed_matches_batch(batch_size=1):
    db, collection = get_connection_for_collection_name('processed_matches')
    matches = list(collection.find({}))
    random.shuffle(matches)
    db.close()
    return matches[:batch_size]

def get_data_batch(batch_size):
    match_batch = get_processed_matches_batch(batch_size)
    data, target = [], []
    for element in match_batch:
        data.append(np.array(element['data']))
        target.append(element['target'])
    return data, target

def get_bucketized_match(match):
    bucket_list = [0, 4, 27, 28]
    for entry in bucket_list:
        print(match)
        print(entry)
        value = tf.strings.to_hash_bucket_strong(list(str(match[entry])), 20, [0, 0]).numpy()
        match[entry] = value[0]
    return match

if __name__ == '__main__':
    batch_size = 142
    data, target = get_data_batch(batch_size)
    result, lengths = [], []
    for entry in data:
        bucket_match = get_bucketized_match(entry)
        result.append(bucket_match)
        lengths.append(len(bucket_match))
    print(lengths)
