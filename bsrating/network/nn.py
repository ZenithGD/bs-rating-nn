import torch
import torch.nn as nn
from torch.nn.utils.rnn import pad_sequence

from bsrating.game.element import ElementType
from bsrating.network.pos_encoding import PositionalEncoding

class RatingPredictorNN(nn.Module):
    def __init__(self, token_dim, model_dim=128, heads=4, attn_layers=3):
        super().__init__()

        # project tokens into the latent space
        self.token_embed = nn.Linear(token_dim, model_dim)
        self.type_embed = nn.Embedding(5, model_dim, padding_idx=ElementType.Other)
        self.pos_encoder = PositionalEncoding(model_dim) 

        # encoder
        encoder_layer = nn.TransformerEncoderLayer(model_dim, heads, batch_first=True)
        self.transformer = nn.TransformerEncoder(encoder_layer, num_layers=attn_layers)

        self.pool = nn.Linear(model_dim, 1)
        
        self.out = nn.Linear(model_dim, 1)

    def forward(self, feats, type_ids, pad_mask):

        # add type and token information
        x = self.token_embed(feats) + self.type_embed(type_ids)

        # add positional encoding information
        x = self.pos_encoder(x)

        # predict scores and pool
        x = self.transformer(x)
        scores = self.pool(x).squeeze(-1)

        # handle padding and compute attention
        scores = scores.masked_fill(pad_mask, -1e9)
        weights = torch.softmax(scores, dim=-1)

        # aggregate values and attention
        pooled = torch.sum(weights.unsqueeze(-1) * x, dim=1)

        # predict rating
        return self.out(pooled).squeeze(-1)