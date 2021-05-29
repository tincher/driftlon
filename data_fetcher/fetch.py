import argparse
import logging
import sys
from datetime import datetime
from get_from_db import *
from write_to_db import DBWriter
from data_fetcher.api_layers.leaguepedia_layer import LPLayer
from data_fetcher.api_layers.trackingthepros_layer import TTPLayer
from data_fetcher.api_layers.riot_layer import RiotLayer
from tqdm import tqdm

batch_size = 20
patch_count = 2
top_leagues = ['LoL European Championship', 'League Championship Series', 'LoL Champions Korea', 'LoL Pro League']
DBWriter = DBWriter()
DBReader = DBReader()
LPLayer = LPLayer()
TTPLayer = TTPLayer()
RiotLayer = RiotLayer()


def fetch_pros(batch_size=0):
    logging.info('FETCH: fetching pros - batch_size: {}'.format(batch_size))
    players = LPLayer.get_all_eligible_players()
    if batch_size > 0:
        players = players[:batch_size]
    for player in tqdm(players):
        player['soloq_ids'] = TTPLayer.get_soloq_ids(player['name'])
        if player['soloq_ids'] is not None:
            for soloq_id in player['soloq_ids']:
                soloq_id['account_id'] = RiotLayer.get_account_id_for_name(soloq_id['account_name'], soloq_id['server'])
                if soloq_id['account_id'] is None: continue
                soloq_id['ranking'] = RiotLayer.get_rank_for_account_id(soloq_id['account_id']['id'], soloq_id['server'])
                soloq_id['ranking']['last_checked'] = datetime.utcnow()
        DBWriter.write_user(player)


def fetch_games_for_oldest_batch(batch_size=20):
    logging.info('FETCH: fetching games for oldest - batch_size: {}'.format(batch_size))
    players = DBReader.get_oldest_updated_batch_of_players(batch_size)
    for player in tqdm(players):
        for soloq_id in player['soloq_ids']:
            if soloq_id['account_id'] is not None:
                for match_batch in RiotLayer.get_matchlist_for_player_since_number_of_patches(soloq_id['account_id']['accountId'], soloq_id['server'], 1):
                    for match in match_batch:
                        result = RiotLayer.get_match_for_match_id(match['gameId'], soloq_id['server'])
                        if result is not None:
                            DBWriter.write_game(result, player)
        DBWriter.update_user_timestamp(player)

def fetch_casuals(config_number):
    logging.info('FETCH: fetching casuals - config: {}'.format(config_number))
    configs = [{'tier': 'challenger', 'division': ''}, {'tier': 'grandmaster', 'division': ''}, {'tier': 'master', 'division': ''}, {'tier': 'DIAMOND', 'division': 'I'}, {'tier': 'DIAMOND', 'division': 'II'}]
    queue ='RANKED_SOLO_5x5'
    subdomain = 'euw1'
    for player in tqdm(RiotLayer.get_players_from_division(queue, configs[config_number]['tier'], configs[config_number]['division'], subdomain)):
        DBWriter.write_user(player)


def main(args):

    logging.basicConfig(filename='/var/log/driftlon/driftlon.log',level=logging.DEBUG, format='%(asctime)s %(message)s')
    logging.info('start fetching - {}'.format(args))
    if args.type == 'pros':
        fetch_pros(args.batch_size)
    elif args.type == 'casuals':
        fetch_casuals(args.config)
    elif args.type == 'games':
        fetch_games_for_oldest_batch(args.batch_size)
    else:
        return False


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--type', type=str ,help='What do you want to fetch? (games, pros, casuals)')
    parser.add_argument('--batch_size', type=int, default=0, help='What is the batch size?')
    parser.add_argument('--config', type=int, default=1,  help='What config type for casuals? (0-4)')
    args = parser.parse_args()
    if main(args) == False:
        parser.print_help()
