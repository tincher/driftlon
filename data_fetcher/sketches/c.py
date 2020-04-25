import mwclient
import json
site = mwclient.Site('lol.gamepedia.com', path='/')
response = site.api('cargoquery', limit='max',
                    tables="PlayerLeagueHistory=PLH", fields="PLH.TotalGames, PLH.Player, PLH.League",
                    order_by="PLH.TotalGames desc", where="PLH.Player='Langx'")
print(json.dumps(response))
