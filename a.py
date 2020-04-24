import mwclient
import json
site = mwclient.Site('lol.gamepedia.com', path='/')
response = site.api('cargoquery',
                    tables="Players=P", fields="P.ID, P.SoloqueueIds",
                    where="P.ID='Zven'")
print(json.dumps(response))
