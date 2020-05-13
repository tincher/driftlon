from driftlon_utils import get_connection_for_collection_name
import pymongo


def get_duplicates_from_collection(collection):
    pipeline = [{'$unwind': '$data'},
                {"$group": {"_id": {"gameId": "$data.gameId", "platformId": "$data.platformId"}, "count": {"$sum": 1}}},
                {"$match": {"_id": {"$ne": None}, "count": {"$gt": 1}}}]
    duplicates = collection.aggregate(pipeline)
    return duplicates


def clean_collection(collection_name):
    db, collection = get_connection_for_collection_name(collection_name)
    duplicates = get_duplicates_from_collection(collection)
    for duplicate in duplicates:
        query = {'data.gameId': duplicate["_id"]['gameId'], 'data.platformId': duplicate["_id"]['platformId']}
        for i in range(1, duplicate['count']):
            result = collection.delete_one(query)
    db.close()


def clean_matches_from_duplicates():
    clean_collection('matches')


def clean_players_from_duplicates():
    clean_collection('player')


clean_matches_from_duplicates()
