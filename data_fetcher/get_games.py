import json
from datetime import datetime, timedelta

import requests

api_key = '?api_key=RGAPI-a35c93a9-3dc3-42da-8846-3149295755d7'
api_url = 'https://{server}.api.riotgames.com{url_path}'

subdomains = {'[NA]': 'na1', '[EU]': 'euw1', '[EUW]': 'euw1', '[KR]': 'kr', '[EUNE]': 'eun1', '[BR]': 'br1'}
time_response_codes = [429, 504]
last_requests_timestamps = []


def get_subdomain_for_region(region):
    return subdomains[region]


def time_to_wait():
    global last_requests_timestamps
    result = 0
    now = datetime.utcnow()
    short_time_limit = [x for x in last_requests_timestamps if x + timedelta(seconds=1) > now]
    long_time_limit = [x for x in last_requests_timestamps if x + timedelta(minutes=2) > now]
    last_requests_timestamps = [x for x in last_requests_timestamps if x in short_time_limit or x in long_time_limit]
    if len(short_time_limit) >= 20:
        result = (timedelta(seconds=1)-(now - short_time_limit[0])).total_seconds()
    elif len(long_time_limit) >= 100:
        long_time_waiting_time = (timedelta(minutes=2)-(now - long_time_limit[0])).total_seconds()
        if long_time_waiting_time > result:
            result = long_time_waiting_time
    return result


def make_request(url):
    time.sleep(time_to_wait())
    last_requests_timestamps.append(datetime.utcnow())
    return requests.get(url)


def get_json_from_url(url):
    r = make_request(url)
    while r.status_code != 200:
        if r.status_code in time_response_codes:
            r = make_request(url)
        else:
            if r.status_code == 404:
                return {'matches': [], 'endIndex': 0, 'totalGames': 0}
            raise Exception('Can not handle response code: ', r.text)
    return json.loads(r.text)


def get_account_id_for_name(name, region):
    summoner_url = '/lol/summoner/v4/summoners/by-name/{}'.format(name) + api_key
    complete_url = api_url.format(url_path=summoner_url, server=get_subdomain_for_region(region))
    return get_json_from_url(complete_url)['accountId']


def get_match_list_batch(account_id, region, begin_index, timestamp=0):
    timestamp_url = ''
    if timestamp > 0:
        timestamp_url = '&beginTime=' + str(int(timestamp))
    matchlist_url = '/lol/match/v4/matchlists/by-account/{}'.format(account_id) + api_key + timestamp_url
    complete_url = api_url.format(url_path=matchlist_url, server=get_subdomain_for_region(region)) + '&beginIndex={}'.format(begin_index)
    return get_json_from_url(complete_url)


def get_match_list_for_account(account_id, region, timestamp=0):
    result, start_index = [], 0
    response = get_match_list_batch(account_id, region, 0, timestamp)
    result.extend(response['matches'])
    while response['endIndex'] < response['totalGames']:
        start_index = response['endIndex']
        response = get_match_list_batch(account_id, region, start_index, timestamp)
        result.extend(response['matches'])
    return result


def get_match_for_match_id(match_id, region):
    match_url = '/lol/match/v4/matches/{}'.format(match_id) + api_key
    complete_url = api_url.format(url_path=match_url, server=get_subdomain_for_region(region))
    return get_json_from_url(complete_url)


def get_number_of_patches(patch_count):
    patches = json.loads(open('./data_fetcher/json_files/patches.json').read())
    now = datetime.now()
    for i in range(patch_count, len(patches)):
        if datetime.strptime(patches[i]['date'], "%d. %B %Y") > now:
            return patches[i - patch_count]
    return patches[-1]


def get_timestamp_for_last_number_of_patches(number_of_patches):
    raw_date = get_number_of_patches(number_of_patches)['date']
    patch_as_datetime = datetime.strptime(raw_date, "%d. %B %Y") + timedelta(hours=6)
    return patch_as_datetime.timestamp() * 1000


def get_matchlist_for_player_since_number_of_patches(accound_id, patch_count):
    #todo only ranked!
    timestamp = int(get_timestamp_for_last_number_of_patches(patch_count))
    return get_match_list_for_account(account_id, region, timestamp)


def get_number_of_patches(patch_count):
	patches = json.loads(open('./patches.json').read())
	now = datetime.now()
	for i in range(patch_count, len(patches)):
		if datetime.strptime(patches[i]['date'], "%d. %B %Y") > now:
			return patches[i - patch_count]
	return patches[-1]


def get_timestamp_for_last_number_of_patches(number_of_patches):
	raw_date = get_number_of_patches(number_of_patches)['date']
	patch_as_datetime = datetime.strptime(raw_date, "%d. %B %Y") + timedelta(hours=6)
	return patch_as_datetime.timestamp()


subdomain = 'euw1'
account_id = get_account_id_for_name('bigmcjoe', subdomain)
matchlist = get_full_match_list_for_account(account_id, subdomain)
match = get_match_for_match_id(matchlist[0]['gameId'], server=subdomain)
current_patch = get_timestamp_for_last_number_of_patches(3)
print(current_patch)
