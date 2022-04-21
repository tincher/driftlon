import json
from datetime import datetime, timedelta
import time

import requests

api_key = '?api_key=RGAPI-a35c93a9-3dc3-42da-8846-3149295755d7'
api_url = 'https://{server}.api.riotgames.com{url_path}'

subdomains = {'[NA]': 'na1', '[EU]': 'euw1', '[EUW]': 'euw1', '[KR]': 'kr', '[EUNE]': 'eun1'}


def get_subdomain_for_region(region):
    return subdomains[region]


def get_json_from_url(url):
    # todo ratelimit_control
    time_response_codes = [429, 504]
    r = requests.get(url)
    is_first_time = True
    while r.status_code != 200:
        if r.status_code in time_response_codes:
            if is_first_time:
                time.sleep(1)
            else:
                time.sleep(20)
            r = requests.get(url)
        else:
            if r.status_code == 404:
                return {'matches': [], 'endIndex': 0, 'totalGames': 0}
            raise Exception('Can not handle response code: ', r.text)
    return json.loads(r.text)


def get_account_id_for_name(name, region):
    summoner_url = f'/lol/summoner/v4/summoners/by-name/{name}{api_key}'
    complete_url = api_url.format(url_path=summoner_url, server=get_subdomain_for_region(region))
    return get_json_from_url(complete_url)['accountId']


def get_match_list_batch(account_id, region, begin_index, timestamp=0):
    timestamp_url = ''
    if timestamp > 0:
        timestamp_url = '&beginTime=' + str(int(timestamp))
    matchlist_url = f'/lol/match/v4/matchlists/by-account/{account_id}{api_key}{timestamp_url}'
    complete_url = api_url.format(url_path=matchlist_url,
                                  server=get_subdomain_for_region(region)) + '&beginIndex={begin_index}'
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


def get_full_match_list_for_account(account_id, region, timestamp=0):
    result, start_index = [], 0
    response = get_match_list_batch(account_id, region, 0, timestamp)
    result.extend(response['matches'])
    while response['endIndex'] < response['totalGames']:
        start_index = response['endIndex']
        response = get_match_list_batch(account_id, region, start_index, timestamp)
        result.extend(response['matches'])
    return result


def get_match_for_match_id(match_id, region):
    match_url = f'/lol/match/v4/matches/{match_id}{api_key}'
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


def get_matchlist_for_player_since_number_of_patches(name, region, patch_count):
    timestamp = int(get_timestamp_for_last_number_of_patches(patch_count))
    account_id = get_account_id_for_name(name, region)
    return get_full_match_list_for_account(account_id, region, timestamp)


if __name__ == '__main__':
    subdomain = '[EU]'
    account_id = get_account_id_for_name('bigmcjoe', subdomain)
    matchlist = get_full_match_list_for_account(account_id, subdomain)
    match = get_match_for_match_id(matchlist[11]['gameId'], server=subdomain)
    current_patch = get_timestamp_for_last_number_of_patches(3)
    my_matchlist = get_matchlist_for_player_since_number_of_patches('bigmcjoe', subdomain, 2)
    print(json.dumps(my_matchlist))
