import sys

sys.path.append(".")
sys.path.append("/Users/joelewig/projects/driftlon")
sys.path.append("/Users/joelewig/projects/driftlon/data_fetcher")

from driftlon_utils import *
from get_from_db import *
import random
import json
import statistics
import numpy as np

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


def get_processed_stats(stats, items_to_be_kept):
	result = {}
	for key in stats:
		if key in items_to_be_kept:
			result[key] = stats[key]
	return result


def get_processed_timeline_data(match, items_to_be_kept):
	offset = 2
	result = {}
	for item in items_to_be_kept[offset:]:
		try:
			result[item] = match['participant_stats']['timeline'][item]
			result[item] = statistics.median(result[item].values())
		except:
			result[item] = 0
	result = {k: int(v) for k, v in result.items()}
	for item in items_to_be_kept[:offset]:
		result[item] = match['participant_stats']['timeline'][item]
	return result

def get_target_for_match(match, threshold=20):
    return int(match['pro_games_count'] > threshold)


def get_transformed_match(match):
	result = {}
	participant_id = get_particpant_id(match)
	if participant_id == 0:
		return []
	match['participant_stats'] = match['data']['participants'][participant_id - 1]
	config = json.loads(open('./preprocessor/config.json').read())
	match['team_stats'] = match['data']['teams'][int((int(match['participant_stats']['teamId']) / 100)) - 1]
	result['team_stats'] = get_processed_stats(match['team_stats'], config['team_stats'])
	result['participant_stats'] = get_processed_stats(match['participant_stats']['stats'], config['participant_stats'])
	result['timeline_data'] = get_processed_timeline_data(match, config['participant_timeline_keep'])
	result['participant'] = get_processed_stats(match['participant_stats'], config['participant'])
	result['game']=get_processed_stats(match['data'], config['game'])
	return result


def get_match_as_vector(match):
	match_as_list = list(my_flatten(match).values())
	return np.array(match_as_list)


if __name__ == '__main__':
	match = get_random_matches_batch(1)[0]
	transformed_match = get_transformed_match(match)
	vector = get_match_as_vector(transformed_match)
	# print(json.dumps(match, default=str))
	# print(json.dumps(get_transformed_match(match), default=str))
	# print(json.dumps(get_match_as_vector(transformed_match), default=str))
