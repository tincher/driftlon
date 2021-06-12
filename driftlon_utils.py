# flatten dict
def flatten_dict(d, sep='_'):
    obj = collections.OrderedDict()

    def recurse(t, parent_key=''):
        if isinstance(t, list):
            for i in range(len(t)):
                recurse(t[i], parent_key + sep + str(i) if parent_key else str(i))
        elif isinstance(t, dict):
            for k, v in t.items():
                recurse(v, parent_key + sep + k if parent_key else k)
        else:
            obj[parent_key] = t
    recurse(d)
    return obj


# db
def get_connection_for_collection_name(collection_name, ip='localhost'):
    db = pymongo.MongoClient('mongodb://{}:27017'.format(ip))
    return db, db['driftlon'][collection_name]

def get_particpant_id(match):
	participant_id = 0
	player = DBReader.get_player_for_id(match['player_id'])
	player_account_ids = []
	player_account_ids = [x['account_id']['accountId'] for x in player['soloq_ids'] if x['account_id'] is not None]
	for participant in match['data']['participantIdentities']:
		if participant['player']['accountId'] in player_account_ids:
			participant_id = participant['participantId']
	return participant_id
