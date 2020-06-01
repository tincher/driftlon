import sys

sys.path.append('.')
sys.path.append('/Users/joelewig/projects/driftlon')
sys.path.append('/Users/joelewig/projects/driftlon/data_fetcher')

from driftlon_utils import *
from get_from_db import *
from write_to_db import *
import random
import json
import statistics
import numpy as np
# import tensorflow as tf
from tensorflow import strings as tfs

DBReader = DBReader()
DBWriter = DBWriter()


def get_random_matches_batch(batch_size):
	db, collection = get_connection_for_collection_name('matches')
	matches = list(collection.find({}))
	random.shuffle(matches)
	db.close()
	return matches[:batch_size]


def get_particpant_id(match):
	participant_id = 0
	player = DBReader.get_player_for_id(match['player_id'])
	player_account_ids = []
	player_account_ids = [x['account_id']['accountId'] for x in player['soloq_ids'] if x['account_id'] is not None]
	for participant in match['data']['participantIdentities']:
		if participant['player']['accountId'] in player_account_ids:
			participant_id = participant['participantId']
	return participant_id


def get_processed_stats(stats, items_to_be_kept):
	result = {}
	for key in items_to_be_kept:
		if key in stats.keys():
			result[key] = stats[key]
		else:
			#todo maybe median
			result[key] = 0
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


def transform_match_by_config(match, config, participant_id):
	result = {}
	match['participant_stats'] = match['data']['participants'][participant_id - 1]
	match['team_stats'] = match['data']['teams'][int((int(match['participant_stats']['teamId']) / 100)) - 1]

	result['team_stats'] = get_processed_stats(match['team_stats'], config['team_stats'])
	result['participant_stats'] = get_processed_stats(match['participant_stats']['stats'], config['participant_stats'])
	result['timeline_data'] = get_processed_timeline_data(match, config['participant_timeline_keep'])
	result['participant'] = get_processed_stats(match['participant_stats'], config['participant'])
	result['game'] = get_processed_stats(match['data'], config['game'])
	return result

def get_transformed_match(match):
	participant_id = get_particpant_id(match)
	if participant_id == 0:
		return []
	config = json.loads(open('./preprocessor/config.json').read())
	return transform_match_by_config(match, config, participant_id)


def get_match_as_vector(match):
	match_as_list = list(my_flatten(match).values())
	return np.array(match_as_list)

def get_match_vector_batch(batch_size):
	matches = get_random_matches_batch(batch_size)
	data, targets = [], []
	for match in matches:
		transformed_match = get_transformed_match(match)
		bucketized_match = get_bucketized_match(transformed_match)
		data.append(bucketized_match)
		targets.append(get_target_for_match(match))
	return data, targets

def get_bucketized_match(match):
    bucket_list = [3, 21, 31, 32]
    for entry in bucket_list:
        value = tfs.to_hash_bucket_strong(list(str(match[entry])), 20, [0, 0]).numpy()
        match[entry] = value[0]
    return match

def transform_batch(batch_size):
	matches = get_random_matches_batch(batch_size)
	for match in matches:
		transformed_match = get_transformed_match(match)
		if transformed_match != []:
			vector = get_match_as_vector(transformed_match)
			bucketized_vector = get_bucketized_match(vector)
			if len(bucketized_vector) != 35:
				print(transformed_match)
			target = get_target_for_match(match)
			DBWriter.write_processed_game(bucketized_vector, target, match['player_id'], match['data']['gameCreation'])

if __name__ == '__main__':
	batch_size = int(sys.argv[1])
	transform_batch(batch_size)
