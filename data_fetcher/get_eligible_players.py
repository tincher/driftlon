import html
import json

import mwclient
import requests
from bs4 import BeautifulSoup

top_leagues = ["LoL European Championship", "League Championship Series", "LoL Champions Korea", "LoL Pro League"]

site = mwclient.Site('lol.gamepedia.com', path='/')
min_games = 20


def get_next_player_batch(current_offset):
	request = site.api('cargoquery', offset=current_offset, limit=500, tables="PlayerLeagueHistory=PLH",
					   fields="PLH.TotalGames, PLH.Player, PLH.League", order_by="PLH.TotalGames desc",
					   where="PLH.TotalGames>={}".format(min_games))['cargoquery']
	return [(x['title']['TotalGames'], x['title']['Player'], x['title']['League']) for x in request['cargoquery']]


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
		raise Exception("redirect")
	soup = BeautifulSoup(r.text, features="lxml")
	inner_info = soup.find_all("div", class_="player-info-inner")
	card = [x for x in inner_info if x.find("h4", text='Accounts') is not None][0]
	table = card.find("table")
	element = table.find("tr")
	while not (element.has_attr('id') and 'inactive_link' in element['id']):
		if element.has_attr('class') and 'inactive_account' in element['class']:
			element = element.next_sibling
			continue
		td = element.find("td")
		server = td.find("b").getText()
		account_name = td.getText().split("]")[-1]
		result.append((server, account_name))
		element = element.next_sibling
	return result


def get_soloq_ids_from_leaguepedie(name):
	response = site.api('cargoquery', tables="Players=P", fields="P.ID, P.SoloqueueIds, P.IsRetired",
						where="P.ID='{}'".format(name))
	response['cargoquery'] = json.loads(html.unescape(json.dumps(response['cargoquery'])))
	return response['cargoquery']


players = get_all_eligible_players()
print(get_soloq_ids_from_trackingthepros('PerkZ'))
