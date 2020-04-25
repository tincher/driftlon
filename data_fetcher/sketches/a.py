import mwclient
import json
site = mwclient.Site('lol.gamepedia.com', path='/')
name = 'Bjergsen'
where = "P.ID='{}'".format(name)
response = site.api('cargoquery',
                    tables="Players=P", fields="P.ID, P.SoloqueueIds, P.IsRetired",
                    where=where)
print(json.dumps(response))
