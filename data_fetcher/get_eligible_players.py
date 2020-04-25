import mwclient
import json
import html
import requests
from bs4 import BeautifulSoup

top_leagues = ["LoL European Championship", "League Championship Series", "LoL Champions Korea", "LoL Pro League"]

site = mwclient.Site('lol.gamepedia.com', path='/')
min_games = 20


def get_eligible_players():
	response = site.api('cargoquery', limit='max', tables="PlayerLeagueHistory=PLH",
						fields="PLH.TotalGames, PLH.Player, PLH.League", order_by="PLH.TotalGames desc",
						where="PLH.TotalGames>={}".format(min_games))
	return response["cargoquery"]


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
	while element is not None:
		if element.has_attr('class') and 'inactive_account' in element['class']:
			element = element.next_sibling
			continue
		if element.has_attr('id') and 'inactive_link' in element['id']:
			break
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


players = get_eligible_players()
print(get_soloq_ids_from_trackingthepros('PerkZ'))
