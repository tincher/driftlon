import sys
sys.path.append(".")
sys.path.append("..")

from datetime import datetime
from get_from_db import *
from write_to_db import DBWriter
from leaguepedia_layer import LPLayer
from trackingthepros_layer import TTPLayer


batch_size = 20
patch_count = 2
top_leagues = ["LoL European Championship", "League Championship Series", "LoL Champions Korea", "LoL Pro League"]
DBWriter = DBWriter()
DBReader = DBReader()
LPLayer = LPLayer()
TTPLayer = TTPLayer()
RiotLayer = RiotLayer()

def fetch_all_users():
    players = LPLayer.get_all_eligible_players()
    for player in players:
        player['soloq_ids'] = TTPLayer.get_soloq_ids_from_trackingthepros(player['name'])
        if player['soloq_ids'] is not None:
            for soloq_id in player['soloq_ids']:
                soloq_id['account_id'] = RiotLayer.get_account_id_for_name(soloq_id['account_name'], soloq_id['server'])
        DBWriter.write_user(player)


def fetch_user_batch(batch_size):
    player_batch = LPLayer.get_random_batch_of_players(batch_size)
    for player in player_batch:
        player['soloq_ids'] = TTPLayer.get_soloq_ids_from_trackingthepros(player['name'])
        if player['soloq_ids'] is not None:
            for soloq_id in player['soloq_ids']:
                soloq_id['account_id'] = RiotLayer.get_account_id_for_name(soloq_id['account_name'], soloq_id['server'])
        DBWriter.write_user(player)


def fetch_games_for_oldest_batch(batch_size):
    players = DBReader.get_oldest_updated_batch_of_players(batch_size)
    for player in players:
        for soloq_id in player['soloq_ids']:
            match_list = RiotLayer.get_matchlist_for_player_since_number_of_patches(soloq_id['account_id'], soloq_id['server'], 1)
            for match in match_list:
                result = RiotLayer.get_match_for_match_id(match['gameId'], soloq_id['server'])
                DBWriter.write_game(result, player)
        # DBWriter.update_user_timestamp(player)


if __name__ == '__main__':
    # fetch_user_batch(batch_size)
    fetch_all_users()
    # fetch_games_for_oldest_batch(batch_size)
