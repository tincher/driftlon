import re
import numpy as np
from driftlon_utils import *
from data_fetcher.get_from_db import *
from sklearn.base import BaseEstimator, TransformerMixin


def transform_data_to_np(data):
    values = list(data.values())[1:]
    keys = list(data.keys())[1:]
    return values, keys

class PerMinAdder(BaseEstimator, TransformerMixin):
    def __init__(self, attribute_names):
        pass

    def fit(self, X, y=None):
        pass

    def transform(self, X):
        pass

class TeamShareAdder(BaseEstimator, TransformerMixin):
    def __init__(self, attribute_names=[], wanted_attributes=[], db_connector=None):
        self.attribute_names = attribute_names #all attributes
        self.db_connector = db_connector
        self.wanted_attributes = wanted_attributes # attributes to be summed
        self.attributes_idx = [[] for wanted_attribute in wanted_attributes]
        self.participant_ids = []

    def fit(self, X, y=None):
        print('fit')
        for wanted_attribute in self.wanted_attributes:
#             keys = list(filter(lambda x: re.match(f'data_participants_\d_stats_{wanted_attribute}', x), self.attribute_names))
            keys = [x for x in self.attribute_names if re.match(f'stats_{wanted_attribute}', x)]
            indices = [element[0] for element in enumerate(self.attribute_names) if element[1] in keys]
            self.attributes_idx.append(indices)
        for game in X:
            self.participant_ids.append(self.db_connector.get_particpant_id(game))
        return self

    def transform(self, X):
        print('trans')
        result = X
        for attribute_name, attributes_idx in zip(self.attribute_names, self.attributes_idx):
            team0_sums = np.sum(X[:, attributes_idx[:5]], axis=1, keepdims=True)
            team1_sums = np.sum(X[:, attributes_idx[5:]], axis=1, keepdims=True)
            mask = np.c_[self.participant_ids<5, self.participant_ids>=5]

            new_attribute = np.sum(np.c_[team0_sums, team1_sums]*mask, axis=1, keepdims=True)

            result = np.c_[result, new_attribute]
        return result

class DataFetcher:
    def __init__(self, mongo_address='localhost', mongo_username=None, mongo_password=None):
        self.db_reader = DBReader(mongo_address, mongo_username, mongo_password)

    def get_data(self, batch_size=10000, offset=0):
        data, target = [], []

        new_data, new_target = self.get_raw_data_batch(batch_size, offset)

        while len(new_target) > 0:
            data.extend(new_data)
            target.extend(new_target)

            offset += batch_size
            new_data, new_target = self.get_raw_data_batch(batch_size, offset)

            # print(len(target))
        return data, target

    def get_raw_data_batch(self, limit, offset=0):
        matches = self.db_reader.get_matches_batch(limit, offset=offset)
        data = [self.flatten_match(element) for element in matches]
        target = [element['pro_games_count'] for element in matches]
        return data, target

    def get_filtered_data_batch(self, limit, offset=0):
        matches = self.db_reader.get_matches_batch(limit, offset=offset)
        data = [self.filter_and_flatten_match(element) for element in matches]
        target = [element['pro_games_count'] for element in matches]
        return data, target

    def filter_and_flatten_match(self, match):
        participant_id = self.get_particpant_id(match)
        participant_data = match['data']['participants'][participant_id-1]
        flattened_participant_data = flatten_dict(participant_data)

        # team data
        stats = ['totalDamageDealtToChampions', 'kills', 'deaths', 'assists', 'totalDamageTaken', 'goldEarned']
        team_data = self.get_aggregated_data(match, stats, participant_data['teamId'])

        result = {**flattened_participant_data, **team_data} # python3.9: flattened_participant_data | team_data
        return result

    @staticmethod
    def get_aggregated_data(match, stats, participant_team_id):
        team_data = {}
        for stat in stats:
            value = sum([participant['stats'][stat] for participant in match['data']['participants'] if participant['teamId'] == participant_team_id])
            team_data[f'team_{stat}'] = value
        return team_data

    def flatten_match(self, match):
        flattened_match = flatten_dict(match)
        return flattened_match

    def get_particpant_id(self, match):
        participant_id = 0
        player = self.db_reader.get_player_for_id(match['player_id'])
        player_account_ids = [x['account_id']['accountId'] for x in player['soloq_ids'] if x['account_id'] is not None]
        for participant in match['data']['participantIdentities']:
            if participant['player']['accountId'] in player_account_ids:
                participant_id = participant['participantId']
        return participant_id



def get_data_for_keys(common_keys, X):
    values_list = []
    for key in common_keys:
        values = [element[key] for element in X]
        values_list.append(values)
    return values_list


def get_common_keys(X):
    keys = []
    for element in X:
        keys.extend(element.keys())

    keys = list(set(keys))
    result_keys = sorted(list(filter(lambda x: all(x in element.keys() for element in X), keys)))
    return result_keys


def get_all_keys(X):
    keys = []
    for element in X:
        keys.extend(element.keys())

    keys = list(set(keys))
    result_keys = sorted(list(filter(lambda x: any(x in element.keys() for element in X), keys)))
    return result_keys
