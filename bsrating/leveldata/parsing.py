import os
import json

from packaging.version import Version

from bsrating.game.beatmap import BeatMap, SongInfo
from bsrating.leveldata.levelinfo import find_info_file
from bsrating.utils.strings import capitalize_diff

def process_map_folder(map_folder):

    # load info data
    info_path = find_info_file(map_folder)
    json_info = None
    with open(info_path, encoding='utf-8') as dd:
        json_info = json.load(dd)

    # load difficulty names (assumming <4.0.0)
    # TODO improve info reading (modify song info to read all diffs into a dict)
    # this is currently reading info twice
    
    # fetch all map data
    bm_data = next(filter(lambda e : e["_beatmapCharacteristicName"] == "Standard", json_info["_difficultyBeatmapSets"]))["_difficultyBeatmaps"]

    # create a dict associating the difficulty name and its path inside the map folder 
    diffs = { e["_difficulty"] : e["_beatmapFilename"] for e in bm_data }
    
    beatmaps = {}
    for diff, diff_fname in diffs.items():
        version = Version(json_info["_version"])
        diff_info = SongInfo.from_json(version, json_info, diff=capitalize_diff(diff))

        # load beatmap file data
        json_beatmap = None
        with open(os.path.join(map_folder, diff_fname), encoding='utf-8') as dd:
            json_beatmap = json.load(dd)

        jv = json_beatmap["_version"] if "_version" in json_beatmap else json_beatmap.get("version", "2.0.0")
        version = Version(jv)
        beatmap = BeatMap.from_json(version, json_beatmap, info=diff_info)

        beatmaps[diff] = beatmap
    
    return beatmaps