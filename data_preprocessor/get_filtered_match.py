from data_fetcher.write_to_db import get_connection_for_collection_name


def get_match():
	db, collection = get_connection_for_collection_name('matches')
