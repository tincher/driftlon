from datetime import datetime
from write_to_db import get_connection_for_collection_name
import pymongo


def get_oldest_updated_batch_of_players(batch_size):
    db, connection = get_connection_for_collection_name('player')
    players = connection.find({'soloq_ids': {'$ne': None}}).sort('timestamp')
    return list(players[:batch_size])
