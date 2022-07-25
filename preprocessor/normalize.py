from driftlon_utils import *
from write_to_db import DBWriter
import random
import numpy as np
import os

db_writer = DBWriter(os.environ['MONGODB_ADDRESS'])


def get_all_processed_matches():
    db, collection = get_connection_for_collection_name('processed_matches')
    matches = list(collection.find({}))
    random.shuffle(matches)
    db.close()
    return matches


def get_z_score(match, means, stddevs):
    #z-score -> mean is 0 and stddev is 1
    return (match - means) / stddevs


def get_normalized_matches(matches_data):
    result = []
    means = np.mean(matches_data, axis=0)
    standard_derivations = np.std(matches_data, axis=0)
    max = np.max(matches_data, axis=0)
    for match in matches_data:
        result.append(get_z_score(match, means, standard_derivations))
    return result


def normalize_all():
    matches = get_all_processed_matches()
    matches_data = [match['data'] for match in matches]
    normalized_matches = get_normalized_matches(matches_data)
    for normalized_match, match in zip(normalized_matches, matches):
        db_writer.write_normalized_game(normalized_match.tolist(), match['target'], match['player_id'],
                                        match['timestamp'])


if __name__ == '__main__':
    normalize_all()
