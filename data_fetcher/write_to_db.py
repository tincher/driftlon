import pymongo


def insert_or_update(collection, query, content):
	if len([x for x in collection.find(query)]) > 0:
		collection.update_one(query, {'$set': content})
	else:
		collection.insert_one(content)


def get_connection_for_collection_name(collection_name):
	db = pymongo.MongoClient('mongodb://localhost:27017')
	return db, db['driftlon'][collection_name]


def write_names_for_user(names_and_server, user, is_pro):
	db, collection = get_connection_for_collection_name('user_soloq')
	query, data = {'user': user}, {'user': user, 'data': names_and_server, 'is_pro': is_pro}
	insert_or_update(collection, query, data)
	db.close()


def write_gamelist_for_user_to_db(games, name, server):
	db, collection = get_connection_for_collection_name('match_list')
	query, data = {'name': name}, {'name': name, 'server': server, 'games': games}
	insert_or_update(collection, query, data)


def write_game(game):
	db, collection = get_connection_for_collection_name('matches')
	query, data = {'gameId': game['gameId']}, game
	insert_or_update(collection, query, data)


# write_names_for_user(['moinsen'], 'bigmcjoe', False)
write_game({'gameId': 'test'})
