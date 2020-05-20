import sys

sys.path.append(".")
sys.path.append("/Users/joelewig/projects/driftlon")

import pymongo
import json
import random
import numpy as np
from driftlon_utils import *



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

if __name__ == '__main__':
    batch_size = 1
    data, target = get_data_batch(batch_size)
    print(data)
