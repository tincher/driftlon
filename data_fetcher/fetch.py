import argparse
import logging
from datetime import datetime
from get_from_db import DBReader
from write_to_db import DBWriter
from data_fetcher.api_layers.leaguepedia_layer import LPLayer
from data_fetcher.api_layers.trackingthepros_layer import TTPLayer
from data_fetcher.api_layers.riot_layer import RiotLayer
from tqdm import tqdm
import yaml

mongo_config = yaml.safe_load(open('/config.yml', 'r'))['mongodb']
db_writer = DBWriter(mongo_config['address'], mongo_config['username'], mongo_config['password'])
db_reader = DBReader(mongo_config['address'], mongo_config['username'], mongo_config['password'])
lp_layer = LPLayer()
ttp_layer = TTPLayer()
riot_layer = RiotLayer()


def fetch_pros(batch_size=0):
    logging.info(f'FETCH: fetching pros - batch_size: {batch_size}')
    players = lp_layer.get_all_eligible_players()
    if batch_size > 0:
        players = players[:batch_size]
    for player in tqdm(players):
        player['soloq_ids'] = ttp_layer.get_soloq_ids(player['name'])
        if player['soloq_ids'] is not None:
            for soloq_id in player['soloq_ids']:
                soloq_id['account_id'] = riot_layer.get_account_id_for_name(soloq_id['account_name'],
                                                                            soloq_id['server'])
                if soloq_id['account_id'] is None: continue
                soloq_id['ranking'] = riot_layer.get_rank_for_account_id(soloq_id['account_id']['id'],
                                                                         soloq_id['server'])
                soloq_id['ranking']['last_checked'] = datetime.utcnow()
        db_writer.write_user(player)


def fetch_games_for_oldest_batch(batch_size=20, max_nr=30):
    logging.info(f'FETCH: fetching games for oldest - batch_size: {batch_size}')
    players = db_reader.get_oldest_updated_batch_of_players(batch_size)
    for player in tqdm(players):
        for soloq_id in player['soloq_ids']:
            if soloq_id['account_id'] is not None:
                for match_batch in riot_layer.get_matchlist_for_player_since_number_of_patches(
                        soloq_id['account_id']['puuid'], soloq_id['server'], 1, max_nr):
                    for match in match_batch:
                        result = riot_layer.get_match_for_match_id(match, soloq_id['server'])
                        if result is not None:
                            db_writer.write_game(result, player)
        db_writer.update_user_timestamp(player)


def fetch_casuals(config_number):
    logging.info(f'FETCH: fetching casuals - config: {config_number}')
    configs = [{
        'tier': 'challenger',
        'division': ''
    }, {
        'tier': 'grandmaster',
        'division': ''
    }, {
        'tier': 'master',
        'division': ''
    }, {
        'tier': 'DIAMOND',
        'division': 'I'
    }, {
        'tier': 'DIAMOND',
        'division': 'II'
    }]
    queue = 'RANKED_SOLO_5x5'
    subdomain = 'euw1'
    for player in tqdm(
            riot_layer.get_players_from_division(queue, configs[config_number]['tier'],
                                                 configs[config_number]['division'], subdomain)):
        db_writer.write_user(player)


def main(args):
    logging.basicConfig(filename='/var/log/driftlon/driftlon.log', level=logging.DEBUG,
                        format='%(asctime)s %(message)s')
    logging.info(f'start fetching - {args}')
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
    parser.add_argument('--type', type=str, help='What do you want to fetch? (games, pros, casuals)')
    parser.add_argument('--batch_size', type=int, default=0, help='What is the batch size?')
    parser.add_argument('--config', type=int, default=1, help='What config type for casuals? (0-4)')
    args = parser.parse_args()
    if main(args) == False:
        parser.print_help()
