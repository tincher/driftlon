import os
import yaml
import json
import time
import getpass
import logging
import requests
import platform
from datetime import datetime, timedelta


class RiotLayer:
    def __init__(self):
        with open('/config.yml', 'r') as configfile:
            self.config = yaml.safe_load(configfile)

        self.api_key = 'api_key=' + self.config['riot']['api_key']
        self.api_url = 'https://{server}.api.riotgames.com{url_path}'

        self.last_requests_timestamps = []
        self.time_response_codes = [429, 504]

    def time_to_wait(self):
        result = 0
        now = datetime.utcnow()
        short_time_limit = [x for x in self.last_requests_timestamps if x + timedelta(seconds=1) >= now]
        long_time_limit = [x for x in self.last_requests_timestamps if x + timedelta(minutes=2) >= now]
        self.last_requests_timestamps = [
            x for x in self.last_requests_timestamps if x in short_time_limit or x in long_time_limit
        ]
        if len(short_time_limit) >= 20:
            result = (timedelta(seconds=1) - (now - short_time_limit[0])).total_seconds()
        elif len(long_time_limit) >= 100:
            long_time_waiting_time = (timedelta(minutes=2) - (now - long_time_limit[0])).total_seconds()
            if long_time_waiting_time > result:
                result = long_time_waiting_time
        result += 0.01
        logging.debug('RIOT: waiting - seconds: {result}')
        return result

    def make_request(self, url):
        time.sleep(self.time_to_wait())
        self.last_requests_timestamps.append(datetime.utcnow())
        return requests.get(url)

    def get_json_from_url(self, url):
        r = self.make_request(url)
        while r.status_code != 200:
            if r.status_code in self.time_response_codes:
                r = self.make_request(url)
            else:
                if r.status_code == 404:
                    return None
                logging.error(f'RIOT: can not handle response code: {r.status_code} - {r.text}')
                raise Exception('Can not handle response code! Text: ', r.text)
        return json.loads(r.text)

    def generate_url(self, subdomain, endpoint_url, *request_values):
        generated_url = endpoint_url.format(*request_values, self.api_key)
        return self.api_url.format(server=subdomain, url_path=generated_url)

    def get_account_id_for_name(self, name, subdomain):
        complete_url = self.generate_url(subdomain, '/lol/summoner/v4/summoners/by-name/{}?{}', name)
        result = self.get_json_from_url(complete_url)
        if result is None:
            logging.warning(f'RIOT: accountId not found - name: {name} - {subdomain}')
            return None
        elif 'accountId' not in result.keys():
            logging.warning(f'RIOT: accountId not found - name: {name} - {subdomain}')
            return None
        else:
            logging.debug(f'RIOT: accountId - name: {name} - {subdomain}')
            return result

    def get_rank_for_account_id(self, account_id, subdomain, queue='RANKED_SOLO_5x5'):
        complete_url = self.generate_url(subdomain, '/lol/league/v4/entries/by-summoner/{}?{}', account_id)
        result = self.get_json_from_url(complete_url)
        rank = list(filter(lambda x: x['queueType'] == queue, result))
        logging.info(f'RIOT: rank - accountId: {account_id} - subdomain: {subdomain} - queue: {queue} - rank: {rank}')
        if len(rank) > 0:
            return rank[0]
        else:
            return {'tier': 'unranked', 'rank': 'unranked'}

    def get_match_list_batch(self, account_id, subdomain, begin_index, timestamp=0, queues=[420, 440], end_index=0):
        timestamp_url = ''
        if timestamp > 0:
            timestamp_url = '&beginTime=' + str(int(timestamp))
        queues_url = ''
        for queue in queues:
            queues_url += '&queue=' + str(queue)
        begin_url = f'beginIndex={begin_index}'
        endindex_url = 'endIndex={}'.format(end_index if (end_index -
                                                          begin_index) <= 100 else 100) if end_index != 0 else ''
        complete_url = self.generate_url(subdomain, '/lol/match/v4/matchlists/by-account/{}?{}{}{}&{}&{}', account_id,
                                         begin_url, timestamp_url, queues_url, endindex_url)
        result = self.get_json_from_url(complete_url)
        return result

    def get_match_list_for_account(self, account_id, region, timestamp=0, queues=[420, 440], end_index=0):
        result, start_index = [], 0
        response = self.get_match_list_batch(account_id, region, 0, timestamp, queues, end_index)
        if response is None:
            return []
        yield response['matches']
        while response['endIndex'] < response['totalGames']:
            start_index = response['endIndex']
            response = self.get_match_list_batch(account_id, region, start_index, timestamp, queues)
            yield response['matches']
        logging.info(
            f'RIOT: match list - name: {account_id} - timestamp: {timestamp} - length: {response["totalGames"]}')

    def get_match_for_match_id(self, match_id, subdomain):
        complete_url = self.generate_url(subdomain, '/lol/match/v4/matches/{}?{}', match_id)
        result = self.get_json_from_url(complete_url)
        if 'gameId' not in result.keys():
            logging.warning(f'RIOT: gameId not found - match id: {match_id} - {subdomain} - keys: {result.keys()}')
            return None
        logging.info(f'RIOT: match - match id: {match_id} - {subdomain} - gameId: {result["gameId"]}')
        return result

    def get_timestamp_for_last_number_of_patches(self, number_of_patches):
        raw_date = self.get_number_of_patches(number_of_patches)['date']
        patch_as_datetime = datetime.strptime(raw_date, '%d. %B %Y') + timedelta(hours=6)
        return patch_as_datetime.timestamp() * 1000

    def get_matchlist_for_player_since_number_of_patches(self, account_id, region, patch_count, max_nr=0):
        timestamp = int(self.get_timestamp_for_last_number_of_patches(patch_count))
        for i, match_list_batch in enumerate(
                self.get_match_list_for_account(account_id, region, timestamp, end_index=max_nr)):
            yield match_list_batch
            logging.info(
                f'RIOT: matches - account id: {account_id} - {region} - #patches: {patch_count} - batch_no: {i}')

    def get_players_from_higher_tier(self, queue, tier, subdomain):
        complete_url = self.generate_url(subdomain, '/lol/league/v4/{}leagues/by-queue/{}?{}', tier, queue)
        result = self.get_json_from_url(complete_url)['entries']
        logging.info(
            f'RIOT: players (higher tier) - tier {tier} - {subdomain} - queue: {queue}- #players: {len(result)}')
        return result

    def get_all_players_from_division(self, tier, division, subdomain, queue, page_limit=1):
        result, page_count = [], 1
        next_batch = self.get_player_page_from_division(queue, tier, division, subdomain, page_count)
        while len(next_batch) > 0 and page_count <= page_limit:
            page_count += 1
            result.extend(next_batch)
            next_batch = self.get_player_page_from_division(queue, tier, division, subdomain, page_count)
        logging.info(
            f'RIOT: players (lower tier) - tier {tier} {division} - {subdomain} - queue: {queue} - #players: {len(result)}'
        )
        return result

    def get_player_page_from_division(self, queue, tier, division, subdomain, page):
        complete_url = self.generate_url(subdomain, '/lol/league/v4/entries/{}/{}/{}?page={}&{}', queue, tier, division,
                                         page)
        result = self.get_json_from_url(complete_url)
        return result

    def get_players_from_division(self, queue, tier, division, subdomain):
        players = []
        if tier in ['master', 'challenger', 'grandmaster']:
            players = self.get_players_from_higher_tier(queue, tier, subdomain)
        else:
            players = self.get_all_players_from_division(tier, division, subdomain, queue)
        for player in players:
            player_dto = {}
            soloq_ids = [{
                'account_id': self.get_account_id_for_name(player['summonerName'], subdomain),
                'server': subdomain,
                'account_name': player['summonerName']
            }]
            if soloq_ids[0]['account_id'] is None:
                continue
            soloq_ids[0]['ranking'] = self.get_rank_for_account_id(soloq_ids[0]['account_id']['id'],
                                                                   soloq_ids[0]['server'])
            soloq_ids[0]['ranking']['last_checked'] = datetime.utcnow()
            player_dto['soloq_ids'] = soloq_ids
            player_dto['name'] = player['summonerName']
            player_dto['pro_games'] = 0
            yield player_dto

    @staticmethod
    def get_number_of_patches(patch_count):
        patches = json.loads(open('/data_fetcher/json_files/patches.json').read())
        now = datetime.now()
        for i in range(patch_count, len(patches)):
            if datetime.strptime(patches[i]['date'], '%d. %B %Y') > now:
                return patches[i - patch_count]
