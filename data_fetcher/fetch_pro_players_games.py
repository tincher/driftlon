from get_eligible_players import *
from write_to_db import *

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


# fetch_user_batch(batch_size)
fetch_all_users()
