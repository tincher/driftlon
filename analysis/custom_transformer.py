import re
import numpy as np
from data_fetcher.get_from_db import DBReader
from sklearn.base import BaseEstimator, TransformerMixin

class TeamShareAdder(BaseEstimator, TransformerMixin):
    def __init__(self, attribute_names=[], config=[]):
        self.attribute_names = attribute_names #all attributes
        self.config = config # [(player_stat, team_stat)]
        self.config_idx = []

    def fit(self, X, y=None):
        player_stat_names, team_stat_names = list(zip(*self.config))
        player_stats_indices = [element[0] for element in enumerate(self.attribute_names) if element[1] in player_stat_names]
        team_stats_indices = [element[0] for element in enumerate(self.attribute_names) if element[1] in team_stat_names]
        self.config_idx = list(zip(player_stats_indices, team_stats_indices))
        return self

    def transform(self, X):
        result = X
        for current_idx in self.config_idx:
            # drin lassen wenn remake,nicht genau feststellbar + weniger overfitting
            # no division by zero
            team_value = X[:, current_idx[1]]
            team_value = np.where(team_value < 1, np.inf, team_value)
            new_attribute = X[:, current_idx[0]] / team_value
            result = np.c_[result, new_attribute]
        return result

class StatPerTimeAdder(BaseEstimator, TransformerMixin):
    def __init__(self, attribute_names=[], config=[]):
        self.attribute_names = attribute_names #all attributes
        self.config = config # [stat1, stat2]
        self.match_time_id = self.attribute_names.index('match_length')
        self.config_idx = []

    def fit(self, X, y=None):
        self.config_idx = [element[0] for element in enumerate(self.attribute_names) if element[1] in self.config]
        print(self.config_idx, self.config)
        return self

    def transform(self, X):
        result = X
        for current_id in self.config_idx:
            # no division by zero
            match_lengths = X[:, self.match_time_id]
            team_value = np.where(match_lengths < 1, np.inf, match_lengths)
            new_attribute = X[:, current_id] / match_lengths
            result = np.c_[result, new_attribute]
        return result
