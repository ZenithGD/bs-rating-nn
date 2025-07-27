import json
from pprint import pprint
import torch
from torch.nn.utils.rnn import pad_sequence

from bsrating.game.element import ElementType
from torch.utils.data import Dataset, DataLoader

class MapDataset(Dataset):

    def __init__(self, filepaths):
        self.filepaths = filepaths

    def __len__(self):
        return len(self.filepaths)
    
    def __getitem__(self, idx : int) -> tuple[torch.tensor, torch.tensor, torch.tensor]:
        """Load the map at some index from the dataset. It will convert the map to 
        a sequence of tokens, and returns both the input (map) and output (rating)

        Args:
            idx (int): The index of the map to load

        Returns:
            (torch.tensor, torch.tensor, torch.float32): The type and data of the tokens, 
                along with its rating, everything as a tensor
        """
        filepath = self.filepaths[idx]
        with open(filepath) as fp:
            data = json.load(fp)

        def format_token(tok: dict):
            return [
                tok.get("type", 0),
                tok.get("time", 0),
                tok.get("x", 0),
                tok.get("y", 0),
                tok.get("angle", 0),
                1 if tok.get("any_dir", False) else 0,
                tok.get("w", 0),
                tok.get("h", 0),
                tok.get("duration", 0),
                tok.get("njs", 0)
            ], tok.get("type", 0)

        formatted_toks = list(zip(*[ format_token(tok) for tok in data["data"] ]))
        
        rating = torch.tensor(data["rating"], dtype=torch.float32)
        tokens = torch.tensor(formatted_toks[0], dtype=torch.float32)
        type_id = torch.tensor(formatted_toks[1], dtype=torch.long)

        return tokens, type_id, rating

def collate_fn(batch):
    tokens, type_id, ratings = zip(*batch)

    # Pad the tokens (shape: [batch, seq_len, feature_dim])
    padded_tokens = pad_sequence(tokens, batch_first=True)  # tokens are [seq_len, feature_dim]

    # Pad the type IDs (shape: [batch, seq_len])
    padded_type_id = pad_sequence(type_id, batch_first=True, padding_value=ElementType.Other)

    # Create the padding mask: True where the type is padding
    padding_mask = padded_type_id == ElementType.Other

    return padded_tokens, padded_type_id, torch.stack(ratings), padding_mask