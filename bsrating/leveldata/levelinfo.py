import json
from bsrating.leveldata.exceptions import MapLogicError
import numpy as np

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
        level_path : str):

        self.id = id
        self.hash = hash
        self.name = name
        self.diff = diff
        self.stars = stars
        self.level_path = level_path

    def unique_id(self) -> str:

        return f"{self.hash}_{self.diff}"

    @staticmethod
    def from_json(json_data : dict):

        return LocalLevelInfo(
            json_data["id"],
            json_data["hash"],
            json_data["name"],
            json_data["diff"],
            json_data["stars"],
            json_data["level_path"]
        )
    
    def process(self) -> dict:

        # load difficulty data
        data = None
        with open(self.level_path) as dd:
            data = json.load(dd)

        # get notes, arcs and chains
        
