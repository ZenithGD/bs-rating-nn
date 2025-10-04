import argparse 
import json
from matplotlib import pyplot as plt
import requests
import os, time
from pprint import pprint
from tqdm import tqdm, trange
from bsrating.leveldata import *
from bsrating.leveldata.parsing import process_map_folder
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
    # create folder 
    try:
        os.makedirs(args.output)
    except:
        print(f"Folder already {args.output} exists.")

    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    # device = torch.device("cpu")
    print("Using device:", device)

    # 1. load map
    beatmaps = process_map_folder(args.map_folder)

    paths = []
    for diff, bm in beatmaps.items():
        output_path = os.path.join(args.output, f"{diff}.json")
        with open(output_path, 'w') as out:
            json.dump({"data": bm.to_dict(), "rating": 0}, out)

        paths.append(output_path)
    print(paths)

    # 2. eval beatmaps
    # TODO load just the model, don't load a checkpoint
    model = RatingPredictorNN(
        token_dim=10,
        model_dim=512,
        heads=4,
        attn_layers=2)
    model = model.load_state_dict(torch.load(args.model, weights_only=True))

    dataset = MapDataset(paths)
    dataloader = DataLoader(dataset, batch_size=1, collate_fn=collate_fn)

    predicted_ratings = []
    map_names = []

    with torch.no_grad():
        for batch, path in zip(dataloader, paths):
            tokens, type_ids, _, padding_mask = batch
            tokens = tokens.to(device)
            type_ids = type_ids.to(device)
            padding_mask = padding_mask.to(device)

            rating = model(tokens, type_ids, padding_mask)
            
            predicted_ratings.append(rating.item())
            map_names.append(os.path.basename(path))

    x = np.arange(len(predicted_ratings))
    ratings = np.array(predicted_ratings)

    plt.figure(figsize=(10, 5))
    plt.plot(x, ratings, fmt='o', ecolor='gray', capsize=5, label="Prediction")
    plt.xticks(x, map_names, rotation=45, ha='right')
    plt.ylabel("Stars")
    plt.title("Predicted ratings")
    plt.grid(True)
    plt.tight_layout()
    plt.legend()
    plt.show()

if __name__ == '__main__':
    load_dotenv()

    parser = argparse.ArgumentParser(description="Load info from maps")

    parser.add_argument("model", help="The path to the model parameters")
    parser.add_argument("map_folder", help="The folder containing the song data")
    parser.add_argument("--output", help="Where is the processed beatmap information stored", default=".")
    main(parser.parse_args())