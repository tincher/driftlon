import logging
import hashlib
from datetime import datetime, timedelta
from driftlon_utils import get_connection_for_collection_name


class DBWriter:
    def __init__(self, ip='localhost', username=None, password=None):
        print(ip, username, password)
        self.db_player, self.player_collection = get_connection_for_collection_name('player', ip, username, password)
        self.db_matches, self.matches_collection = get_connection_for_collection_name('matches', ip, username, password)
        self.db_processed, self.processed_collection = get_connection_for_collection_name(
            'processed_matches', ip, username, password)

    @staticmethod
    def get_hash(value):
        return hashlib.sha256(value.encode('utf-8')).hexdigest()

    @staticmethod
    def insert_or_update(collection, query, content):
        if len([x for x in collection.find(query)]) > 0:
            return collection.update_one(query, {'$set': content})
        else:
            return collection.insert_one(content)

    def update_user_timestamp(self, player):
        query = {'id': self.get_hash(player['name'])}
        new_timestamp = {'$set': {'timestamp': datetime.utcnow()}}
        result = self.player_collection.update_one(query, new_timestamp)
        logging.info('MONGO: update timestamp - name: {}'.format(player['name']))

    def write_user(self, player):
        name, soloq_ids, pro_games = player['name'], player['soloq_ids'], player['pro_games']
        hash_name = self.get_hash(name)
        query = {'id': hash_name}
        data = {
            'id': hash_name,
            'name': name,
            'soloq_ids': soloq_ids,
            'pro_games': int(pro_games),
            'timestamp': datetime.utcnow() - timedelta(weeks=4)
        }
        result = self.insert_or_update(self.player_collection, query, data)
        logging.info(f'MONGO: write user - name: {player["name"]}')

    def write_game(self, game, player):
        data = {
            'data': game,
            'timestamp': datetime.utcnow(),
            'player_id': self.get_hash(player['name']),
            'pro_games_count': int(player['pro_games'])
        }
        query = {'game_id': game['gameId']}
        result = self.insert_or_update(self.matches_collection, query, data)
        logging.info(f'MONGO: write game - name: {player["name"]} - gameId: {game["gameId"]}')

    def write_processed_game(self, processed_game, target, player_id, timestamp=int(datetime.utcnow().timestamp())):
        data = {'data': processed_game, 'target': target, 'timestamp': timestamp, 'player_id': player_id}
        query = {'player_id': player_id, 'data': processed_game}
        result = self.insert_or_update(self.processed_collection, query, data)
        logging.info(f'MONGO: write processed game - player_id: {player_id} - timestamp: {timestamp}')


if __name__ == '__main__':
    player = {'name': 'WildTurtle'}
    # update_user_timestamp(player)
    # print(get_hash(player['name']))
