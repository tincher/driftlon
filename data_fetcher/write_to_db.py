import pymongo


def insert_or_update(collection, query, content):
	if len([x for x in collection.find(query)]) > 0:
		collection.update_one(query, {'$set': content})
	else:
		collection.insert_one(content)


def get_connection_for_collection_name(collection_name):
	db = pymongo.MongoClient('mongodb://localhost:27017')
	return db, db['driftlon'][collection_name]


def write_user(name, soloq_ids, pro_games_count):
	db, collection = get_connection_for_collection_name('player')
	query, data = {'id': hash(name)}, {'id': hash(name), 'name': name, 'soloq_ids': soloq_ids,
									   'pro_games_count': pro_games_count}
	insert_or_update(collection, query, data)


def write_game(game):
	db, collection = get_connection_for_collection_name('matches')
	query, data = {'gameId': game['gameId']}, game
	insert_or_update(collection, query, data)


# write_names_for_user(['moinsen'], 'bigmcjoe', False)
# write_game({'gameId': 'test'})
