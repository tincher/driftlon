import json

import requests

api_key = 'RGAPI-9db58bc2-97b2-42f9-a9cc-f28569151042'
api_url = 'https://{server}.api.riotgames.com{url_path}'


def get_json_from_url(url):
	return json.loads(requests.get(url).text)


def get_account_id_for_name(name, server):
	summoner_url = '/lol/summoner/v4/summoners/by-name/{}?api_key={}'.format(name, api_key)
	complete_url = api_url.format(url_path=summoner_url, server=server)
	req = requests.get(complete_url)
	summoner = json.loads(req.text)
	return summoner['accountId']


def get_full_match_list_for_account(account_id, server):
	matchlist_url = '/lol/match/v4/matchlists/by-account/{}?api_key={}'.format(account_id, api_key)
	complete_url = api_url.format(url_path=matchlist_url, server=server)
	return get_json_from_url(complete_url)


subdomain = 'euw1'
account_id = get_account_id_for_name('bigmcjoe', subdomain)
matchlist = get_full_match_list_for_account(account_id, subdomain)
print(matchlist)
