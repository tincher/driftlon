import html
import json
import random

import mwclient
import requests
from bs4 import BeautifulSoup

top_leagues = {
    "LoL European Championship": 'LEC',
    "League Championship Series": 'LCS',
    "LoL Champions Korea": 'LCK',
    "LoL Pro League": 'LPL'}

site = mwclient.Site('lol.gamepedia.com', path='/')
min_games = 20


# helper? todo
def get_abbreviated_league_player(player):
    player['league'] = top_leagues[player['league']]
    return player


def get_abbreviated_league_player(player):
    player['league'] = top_leagues[player['league']]
    return player


def get_next_player_batch(current_offset):
    request = site.api('cargoquery', offset=current_offset, limit=500, tables="PlayerLeagueHistory=PLH",
                       fields="PLH.TotalGames, PLH.Player, PLH.League", order_by="PLH.TotalGames desc",
                       where="PLH.TotalGames>={}".format(min_games))
    result = []
    for entry in request['cargoquery']:
        player = {'pro_games': entry['title']['TotalGames'],
                  'name': entry['title']['Player'],
                  'league': entry['title']['League']}
        result.append(player)
    result = list(filter(lambda x: x['league'] in top_leagues.keys(), result))
    result = list(map(get_abbreviated_league_player, result))
    return result


def get_all_eligible_players():
    current_offset = 0
    result = []
    player_batch = get_next_player_batch(current_offset)
    while len(player_batch) > 0:
        result.extend(player_batch)
        current_offset += 500
        player_batch = get_next_player_batch(current_offset)
    return result


def get_soloq_ids_from_trackingthepros(name):
    result = []
    r = requests.get('https://www.trackingthepros.com/player/{}'.format(name))
    if 'players' in r.url:
        return None
    soup = BeautifulSoup(r.text, features="lxml")
    inner_info = soup.find_all("div", class_="player-info-inner")
    card = [x for x in inner_info if x.find("h4", text='Accounts') is not None][0]
    table = card.find("table")
    element = table.find("tr")
    while element is not None and not (element.has_attr('id') and 'inactive_link' in element['id']):
        if element.has_attr('class') and 'inactive_account' in element['class']:
            element = element.next_sibling
            continue
        td = element.find("td")
        server = td.find("b").getText().strip()
        account_name = td.getText().split("]")[-1].strip()
        result.append({'server': server, 'account_name': account_name})
        element = element.next_sibling
    return result


def get_soloq_ids_from_leaguepedie(name):
    response = site.api('cargoquery', tables="Players=P", fields="P.ID, P.SoloqueueIds, P.IsRetired",
                        where="P.ID='{}'".format(name))
    response['cargoquery'] = json.loads(html.unescape(json.dumps(response['cargoquery'])))
    return response['cargoquery']


def get_random_batch_of_players(batch_size):
    all_players = get_all_eligible_players()
    random.shuffle(all_players)
    return all_players[:batch_size]

# players = get_all_eligible_players()
# print(get_soloq_ids_from_trackingthepros('PerkZ'))
