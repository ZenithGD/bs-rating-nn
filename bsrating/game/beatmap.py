from packaging.version import Version

from bsrating.game.element import Element

class SongInfo(Element):
    def __init__(self, version, initial_bpm, njs, diff_fname):
        self.version = version
        self.initial_bpm = initial_bpm
        self.njs = njs
        self.diff_fname = diff_fname

    @classmethod
    def get_parsing_table():
        return {
            Version("2.0.0"): SongInfo.from_json_2_0_0,
            Version("4.0.0"): SongInfo.from_json_4_0_0
        }
    
    @staticmethod
    def from_json_2_0_0(json : dict, **kwargs):
        raise NotImplementedError("TODO")
    
    @staticmethod
    def from_json_4_0_0(json : dict, **kwargs):
        raise NotImplementedError("Not planned")

    def get_diff_filename(diff : str):
        raise NotImplementedError("TODO")

class BeatMap(Element):

    def __init__(self, version : Version, info : SongInfo, bpm_events, notes, bombs, obstacles):

        self.info = info
        self.bpm_events = bpm_events
        self.notes = notes
        self.bombs = bombs
        self.obstacles = obstacles

    @classmethod
    def get_parsing_table():
        return {
            Version("2.0.0"): BeatMap.from_json_2_0_0,
            Version("3.0.0"): BeatMap.from_json_3_0_0,
            Version("4.0.0"): BeatMap.from_json_4_0_0
        }
    
    @staticmethod
    def from_json_2_0_0(json : dict, **kwargs):
        raise NotImplementedError("TODO")

    @staticmethod
    def from_json_3_0_0(json : dict, **kwargs):
        raise NotImplementedError("TODO")
    
    @staticmethod
    def from_json_4_0_0(json : dict, **kwargs):
        raise NotImplementedError("Not planned")
    