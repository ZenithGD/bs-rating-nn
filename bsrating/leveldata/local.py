import os

def combine_map_info(raw_info : dict, folder_association : dict) -> dict:
    """Load information from the local map folder and combine it with the 
    online BeatSaver and ScoreSaber data. Note that this won't contain the level data, but
    it will reference the appropriate .dat file.

    Each object also contains general information about the map, such as the BeatSaver id, its hash,
    the name and the ScoreSaber ranked stars.

    Args:
        raw_info (dict): Combined information from ScoreSaber and BeatSaver APIs.
        folder_association (dict): An association returned by `preprocess_folders`.

    Returns:
        dict: A dictionary containing the map information and a pointer to the 
    """

    level_path = os.path.join(folder_association[raw_info["id"]], f"{raw_info["difficulty"]}Standard.dat")
    if not os.path.isfile(level_path):
        level_path = os.path.join(folder_association[raw_info["id"]], f"{raw_info["difficulty"]}.dat")

        if not os.path.isfile(level_path):
            raise 
        
    return {
        "id" :              raw_info["id"],
        "difficulty" :      raw_info["difficulty"],
        "hash" :            raw_info["hash"],
        "name" :            raw_info["name"],
        "stars" :           raw_info["stars"],
        "level_path":       level_path
    }