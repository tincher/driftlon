from driftlon_utils import get_connection_for_collection_name, flatten
import random
import pymongo
import json
import collections


def get_random_matches_batch(batch_size):
    db, collection = get_connection_for_collection_name('matches')
    matches = list(collection.find({}))
    random.shuffle(matches)
    db.close()
    return matches[:batch_size]


def get_transformed_match(match):
    # todo filter relevant infos
    flat_match = flatten(match)
    flat_match.pop('_id')
    return flat_match


def write_to_tfrecord(matches):
    pass


match = get_random_matches_batch(1)[0]
# print(json.dumps(get_transformed_match(match)))
# print(get_transformed_match(match))
