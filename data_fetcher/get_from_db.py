from driftlon_utils import get_connection_for_collection_name
from datetime import datetime
import logging


class DBReader:
    def __init__(self, ip='localhost', username=None, password=None):
        self.db, self.player_collection = get_connection_for_collection_name('player', ip, username, password)
        self.db, self.matches_collection = get_connection_for_collection_name('matches', ip, username, password)

    def get_oldest_updated_batch_of_players(self, batch_size):
        players = self.player_collection.find({'soloq_ids': {'$ne': None}}).sort('timestamp').limit(batch_size)
        logging.info(f'MONGO: oldest batch - size: {batch_size}')
        return list(players)

    def get_player_for_id(self, player_id):
        player = self.player_collection.find_one({'id': player_id})
        logging.info(f'MONGO: player - id {player_id}')
        return player

    def get_matches_batch(self, limit, offset=0):
        matches = self.matches_collection.find(projection=['pro_games_count', 'data', 'player_id'], limit=limit,
                                               skip=offset)
        return list(matches)
