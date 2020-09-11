from driftlon_utils import get_connection_for_collection_name
import pymongo


def get_duplicates_from_collection(collection):
    pipeline = [{'$unwind': '$data'},
                {'$group': {'_id': {'gameId': '$data.gameId', 'platformId': '$data.platformId'}, 'count': {'$sum': 1}}},
                {'$match': {'_id': {'$ne': None}, 'count': {'$gt': 1}}}]
    duplicates = collection.aggregate(pipeline)
    return duplicates


def clean_collection(collection_name):
    db, collection = get_connection_for_collection_name(collection_name)
    duplicates = get_duplicates_from_collection(collection)
    for duplicate in duplicates:
        query = {'data.gameId': duplicate['_id']['gameId'], 'data.platformId': duplicate['_id']['platformId']}
        for i in range(1, duplicate['count']):
            result = collection.delete_one(query)
    db.close()

def get_players_by_query(query):
    db, collection = get_connection_for_collection_name('player')
    result = list(collection.find(query))
    db.close()
    return result

def get_all_pro_ids():
    query = {'pro_games': {'$gt': 0}}
    pros = get_players_by_query(query)
    result = []
    for pro in pros:
        if pro['soloq_ids'] is not None:
            for id in pro['soloq_ids']:
                if id['account_id'] is not None:
                    result.append(id['account_id']['accountId'])
    return result

def get_all_casuals():
    query = {'pro_games': 0}
    return get_players_by_query(query)


def remove_casual(casual):
    db, collection = get_connection_for_collection_name('player')
    query = {'id': casual['id']}
    pros = collection.delete_one(query)
    db.close()


def clean_players_from_pros():
    pro_ids = get_all_pro_ids()
    casuals = get_all_casuals()
    for casual in casuals:
        if casual['soloq_ids'][0]['account_id']['accountId'] in pro_ids:
            remove_casual(casual)



def clean_matches_from_duplicates():
    clean_collection('matches')


def clean_players_from_duplicates():
    clean_collection('player')


if __name__ == '__main__':
    clean_players_from_pros()
