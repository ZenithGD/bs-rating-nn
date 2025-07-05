import argparse 
import json
import requests
import os, time
from pprint import pprint
from tqdm import trange
from bsrating.ssapi import *
from bsrating.utils import *

from dotenv import load_dotenv

import traceback

def preprocess_folders(song_folder):

    # mapping for all files
    def strip_id(name):
        tokens = name.split()

        return tokens[0]
    
    names = os.listdir(song_folder)
    
    return { strip_id(name) : os.path.join(song_folder, name) 
             for name in names }

def load_local_map_info(raw_info, folder_association : dict):

    level_path = os.path.join(folder_association[raw_info["id"]], f"{raw_info["difficulty"]}Standard.dat")
    if not os.path.isfile(level_path):
        level_path = os.path.join(folder_association[raw_info["id"]], f"{raw_info["difficulty"]}.dat")
        
    return {
        "id" :              raw_info["id"],
        "difficulty" :      raw_info["difficulty"],
        "hash" :            raw_info["hash"],
        "name" :            raw_info["name"],
        "stars" :           raw_info["stars"],
        "level_path":       level_path
    }

def read_maps_info(
        songs_folder : str, 
        ss_ranked_playlist, 
        folder_association : list,
        verbose = False,
        limit = -1) -> list:

    MAX_ATTS = int(os.getenv("SS_TIMEOUT_RETRIES"))
    map_list = []
    i = 0
    # loop through all ranked maps and fetch information from ss
    for i in range(len(ss_ranked_playlist["songs"])):
        print("i =", i)
        item = ss_ranked_playlist["songs"][i]

        print(item)
        for diff in item["difficulties"]:
            print("diff =", diff)

            # fetch and save information combined from ss and local
            attempts = 0
            while attempts < MAX_ATTS:
                try:
                    map_info = ss_load_info_by_hash(item["hash"], diff["name"])
                    map_list.append(load_local_map_info(map_info, folder_association))
                    break
                except SSTimeOutError as terr:
                    print(f"Waiting {terr.time} seconds. Reason: {terr}")
                    time.sleep(terr.time)
                except Exception as e:
                    print("Unknown error:", traceback.print_exc())
                    time.sleep(1)
                print(f"Retrying... {attempts} / {MAX_ATTS}")
                attempts += 1

            if limit > 0 and i >= limit:
                return map_list

    return map_list

def main(args):

    # create folder 
    path_to_dataset = os.path.join(args.folder, "dataset")
    try:
        os.makedirs(path_to_dataset)
    except:
        print(f"Folder already {path_to_dataset} exists.")

    # read playlist referencing ss ranked maps
    ss_ranked_playlist = None
    with open(args.playlist) as rp:
        ss_ranked_playlist = json.load(rp)

    # associate the id with the local folder of the song
    folder_association = preprocess_folders(args.songs)

    # read song folder and fetch information from scoresaber
    song_data = read_maps_info(args.songs, ss_ranked_playlist, folder_association, verbose=args.verbose, limit=args.limit)
    with open(os.path.join(args.folder, "song_data.json"), 'w') as song_list:
        json.dump(song_data, song_list, indent=2)

if __name__ == '__main__':
    load_dotenv()

    parser = argparse.ArgumentParser(description="Load info from maps")

    parser.add_argument("folder", help="The folder to store the map dataset")
    parser.add_argument("--songs", help="The folder containing the level data")
    parser.add_argument("--playlist", help="The playlist referencing all the beat saber maps")
    parser.add_argument("--limit", type=int, default=-1, help="Limit of ranked maps")
    parser.add_argument("--verbose", action="store_true", help="Whether to print additional info")

    main(parser.parse_args())