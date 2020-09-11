from driftlon_utils import get_connection_for_collection_name
from datetime import datetime, timedelta
import random
import tensorflow as tf


#todo these 4 are a duplicate (get_data)
def get_player_ids_in_timespan(batch_size, timespan):
	db, collection = get_connection_for_collection_name('processed_matches')
	timestamp_for_span = int((datetime.utcnow() - timespan).timestamp())
	players = list(collection.find({'timestamp': {'$gt': timestamp_for_span}}).distinct('player_id'))
	db.close()
	return players[:batch_size]

def get_matches_batch(player_ids, batch_size=1, timespan=timedelta(weeks=2)):
	db, collection = get_connection_for_collection_name('processed_matches')
	timestamp_for_span = int((datetime.utcnow() - timespan).timestamp())
	result = []
	for player_id in player_ids:
		db_result = collection.find({'timestamp': {'$gt': timestamp_for_span}, 'player_id': player_id})
		result.append(list(db_result))
	db.close()
	random.shuffle(result)
	return result[:batch_size]

def get_batch(batch_size, timespan=timedelta(weeks=2)):
	players = get_player_ids_in_timespan(batch_size, timespan)
	player_ids = get_player_ids_in_timespan(batch_size, timespan)
	db_result = get_matches_batch(player_ids, batch_size, timespan)
	data, target = [], []
	for i in range(len(db_result)):
		data.append([match['data'] for match in db_result[i]])
		target.append(db_result[i][0]['target'])
	return data, target

def get_data_batch(batch_size, matches_count=50, timespan=timedelta(weeks=2)):
	data, target = get_batch(batch_size)
	for index in range(len(data)):
		data[index] = data[index][-matches_count:]
		if len(data[index]) < matches_count:
			data[index].extend([[0] * 35 for _ in range(matches_count - len(data[index]))])
	return data, target


def _int64_feature(value):
	return tf.train.Feature(int64_list=tf.train.Int64List(value=[value]))

def _float_feature(value):
	return tf.train.Feature(float_list=tf.train.FloatList(value=value))

def _match_list_as_feature(match_list):
	return tf.io.FixedLenFeature()



def write_tf_record(batch_size, match_depth):
	data, target = get_data_batch(batch_size)
	record_file = 'matches.tfrecords'
	with tf.io.TFRecordWriter(record_file) as writer:
		for i in range(len(data)):
			tf_example = get_example_for_match_list(data[i], target[i])
			writer.write(tf_example.SerializeToString())

def get_example_for_match_list(match_list, target):
	feature = {
	  'match_list': _float_feature(match_list),
	  'label': _int64_feature(label),
	}
	return tf.train.Example(features=tf.train.Features(feature=feature))





if __name__ == '__main__':
	write_tf_record(10, 10)
