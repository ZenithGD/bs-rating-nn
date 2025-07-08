import argparse 
import json
import requests
import os, time
from pprint import pprint
from tqdm import trange
from bsrating.leveldata import *
from bsrating.utils import *

from dotenv import load_dotenv

import traceback

def preprocess_folders(song_folder: str):
    """From the song folder, create the association between ids and the full folder name
    that contains the map data. This will generate a dictionary like this:

    ```
    {
        '1a3e1' : '<song_folder>/1a3e1 (Go Insane - Helloiamdaan & miitchel)',
        '3b2f8' : '<song_folder>/3b2f8 (Kyuukou - zeon & Gabriel)',
        '2c239' : '<song_folder>/2c238 (When I use it - Astrella & Timbo)'
    }
    ```

    The result is used to efficiently look up for a song folder just by the id of the map.

    Args:
        song_folder (str): The path pointing to the CustomLevels folder.

    Returns:
        _type_: _description_
    """

    # mapping for all files
    def strip_id(name):
        tokens = name.split()

        return tokens[0]
    
    names = os.listdir(song_folder)
    
    return { strip_id(name) : os.path.join(song_folder, name) 
             for name in names if os.path.isdir(os.path.join(song_folder, name)) }

def read_maps_info(
        songs_folder : str, 
        ranked_playlist : dict, 
        folder_association : dict,
        verbose = False,
        limit = -1) -> list:
    """Read information about all the maps and return a list containing the combined
    info from Beat Saver and ScoreSaber. 

    The maps from the playlist `ranked_playlist` are searched in the `songs_folder` folder, which
    should contain the level data for the songs.

    Args:
        songs_folder (str): The path pointing to the folder containing the levels' data
        (i.e. your CustomLevels folder)
        ranked_playlist (dict): An object containing the playlist data for all songs to be searched.
        folder_association (dict): A dictionary that associates the level's Beat Saver id to its location in the 
        songs folder. This should be the result of the `preprocess_folder` function
        verbose (bool, optional): Whether to print additional info. Defaults to False.
        limit (int, optional): The limit of maps to process. If the limit is negative, 
        then all songs from the playlist are included. Defaults to -1.

    Returns:
        list: The list of maps, each contains general information about the 
    """

    MAX_ATTS = int(os.getenv("SS_TIMEOUT_RETRIES"))
    map_list = []
    i = 0
    # loop through all ranked maps and fetch information from ss
    for i in range(len(ranked_playlist["songs"])):
        print("i =", i)
        item = ranked_playlist["songs"][i]

        print(item)
        for diff in item["difficulties"]:
            print("diff =", diff)

            # fetch and save information combined from ss and local
            attempts = 0
            while attempts < MAX_ATTS:
                try:
                    map_info = ss_load_info_by_hash(item["hash"], diff["name"])
                    map_list.append(combine_map_info(map_info, folder_association))
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
    ranked_playlist = None
    with open(args.playlist) as rp:
        ranked_playlist = json.load(rp)

    # associate the id with the local folder of the song
    folder_association = preprocess_folders(os.getenv("SONG_FOLDER"))

    # read song folder and fetch information from scoresaber
    song_data = read_maps_info(
        os.getenv("SONG_FOLDER"), 
        ranked_playlist, 
        folder_association, 
        verbose=args.verbose, limit=args.limit)
    
    with open(os.path.join(args.folder, "song_data.json"), 'w') as song_list:
        json.dump(song_data, song_list, indent=2)

    # 

if __name__ == '__main__':
    load_dotenv()

    parser = argparse.ArgumentParser(description="Load info from maps")

    parser.add_argument("folder", help="The folder to store the map dataset")
    parser.add_argument("--playlist", help="The playlist referencing all the beat saber maps")
    parser.add_argument("--limit", type=int, default=-1, help="Limit of ranked maps")
    parser.add_argument("--verbose", action="store_true", help="Whether to print additional info")

    main(parser.parse_args())