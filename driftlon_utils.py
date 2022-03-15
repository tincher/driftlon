import pymongo
import collections


def flatten_dict(d, sep='_'):
    obj = collections.OrderedDict()

    def recurse(t, parent_key=''):
        if isinstance(t, list):
            for i in range(len(t)):
                recurse(t[i],
                        parent_key + sep + str(i) if parent_key else str(i))
        elif isinstance(t, dict):
            for k, v in t.items():
                recurse(v, parent_key + sep + k if parent_key else k)
        else:
            obj[parent_key] = t

    recurse(d)
    return dict(obj)


def get_connection_for_collection_name(collection_name,
                                       ip='localhost',
                                       username=None,
                                       password=None):
    db = pymongo.MongoClient(f'mongodb://{ip}:27017',
                             username=username,
                             password=password)
    return db, db['driftlon'][collection_name]
