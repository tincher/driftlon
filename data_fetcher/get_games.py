import json

import requests

api_key = '?api_key=RGAPI-9db58bc2-97b2-42f9-a9cc-f28569151042'
api_url = 'https://{server}.api.riotgames.com{url_path}'


def get_json_from_url(url):
	return json.loads(requests.get(url).text)


def get_account_id_for_name(name, server):
	summoner_url = '/lol/summoner/v4/summoners/by-name/{}'.format(name) + api_key
	complete_url = api_url.format(url_path=summoner_url, server=server)
	return get_json_from_url(complete_url)['accountId']


def get_match_list_batch(account_id, server, begin_index):
	matchlist_url = '/lol/match/v4/matchlists/by-account/{}'.format(account_id) + api_key
	complete_url = api_url.format(url_path=matchlist_url, server=server) + '&beginIndex={}'.format(begin_index)
	return get_json_from_url(complete_url)


def get_full_match_list_for_account(account_id, server):
	result, start_index = [], 0
	response = get_match_list_batch(account_id, server, 0)
	result.extend(response['matches'])
	while response['endIndex'] < response['totalGames']:
		start_index = response['endIndex'] + 1
		response = get_match_list_batch(account_id, server, start_index)
		result.extend(response['matches'])
	return result


def get_match_for_match_id(match_id, server):
	match_url = '/lol/match/v4/matches/{}'.format(match_id) + api_key
	complete_url = api_url.format(url_path=match_url, server=server)
	return get_json_from_url(complete_url)


subdomain = 'euw1'
account_id = get_account_id_for_name('bigmcjoe', subdomain)
matchlist = get_full_match_list_for_account(account_id, subdomain)
match = get_match_for_match_id(matchlist[0]['gameId'], server=subdomain)
print(match)
