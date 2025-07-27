import argparse 
import json
from matplotlib import pyplot as plt
import requests
import os, time
from pprint import pprint
from tqdm import tqdm, trange
from bsrating.leveldata import *
from bsrating.network.map_dataset import MapDataset, collate_fn
from bsrating.network.nn import RatingPredictorNN
from bsrating.utils import *

from dotenv import load_dotenv

import traceback

import torch
import torch.nn as nn
import torch.optim as optim
from torch.utils.data import DataLoader

def main(args):
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    # device = torch.device("cpu")
    print("Using device:", device)

    # 1. load dataset
    filepaths = [ os.path.join(args.dataset, fname) for fname in os.listdir(args.dataset) ]
    dataset = MapDataset(filepaths)
    dataloader = DataLoader(dataset, batch_size=2, collate_fn=collate_fn)

    # 2. train network
    model = RatingPredictorNN(
        token_dim=9,
        model_dim=128,
        heads=4,
        attn_layers=3)
    
    model.to(device)
    criterion = nn.GaussianNLLLoss()  # Or GaussianNLLLoss if predicting variance too
    optimizer = optim.Adam(model.parameters(), lr=2e-4)

    losses = []
    epochs = 20
    for epoch in (pbar := tqdm(range(epochs), position=0, desc="Epochs")):
        
        epoch_loss = 0.0
        model.train()

        # take batches from the dataloader and train
        for _, batch in enumerate(tqdm(dataloader, position=1, leave=False, desc="Batch")):
            # pass batch to device
            tokens, type_id, rating, padding_mask = batch
            tokens = tokens.to(device)
            type_id = type_id.to(device)
            rating = rating.to(device)
            padding_mask = padding_mask.to(device)
            
            optimizer.zero_grad()
            mu, var = model(tokens, type_id, padding_mask)
            var = var.clamp(min=1e-6)

            loss = criterion(mu.squeeze(), rating, var.squeeze())

            loss.backward()
            optimizer.step()

            epoch_loss += loss.item()

        losses.append(epoch_loss)
        pbar.set_postfix({"loss", epoch_loss})

    # 3. save model
    torch.save({
        'epoch': epoch,
        'model_state_dict': model.state_dict(),
        'optimizer_state_dict': optimizer.state_dict(),
        'loss': loss
    }, args.model_path)

    # 3. show results
    fig, ax = plt.subplots(1, 1)
    ax.plot(np.arange(len(losses)), losses)

    plt.show()

if __name__ == '__main__':
    load_dotenv()

    parser = argparse.ArgumentParser(description="Load info from maps")

    parser.add_argument("dataset", help="The folder containing the maps")
    parser.add_argument("--model_path", help="The path to the trained model parameters", default="model.pt2")
    main(parser.parse_args())