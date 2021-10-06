from torch.utils.data import Dataset
import sys
import numpy as np
sys.path.append('..')
from driftlon_utils import get_connection_for_collection_name

class DriftlonDataset(Dataset):
    def __init__(self, match_count=10, classification_target=True, mongo_config=None):
        self.match_count = match_count
        self.classification_target = classification_target
        self.db, self.processed_collection = get_connection_for_collection_name('processed_matches', mongo_config['address'], mongo_config['username'], mongo_config['password'])
        
        values = [x.values() for x in self.processed_collection.find({})]
        _, self.game_data, self.pro_game_counts, self.timestamps, self.playerids = list(zip(*values))        
    
    def __len__(self):
        return len(self.pro_game_counts)
        
        
    def __getitem__(self, idx):
        result = self.game_data[idx]
        return result
