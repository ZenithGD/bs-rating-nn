import json
import os
from bsrating.game.beatmap import BeatMap, SongInfo
from bsrating.leveldata.exceptions import MapLogicError
import numpy as np
from packaging.version import Version

from bsrating.utils.strings import capitalize_diff

class OnlineLevelInfo:

    def __init__(self, 
        id : str, 
        hash : str, 
        name : str, 
        diff : int, 
        bl_stars : float, 
        ss_stars : float,
        created_date : str):

        self.id = id
        self.hash = hash
        self.name = name
        self.diff = diff
        self.bl_stars = bl_stars
        self.ss_stars = ss_stars
        self.created_date = created_date

    def get_stars(self, use_bl : bool = False) -> float:
        """Simple weighting to take BL stars into account if necessary. If 
        `use_bl == False` then the rating will be always equivalent to the ScoreSaber star value.
        If the map is only BL ranked, the BL value will be taken into account.

        Returns:
            float: The weighted star rating
        """
        if self.ss_stars is not None and self.bl_stars is not None and use_bl:
            # prioritize SS if difference is too high, otherwise take something closer to the average
            S = self.ss_stars
            B = self.bl_stars
            difference = self.bl_stars - self.ss_stars
            h = (B + S) / 2
            l = S
            w = np.maximum(B - S, 0.1)

            return (h - l) * np.exp(-w/2.0 * difference ** 2) + l
        elif self.ss_stars is not None:
            return self.ss_stars
        elif self.bl_stars is not None:
            return self.bl_stars * 0.95
        else:
            raise MapLogicError("This map doesn't have a star rating!")

class LocalLevelInfo:

    def __init__(self, 
        id : str, 
        hash : str, 
        name : str, 
        diff : int, 
        stars : float,
        song_path : str,
        info_file : str):

        self.id = id
        self.hash = hash
        self.name = name
        self.diff = diff
        self.stars = stars
        self.song_path = song_path
        self.info_file = info_file

    def unique_id(self) -> str:

        return f"{self.hash}_{self.diff}"

    @staticmethod
    def from_json(json_data : dict):
        return LocalLevelInfo(
            json_data.get("id", ""),
            json_data.get("hash", ""),
            json_data.get("name", ""),
            json_data.get("difficulty", ""),
            json_data.get("stars", ""),
            json_data.get("song_path", ""),
            json_data.get("info_file", "")
        )
    
    def _process_info(self) -> SongInfo:

        # load info data
        json_info = None
        with open(os.path.join(self.song_path, self.info_file), encoding='utf-8') as dd:
            json_info = json.load(dd)

        version = Version(json_info["_version"])
        return SongInfo.from_json(version, json_info, diff=capitalize_diff(self.diff))
    
    def _process_beatmap(self, info : SongInfo):

        # load beatmap file data
        json_beatmap = None
        with open(os.path.join(self.song_path, info.diff_fname), encoding='utf-8') as dd:
            json_beatmap = json.load(dd)

        jv = json_beatmap["_version"] if "_version" in json_beatmap else json_beatmap.get("version", "2.0.0")
        version = Version(jv)
        return BeatMap.from_json(version, json_beatmap, info=info)

    def process(self) -> dict:

        info = self._process_info()

        return self._process_beatmap(info).to_dict()
        
