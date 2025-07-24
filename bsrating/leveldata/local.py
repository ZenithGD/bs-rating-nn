import json
import os

from bsrating.leveldata.levelinfo import LocalLevelInfo, OnlineLevelInfo

def update_map_info(raw_info : LocalLevelInfo, folder_association : dict, use_bl) -> dict:

    # find beatmap information in the info file.
    path_options = [ "Info.dat", "info.dat" ]
    try:
        opt = next(
            filter(
                lambda op : os.path.isfile(os.path.join(folder_association[raw_info.id], op)), path_options
            )
        )
    except Exception as e:
        raise Exception(f"[{raw_info.id}] Info file cannot be found!")
        
    return {
        "id" :              raw_info.id,
        "difficulty" :      raw_info.diff,
        "hash" :            raw_info.hash,
        "name" :            raw_info.name,
        "stars" :           raw_info.stars,
        "song_path":        folder_association[raw_info.id],
        "info_file":        opt
    }


def combine_map_info(raw_info : OnlineLevelInfo, folder_association : dict, use_bl) -> dict:
    """Load information from the local map folder and combine it with the 
    online data. Note that this won't contain the level data, but
    it will reference the appropriate .dat file.

    Each object also contains general information about the map, such as the BeatSaver id, its hash,
    the name and the ScoreSaber ranked stars (optionally BeatLeader stars as well).

    Args:
        raw_info (dict): Combined information from online APIs.
        folder_association (dict): An association returned by `preprocess_folders`.

    Returns:
        dict: A dictionary containing the map information and a path to the song folder, as well as the characteristic and difficulty.
    """

    # find beatmap information in the info file.
    path_options = [ "Info.dat", "info.dat" ]
    try:
        opt = next(
            filter(
                lambda op : os.path.isfile(os.path.join(folder_association[raw_info.id], op)), path_options
            )
        )
    except Exception as e:
        raise Exception(f"[{raw_info.id}] Info file cannot be found!")
        
    return {
        "id" :              raw_info.id,
        "difficulty" :      raw_info.diff,
        "hash" :            raw_info.hash,
        "name" :            raw_info.name,
        "stars" :           raw_info.get_stars(use_bl),
        "song_path":        folder_association[raw_info.id],
        "info_file":        opt
    }
