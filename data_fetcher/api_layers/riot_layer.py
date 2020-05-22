import time

import requests
import yaml


class RiotLayer:
    def __init__(self):
        with open('./data_fetcher/api_layers/config.yml', 'r') as configfile:
            self.config = yaml.safe_load(configfile)

        self.api_key = '?api_key=' + config['riot']['api_key']
        self.api_url = 'https://{server}.api.riotgames.com{url_path}'

        self.last_requests_timestamps = []
        self.time_response_codes = [429, 504]

    def time_to_wait(self):
        result = 0
        now = datetime.utcnow()
        short_time_limit = [x for x in self.last_requests_timestamps if x + timedelta(seconds=1) > now]
        long_time_limit = [x for x in self.last_requests_timestamps if x + timedelta(minutes=2) > now]
        self.last_requests_timestamps = [
            x for x in self.last_requests_timestamps if x in short_time_limit or x in long_time_limit]
        if len(short_time_limit) >= 20:
            result = (timedelta(seconds=1) - (now - short_time_limit[0])).total_seconds()
        elif len(long_time_limit) >= 100:
            long_time_waiting_time = (timedelta(minutes=2) - (now - long_time_limit[0])).total_seconds()
            if long_time_waiting_time > result:
                result = long_time_waiting_time
        return result

    def make_request(self, url):
        time.sleep(time_to_wait())
        self.last_requests_timestamps.append(datetime.utcnow())
        return requests.get(url)

    # todo rename to make request
    def get_json_from_url(self, url):
        r = self.make_request(url)
        while r.status_code != 200:
            if r.status_code in self.time_response_codes:
                r = self.make_request(url)
            else:
                if r.status_code == 404:
                    return {'matches': [], 'endIndex': 0, 'totalGames': 0}
                raise Exception('Can not handle response code: ', r.text)
        return json.loads(r.text)

    def get_account_id_for_name(self, name, region):
        summoner_url = '/lol/summoner/v4/summoners/by-name/{}'.format(name) + self.api_key
        complete_url = self.api_url.format(url_path=summoner_url, server=get_subdomain_for_region(region))
        return self.get_json_from_url(complete_url)['accountId']

    def get_match_list_batch(self, account_id, subdomain, begin_index, timestamp=0, queues=[420, 440]):
        timestamp_url = ''
        if timestamp > 0:
            timestamp_url = '&beginTime=' + str(int(timestamp))
        queues_url = ''
        for queue in queues:
            queues_url = '&queue=' + str(queue)
        matchlist_url = '/lol/match/v4/matchlists/by-account/{}'.format(account_id) + self.api_key + timestamp_url
        complete_url = self.api_url.format(url_path=matchlist_url, server=subdomain) + \
            '&beginIndex={}'.format(begin_index)
        return self.get_json_from_url(complete_url)

    def get_match_list_for_account(self, account_id, region, timestamp=0, queues=[420, 440]):
        result, start_index = [], 0
        response = self.get_match_list_batch(account_id, region, 0, timestamp, queues)
        result.extend(response['matches'])
        while response['endIndex'] < response['totalGames']:
            start_index = response['endIndex']
            response = self.get_match_list_batch(account_id, region, start_index, timestamp, queues)
            result.extend(response['matches'])
        return result

    def get_match_for_match_id(self, match_id, subdomain):
        match_url = '/lol/match/v4/matches/{}'.format(match_id) + self.api_key
        complete_url = self.api_url.format(url_path=match_url, server=subdomain)
        return self.get_json_from_url(complete_url)

    def get_timestamp_for_last_number_of_patches(self, number_of_patches):
        raw_date = self.get_number_of_patches(number_of_patches)['date']
        patch_as_datetime = datetime.strptime(raw_date, "%d. %B %Y") + timedelta(hours=6)
        return patch_as_datetime.timestamp() * 1000

    def get_matchlist_for_player_since_number_of_patches(self, account_id, region, patch_count):
        timestamp = int(self.get_timestamp_for_last_number_of_patches(patch_count))
        return self.get_match_list_for_account(account_id, region, timestamp)

    def get_players_from_division(self, division, tier, queue, subdomain):
        division = '/lol/league/v4/entries/{}/{}/{}'.format(queue, tier, divison) + self.api_key
        complete_url = self.api_url.format(url_path=match_url, server=subdomain)
        return self.get_json_from_url(complete_url)

    @staticmethod
    def get_number_of_patches(patch_count):
        patches = json.loads(open('./data_fetcher/json_files/patches.json').read())
        now = datetime.now()
        for i in range(patch_count, len(patches)):
            if datetime.strptime(patches[i]['date'], "%d. %B %Y") > now:
                return patches[i - patch_count]
                return patches[-1]
