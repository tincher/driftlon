import html
import json
import random
import logging
import mwclient


class LPLayer:
    def __init__(self):
        self.site = mwclient.Site('lol.fandom.com', path='/')
        self.min_games = 20
        self.top_leagues = {
            'LoL European Championship': 'LEC',
            'League Championship Series': 'LCS',
            'LoL Champions Korea': 'LCK',
            'LoL Pro League': 'LPL'
        }

    def get_abbreviated_league_player(self, player):
        player['league'] = self.top_leagues[player['league']]
        return player

    def get_next_player_batch(self, current_offset):
        request = self.site.api('cargoquery', offset=current_offset, limit=500, tables='PlayerLeagueHistory=PLH',
                                fields='PLH.TotalGames, PLH.Player, PLH.League', order_by='PLH.TotalGames desc',
                                where=f'PLH.TotalGames>={self.min_games}')
        result = []
        for entry in request['cargoquery']:
            player = {
                'pro_games': entry['title']['TotalGames'],
                'name': entry['title']['Player'],
                'league': entry['title']['League']
            }
            result.append(player)
        result = list(filter(lambda x: x['league'] in self.top_leagues.keys(), result))
        result = list(map(self.get_abbreviated_league_player, result))
        return result

    def get_all_eligible_players(self):
        current_offset = 0
        result = []
        player_batch = self.get_next_player_batch(current_offset)
        while len(player_batch) > 0:
            result.extend(player_batch)
            current_offset += 500
            player_batch = self.get_next_player_batch(current_offset)
        logging.info(f'LP: #eligible players: {len(result)}')
        return result

    def get_soloq_ids(self, name):
        response = self.site.api('cargoquery', tables='Players=P', fields='P.ID, P.SoloqueueIds, P.IsRetired',
                                 where=f'P.ID=\'{name}\'')
        response['cargoquery'] = json.loads(html.unescape(json.dumps(response['cargoquery'])))
        logging.debug(f'LP: soloq ids - name: {name} - #: {len(response["cargoquery"])}')
        return response['cargoquery']

    def get_random_batch_of_players(self, batch_size):
        all_players = self.get_all_eligible_players()
        random.shuffle(all_players)
        return all_players[:batch_size]
