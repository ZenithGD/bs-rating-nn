import argparse 
import json
import requests
import os, time
from pprint import pprint
from tqdm import tqdm, trange
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
        use_bl : bool = False,
        verbose = False,
        map_list : list = [],
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
        songs folder. This should be the result of the `preprocess_folder` function.
        use_bl (bool, optional): Whether to fetch information from the BeatLeader servers.
        verbose (bool, optional): Whether to print additional info. Defaults to False.
        limit (int, optional): The limit of maps to process. If the limit is negative, 
        then all songs from the playlist are included. Defaults to -1.

    Returns:
        list: The list of maps, each contains general information about the 
    """
    # allows quick lookup of existing map data
    existing_maps = { (item["hash"].lower(), item["difficulty"]) : i for i, item in enumerate(map_list) }

    MAX_ATTS = int(os.getenv("SS_TIMEOUT_RETRIES"))

    # loop through all ranked maps (or up to the limit) and fetch information from ss
    rp = list(ranked_playlist)
    if limit > 0:
        rp = rp[:limit]

    for i, item in enumerate(tqdm(rp)):
        hash_key, diff_name = item
        try:
            if (hash_key.lower(), diff_name) not in existing_maps.keys():
                map_info = load_info_by_hash(hash_key, diff_name, MAX_ATTS, use_bl)
                map_list.append(combine_map_info(map_info, folder_association, use_bl))
            else:
                # update hash to be consistent just in case
                map_info = map_list[existing_maps[(hash_key.lower(), capitalize_diff(diff_name))]]
                updated_info = update_map_info(LocalLevelInfo.from_json(map_info), folder_association, use_bl)
                map_list[existing_maps[(hash_key.lower(), diff_name)]] = updated_info
        except Exception as e:
            if verbose:
                print("Unknown error:", e)
                traceback.print_exc()

    return map_list

def read_playlists(ss_path : str, bl_path : str, use_bl) -> list:
    # read playlists referencing ranked maps
    ss_ranked_playlist = None
    with open(ss_path) as rp:
        ss_ranked_playlist = json.load(rp)

    bl_ranked_playlist = None
    if use_bl:
        with open(bl_path) as rp:
            bl_ranked_playlist = json.load(rp)

    raw_list = ss_ranked_playlist["songs"]
    if bl_ranked_playlist is not None and use_bl:
        raw_list += bl_ranked_playlist["songs"]

    # Remove duplicates and save one entry per (hash, diff) pair.
    playlist = { (item["hash"].lower(), diff["name"]) 
                for item in raw_list
                for diff in item["difficulties"] if diff["characteristic"] == "Standard" }
    
    return playlist

def process_diff_files(song_data : list, folder : str):
    
    err_parse_count = 0
    
    for i, diff_data in enumerate(tqdm(song_data)):
        local_data = LocalLevelInfo.from_json(diff_data)
        with open(os.path.join(folder, local_data.unique_id()), 'w', encoding='utf-8') as f:
            try:
                json.dump(local_data.process(), f)
            except Exception as e:
                print(f"({local_data.id}, {local_data.diff}) Error dumping diff:", e)
                traceback.print_exc()
                err_parse_count += 1

    print(f"{err_parse_count} maps failed to load!")

def main(args):

    # create folder 
    path_to_dataset = os.path.join(args.folder, "dataset")
    try:
        os.makedirs(path_to_dataset)
    except:
        print(f"Folder already {path_to_dataset} exists.")

    print("1. Reading playlists...")
    ranked_playlist = read_playlists(args.ss_playlist, args.bl_playlist, args.use_bl)

    # check if the output file exists and has some maps already
    map_list = []
    try:
        with open(os.path.join(args.folder, args.output)) as em:
            map_list = json.load(em)
    except Exception as e:
        print(e)

    # associate the id with the local folder of the song
    folder_association = preprocess_folders(os.getenv("SONG_FOLDER"))

    print("2. Fetching map info...")
    # read song folder and fetch information from scoresaber
    if args.skip_fetch:
        with open(os.path.join(args.folder, args.output)) as song_file:
            song_data = json.load(song_file)
    else:
        song_data = read_maps_info(
            os.getenv("SONG_FOLDER"), 
            ranked_playlist, 
            folder_association, 
            use_bl=args.use_bl,
            map_list=map_list,
            verbose=args.verbose, 
            limit=args.limit)
    
    with open(os.path.join(args.folder, args.output), 'w') as song_list:
        json.dump(song_data, song_list, indent=2)

    # process each difficulty file for training later 
    # only the note information will be kept along with the real timestamp (not in beats but in seconds)
    # this can potentially be used for the positional encodings to introduce information about the 
    # speed of the swings.
    print("3. Processing difficulty files...")
    process_diff_files(song_data, path_to_dataset)

if __name__ == '__main__':
    load_dotenv()

    parser = argparse.ArgumentParser(description="Load info from maps")

    parser.add_argument("folder", help="The folder to store the map dataset")
    parser.add_argument("--ss_playlist", help="The playlist referencing all the SS ranked maps.", required=True)
    parser.add_argument("--bl_playlist", help="The playlist referencing all the BL ranked maps.")
    parser.add_argument("--use_bl", action="store_true", help="Whether to use BL ranked maps as well.")
    parser.add_argument("--limit", type=int, default=-1, help="Limit of ranked maps")
    parser.add_argument("--verbose", action="store_true", help="Whether to print additional info")
    parser.add_argument("--output", help="The name of the output .json file referencing all the songs.", default="song_data.json")
    parser.add_argument("--skip_fetch", action="store_true", help="Skip fetch and use local data only. Will look for a file matching the output name")
    main(parser.parse_args())