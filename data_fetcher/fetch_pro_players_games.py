from data_fetcher.get_eligible_players import *

batch_size = 10
patch_count = 2
top_leagues = ["LoL European Championship", "League Championship Series", "LoL Champions Korea", "LoL Pro League"]


def write_user_batch(batch_size):
	player_batch = get_random_batch_of_players(batch_size)

	print(player_batch)


write_user_batch(batch_size)
