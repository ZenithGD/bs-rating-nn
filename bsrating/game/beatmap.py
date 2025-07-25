from pprint import pprint
from packaging.version import Version

from bsrating.game.element import Element
from bsrating.game.events import BPMEvent
from bsrating.game.notes import BombNote, ColorNote, Obstacle

class SongInfo(Element):
    def __init__(self, version : Version, initial_bpm : float, njs : float, diff_fname : str):
        self.version = version
        self.initial_bpm = initial_bpm
        self.njs = njs
        self.diff_fname = diff_fname

    @classmethod
    def get_parsing_table(cls):
        return {
            Version("2.0.0"): SongInfo.from_json_2_0_0,
            Version("4.0.0"): SongInfo.from_json_4_0_0
        }
    
    @staticmethod
    def from_json_2_0_0(json : dict, **kwargs):
        
        jv = json["_version"] if "_version" in json else json.get("version", "2.0.0")
        version = Version(jv)

        if "version" in json:
            print(version)
        initial_bpm = json["_beatsPerMinute"]

        # fetch all map data
        bm_data = next(filter(lambda e : e["_beatmapCharacteristicName"] == "Standard", json["_difficultyBeatmapSets"]))["_difficultyBeatmaps"]

        # get the path pointing to the difficulty file and its NJS    
        diff_data = next(filter(lambda e : e["_difficulty"] == kwargs["diff"], bm_data))
        diff_fname = diff_data["_beatmapFilename"]
        diff_njs = diff_data["_noteJumpMovementSpeed"]

        return SongInfo(version, initial_bpm, diff_njs, diff_fname)
    

    @staticmethod
    def from_json_4_0_0(json : dict, **kwargs):
        raise NotImplementedError("Not planned (4.0.0)")

class BeatMap(Element):

    def __init__(self, version : Version, info : SongInfo, 
                 bpm_events : list, notes : list, bombs : list, obstacles : list):

        self.version = version
        self.info = info
        self.bpm_events = bpm_events
        self.notes = notes
        self.bombs = bombs
        self.obstacles = obstacles

    @classmethod
    def get_parsing_table(cls):
        return {
            Version("2.0.0"): BeatMap.from_json_2_0_0,
            Version("3.0.0"): BeatMap.from_json_3_0_0,
            Version("4.0.0"): BeatMap.from_json_4_0_0
        }
    
    @staticmethod
    def from_json_2_0_0(json : dict, **kwargs):
        jv = json["_version"] if "_version" in json else json.get("version", "2.0.0")
        version = Version(jv)

        # read bpm events
        bpm_events = list(
            map(lambda fev : BPMEvent.from_json(version, fev), 
                filter(lambda ev : ev["_type"] == 100, json["_events"])
                )
            )

        # read notes
        notes = []
        bombs = []

        for note in json["_notes"]:

            match note["_type"]:
                case 0 | 1:
                    notes.append(ColorNote.from_json(version, note))

                case 3:
                    notes.append(BombNote.from_json(version, note))

        # read obstacles
        obstacles = list(map(lambda o : Obstacle.from_json(version, o), json["_obstacles"]))

        return BeatMap(version, kwargs["info"], bpm_events, notes, bombs, obstacles)

    @staticmethod
    def from_json_3_0_0(json : dict, **kwargs):
        jv = json["_version"] if "_version" in json else json.get("version", "2.0.0")
        version = Version(jv)

        # read bpm events
        bpm_events = list(
            map(lambda fev : BPMEvent.from_json(version, fev), json["bpmEvents"])
        )

        # read notes
        notes = list(
            map(lambda fev : ColorNote.from_json(version, fev), json["colorNotes"])
        )
        bombs = list(
            map(lambda fev : BombNote.from_json(version, fev), json["bombNotes"])
        )

        # read obstacles
        obstacles = list(
            map(lambda fev : Obstacle.from_json(version, fev), json["obstacles"])
        )

        return BeatMap(version, kwargs["info"], bpm_events, notes, bombs, obstacles)

    
    @staticmethod
    def from_json_4_0_0(json : dict, **kwargs):
        raise NotImplementedError("Not planned (4.0.0)")
    
    def to_dict(self):
        
        serialized_elms = []

        # TODO: for every element, change the beat ("time" field) to real time in seconds.
        # This will potentially improve gauging difficulty based on swing speed/eBPMs

        bpms = sorted(self.bpm_events, key = lambda ev : ev.beat)

        elements = list(sorted(self.notes + self.obstacles + self.bombs, key = lambda n : n.time))
        elements = list(map(lambda e : e.to_dict(), elements))
        
        return elements