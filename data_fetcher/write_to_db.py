from datetime import datetime
import hashlib

import pymongo

# todo db open und close zentralisieren
# maybe: response von db status


def get_hash(value):
    return hashlib.sha256(value.encode('utf-8')).hexdigest()


def insert_or_update(collection, query, content):
    if len([x for x in collection.find(query)]) > 0:
        collection.update_one(query, {'$set': content})
    else:
        collection.insert_one(content)


def get_connection_for_collection_name(collection_name):
    db = pymongo.MongoClient('mongodb://localhost:27017')
    return db, db['driftlon'][collection_name]


def update_user_timestamp(player):
    db, collection = get_connection_for_collection_name('player')
    query = {'id': get_hash(player['name'])}
    new_timestamp = {"$set": {"timestamp": datetime.utcnow()}}
    answer = collection.update_one(query, new_timestamp)
    db.close()


def write_user(player):
    db, collection = get_connection_for_collection_name('player')
    name, soloq_ids, pro_games = player['name'], player['soloq_ids'], player['pro_games']
    hash_name = get_hash(name)
    query = {'id': hash_name}
    data = {'id': hash_name, 'name': name, 'soloq_ids': soloq_ids, 'pro_games': pro_games,
            'timestamp': datetime.utcnow()}
    insert_or_update(collection, query, data)
    db.close()


def write_game(game, player):
    db, collection = get_connection_for_collection_name('matches')
    data = {'data': game, 'timestamp': datetime.utcnow(), 'player_id': get_hash(
        player['name']), 'pro_games_count': int(player['pro_games'])}
    query = {'game_id': game['gameId']}
    insert_or_update(collection, query, data)
    db.close()


if __name__ == '__main__':
    player = {'name': 'WildTurtle'}
    update_user_timestamp(player)
    print(get_hash(player['name']))
