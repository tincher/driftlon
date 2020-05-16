from datetime import datetime
from driftlon_utils import get_connection_for_collection_name
import pymongo



class DBReader:
    def __init__(self):
        self.db, self.player_collection = get_connection_for_collection_name('player')

    def get_oldest_updated_batch_of_players(self, batch_size):
        players = self.player_collection.find({'soloq_ids': {'$ne': None}}).sort('timestamp')
        return list(players[:batch_size])

    def get_player_for_id(self, player_id):
        player = self.player_collection.find_one({'id': player_id})
        return player
