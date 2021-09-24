import re
import numpy as np
from data_fetcher.get_from_db import DBReader
from sklearn.base import BaseEstimator, TransformerMixin

class TeamShareAdder(BaseEstimator, TransformerMixin):
    def __init__(self, attribute_names=[], config=[], db_config=None):
        self.attribute_names = attribute_names #all attributes
        self.db_config = db_config
        self.config = config # [(player_stat, team_stat)] 
        self.config_idx = []
        self.participant_ids = []

    def fit(self, X, y=None):
        db_reader = DBReader(self.db_config['address'], self.db_config['username'], self.db_config['password'])
        player_stat_names, team_stat_names = list(zip(*self.config))
        player_stats_indices = [element[0] for element in enumerate(self.attribute_names) if element[1] in player_stat_names]
        team_stats_indices = [element[0] for element in enumerate(self.attribute_names) if element[1] in team_stat_names]
        self.config_idx = list(zip(player_stats_indices, team_stats_indices))
        return self

    def transform(self, X):
        result = X
        for current_idx in self.config_idx:
            new_attribute = X[:, current_idx[0]] / X[:, current_idx[1]]
            result = np.c_[result, new_attribute]
        return result
    
    def get_participant_id(self, match, db_reader):
        participant_id = 0
        print(match)
        player = db_reader.get_player_for_id(match['player_id'])
        player_account_ids = [x['account_id']['accountId'] for x in player['soloq_ids'] if x['account_id'] is not None]
        for participant in match['data']['participantIdentities']:
            if participant['player']['accountId'] in player_account_ids:
                participant_id = participant['participantId']
        return participant_id