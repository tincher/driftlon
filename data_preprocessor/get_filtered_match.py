import random
import pymongo
import json
import collections

# todo: maybe in different files


def flatten(d, sep="_"):
    # todo in extra file als utility?
    obj = collections.OrderedDict()

    def recurse(t, parent_key=""):
        if isinstance(t, list):
            for i in range(len(t)):
                recurse(t[i], parent_key + sep + str(i) if parent_key else str(i))
        elif isinstance(t, dict):
            for k, v in t.items():
                recurse(v, parent_key + sep + k if parent_key else k)
        else:
            obj[parent_key] = t
    recurse(d)
    return obj


def get_connection_for_collection_name(collection_name):
    # todo duplicate!
    db = pymongo.MongoClient('mongodb://localhost:27017')
    return db, db['driftlon'][collection_name]


def get_random_matches_batch(batch_size):
    db, collection = get_connection_for_collection_name('matches')
    matches = list(collection.find({}))
    random.shuffle(matches)
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
print(get_transformed_match(match))
