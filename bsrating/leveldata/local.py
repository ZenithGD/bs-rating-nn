import os

from bsrating.leveldata.levelinfo import OnlineLevelInfo

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
        dict: A dictionary containing the map information and a path to the difficulty file and the info file.
    """

    level_path = os.path.join(folder_association[raw_info.id], f"{raw_info.diff}Standard.dat")
    if not os.path.isfile(level_path):
        level_path = os.path.join(folder_association[raw_info.id], f"{raw_info.diff}.dat")

        if not os.path.isfile(level_path):
            raise Exception("Difficulty file cannot be found!")
        
    return {
        "id" :              raw_info.id,
        "difficulty" :      raw_info.diff,
        "hash" :            raw_info.hash,
        "name" :            raw_info.name,
        "stars" :           raw_info.get_stars(use_bl),
        "level_path":       level_path
    }
