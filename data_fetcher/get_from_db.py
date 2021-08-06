from datetime import datetime
from driftlon_utils import get_connection_for_collection_name
import pymongo
import logging


class DBReader:
    def __init__(self, ip='localhost', username=None, password=None):
        self.db, self.player_collection = get_connection_for_collection_name('player', ip, username, password)

    def get_oldest_updated_batch_of_players(self, batch_size):
        players = self.player_collection.find({'soloq_ids': {'$ne': None}}).sort('timestamp').limit(batch_size)
        logging.info('MONGO: oldest batch - size: {}'.format(batch_size))
        return list(players)

    def get_player_for_id(self, player_id):
        player = self.player_collection.find_one({'id': player_id})
        logging.info('MONGO: player - id {}'.format(player_id))
        return player
