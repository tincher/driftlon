from datetime import datetime

import pymongo


def insert_or_update(collection, query, content):
	if len([x for x in collection.find(query)]) > 0:
		collection.update_one(query, {'$set': content})
	else:
		collection.insert_one(content)


def get_connection_for_collection_name(collection_name):
	db = pymongo.MongoClient('mongodb://localhost:27017')
	return db, db['driftlon'][collection_name]


def write_user(player):
	db, collection = get_connection_for_collection_name('player')
	name, soloq_ids, pro_games = player['name'], player['soloq_ids'], player['pro_games']
	hash_name = hash(name)
	query = {'id': hash_name}
	data = {'id': hash_name, 'name': name, 'soloq_ids': soloq_ids, 'pro_games': pro_games,
			'timestamp': datetime.utcnow()}
	insert_or_update(collection, query, data)


def write_game(game):
	db, collection = get_connection_for_collection_name('matches')
	query, data = {'gameId': game['gameId']}, game
	insert_or_update(collection, query, data)
