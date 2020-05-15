from datetime import datetime
from driftlon_utils import get_connection_for_collection_name
import pymongo


#todo make class

def get_oldest_updated_batch_of_players(batch_size):
    db, connection = get_connection_for_collection_name('player')
    players = connection.find({'soloq_ids': {'$ne': None}}).sort('timestamp')
    return list(players[:batch_size])

def get_player_for_id(player_id):
    db,connection = get_connection_for_collection_name('player')
    player = connection.find_one({'id': player_id})
    return player
