from driftlon_utils import get_connection_for_collection_name
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

class DBWriter:
    player_collection, matches_collection = None, None
    db_player, db_matches = None, None

    def __init__(self):
        self.db_player, self.player_collection = get_connection_for_collection_name('player')
        self.db_matches, self.matches_collection = get_connection_for_collection_name('matches')
        self.db_processed, self.processed_collection = get_connection_for_collection_name('processed_matches')

    @staticmethod
    def get_hash(value):
        return hashlib.sha256(value.encode('utf-8')).hexdigest()

    @staticmethod
    def insert_or_update(collection, query, content):
        if len([x for x in collection.find(query)]) > 0:
            collection.update_one(query, {'$set': content})
        else:
            collection.insert_one(content)

    def update_user_timestamp(self, player):
        query = {'id': self.get_hash(player['name'])}
        new_timestamp = {'$set': {'timestamp': datetime.utcnow()}}
        answer = self.player_collection.update_one(query, new_timestamp)

    def write_user(self, player):
        name, soloq_ids, pro_games = player['name'], player['soloq_ids'], player['pro_games']
        hash_name = self.get_hash(name)
        query = {'id': hash_name}
        data = {'id': hash_name, 'name': name, 'soloq_ids': soloq_ids, 'pro_games': int(pro_games),
                'timestamp': datetime.utcnow()}
        self.insert_or_update(self.player_collection, query, data)

    def write_game(self, game, player):
        data = {'data': game, 'timestamp': datetime.utcnow(), 'player_id': self.get_hash(
            player['name']), 'pro_games_count': int(player['pro_games'])}
        if 'gameId' not in game.keys():
            print(game)
            return
        query = {'game_id': game['gameId']}
        self.insert_or_update(self.matches_collection, query, data)

    def write_processed_game(self, processed_game, target, player_id, timestamp=int(datetime.utcnow().timestamp())):
        processed_game_list = processed_game.tolist()
        data = {'data': processed_game_list, 'target': target, 'timestamp': timestamp, 'player_id': player_id}
        query = {'player_id': player_id, 'timestamp': timestamp}
        self.insert_or_update(self.processed_collection, query, data)

if __name__ == '__main__':
    player = {'name': 'WildTurtle'}
    update_user_timestamp(player)
    print(get_hash(player['name']))
