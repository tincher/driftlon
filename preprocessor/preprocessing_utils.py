from get_from_db import DBReader
from driftlon_utils import flatten_dict


def transform_data_to_np(data):
    values = list(data.values())[1:]
    keys = list(data.keys())[1:]
    return values, keys


class DataFetcher:
    def __init__(self, mongo_address='localhost', mongo_username=None, mongo_password=None):
        self.db_reader = DBReader(
            mongo_address, mongo_username, mongo_password)

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
        player_ids = [element['player_id'] for element in matches]
        return data, target, player_ids

    def filter_and_flatten_match(self, match):
        participant_id = self.get_particpant_id(match)
        participant_data = match['data']['participants'][participant_id-1]
        flattened_participant_data = flatten_dict(participant_data)

        # team data
        stats = ['totalDamageDealtToChampions', 'kills',
                 'deaths', 'assists', 'totalDamageTaken', 'goldEarned']
        team_data = self.get_aggregated_data(
            match, stats, participant_data['teamId'])

        # python3.9: flattened_participant_data | team_data
        result = {**flattened_participant_data, **team_data}
        return result

    @staticmethod
    def get_aggregated_data(match, stats, participant_team_id):
        team_data = {}
        for stat in stats:
            value = sum([participant['stats'][stat] for participant in match['data']
                         ['participants'] if participant['teamId'] == participant_team_id])
            team_data[f'team_{stat}'] = value
        return team_data

    def flatten_match(self, match):
        flattened_match = flatten_dict(match)
        return flattened_match

    def get_particpant_id(self, match):
        participant_id = 0
        player = self.db_reader.get_player_for_id(match['player_id'])
        player_account_ids = [x['account_id']['accountId']
                              for x in player['soloq_ids'] if x['account_id'] is not None]
        for participant in match['data']['participantIdentities']:
            if participant['player']['accountId'] in player_account_ids:
                participant_id = participant['participantId']
        return participant_id
