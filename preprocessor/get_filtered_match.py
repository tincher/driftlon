import sys
sys.path.append(".")
sys.path.append("/Users/joelewig/projects/driftlon")
sys.path.append("/Users/joelewig/projects/driftlon/data_fetcher")


from driftlon_utils import *
from get_from_db import *
import random
import pymongo
import json

DBReader = DBReader()


def get_random_matches_batch(batch_size):
    db, collection = get_connection_for_collection_name('matches')
    matches = list(collection.find({}))
    random.shuffle(matches)
    db.close()
    return matches[:batch_size]


def get_particpant_id(match):
    participant_id = 0
    player = DBReader.get_player_for_id(match['player_id'])
    player_account_ids = [x['account_id'] for x in player['soloq_ids']]
    for participant in match['data']['participantIdentities']:
        if participant['player']['accountId'] in player_account_ids:
            participant_id = participant['participantId']
    return participant_id

def get_transformed_match(match):
    # participant stats nur von spieler
    # participantIdentities -> participants -> teamId
    # keep timestamp
    participant_id = get_particpant_id(match)
    if participant_id == 0:
        #todo raise error
        return []
    match['participant_stats'] = match['data']['participants'][participant_id-1]
    match['data'].pop('participants')
    match['data'].pop('participantIdentities')
    flat_match = my_flatten(match)
    # todo filter relevant infos
    irrelevant_info = ['_id']
    for key in irrelevant_info:
        flat_match.pop(key)
    return flat_match




if __name__ == '__main__':
    match = get_random_matches_batch(1)[0]
    # print(json.dumps(tmp))
    print(get_transformed_match(match))
