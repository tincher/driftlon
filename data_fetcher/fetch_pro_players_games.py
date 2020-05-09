from get_eligible_players import *
from write_to_db import *
from get_from_db import *
from get_games import *
from datetime import datetime

batch_size = 10
patch_count = 2
top_leagues = ["LoL European Championship",
               "League Championship Series", "LoL Champions Korea", "LoL Pro League"]


def fetch_all_users():
    players = get_all_eligible_players()
    for player in players:
        player['soloq_ids'] = get_soloq_ids_from_trackingthepros(player['name'])
        write_user(player)


def fetch_user_batch(batch_size):
    player_batch = get_random_batch_of_players(batch_size)
    for player in player_batch:
        player['soloq_ids'] = get_soloq_ids_from_trackingthepros(player['name'])
        write_user(player)


def fetch_games_wrt_rate_limit():
    players = get_oldest_updated_batch_of_players(10)
    for player in players:
        for soloq_id in player['soloq_ids']:
            match_list = get_matchlist_for_player_since_number_of_patches(soloq_id['account_name'], soloq_id['server'], 1)
            for match in match_list:
                result = get_match_for_match_id(match['gameId'], soloq_id['server'])
                write_game(result, player)
        update_user_timestamp(player)


# fetch_user_batch(batch_size)
fetch_all_users()
fetch_games_wrt_rate_limit()
