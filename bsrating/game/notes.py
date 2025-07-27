import numpy as np
from packaging.version import Version

from bsrating.game.element import Element, ElementType

class ColorNote(Element): 

    def __init__(self, beat : float, x: float, y: float, color: int, cut_dir: float, angle_offset: float):

        self.beat = beat
        self.x = x
        self.y = y
        self.color = color
        self.cut_dir = cut_dir
        self.angle_offset = angle_offset

    @staticmethod
    def from_json_2_0_0(json: dict, **kwargs):
        return ColorNote(
            json.get("_time", 0),
            json.get("_lineIndex", 0),
            json.get("_lineLayer", 0),
            json.get("_type", 0),
            json.get("_cutDirection", 0),
            0
        )

    @staticmethod
    def from_json_3_0_0(json: dict, **kwargs):
        return ColorNote(
            json.get("b", 0),
            json.get("x", 0),
            json.get("y", 0),
            json.get("c", 0),
            json.get("d", 0),
            json.get("a", 0)
        )

    @classmethod
    def get_parsing_table(cls):
        return {
            Version("2.0.0"): ColorNote.from_json_2_0_0,
            Version("3.0.0"): ColorNote.from_json_3_0_0
        }
    
    def note_angle(self) -> float:
        # get angle of the cut direction and add offset
        dirs = [
            0,                      # 0: up
            np.pi,                  # 1: down
            -np.pi / 2.0,           # 2: left
            np.pi / 2.0,            # 3: right
            -np.pi / 4.0,           # 4: up left
            np.pi / 4.0,            # 5: up right
            -3.0 * np.pi / 4.0,     # 6: down left
            3.0 * np.pi / 4.0,      # 7: down right
            0                       # 8: any
        ]

        a = dirs[self.cut_dir] - np.deg2rad(self.angle_offset)
        any_dir = self.cut_dir == 8

        # clamp to [-pi, pi] range
        return ((a + 180.0) % 360.0) - 180.0, any_dir
    
    def to_dict(self):
        a, any_dir = self.note_angle()
    
        return {
            "type": ElementType.ColorNoteRed if self.color == 0 else ElementType.ColorNoteBlue,
            "beat": self.beat,
            "x": self.x,
            "y": self.y,
            "angle": a,
            "any_dir": any_dir
        }

class BombNote(Element):
    elm_type = ElementType.BombNote

    def __init__(self, beat : float, x, y):

        self.beat = beat
        self.x = x
        self.y = y

    @staticmethod
    def from_json_2_0_0(json: dict, **kwargs):
        return BombNote(
            json.get("_time", 0),
            json.get("_lineIndex", 0),
            json.get("_lineLayer", 0)
        )

    @staticmethod
    def from_json_3_0_0(json: dict, **kwargs):
        return BombNote(
            json.get("b", 0),
            json.get("x", 0),
            json.get("y", 0)
        )

    @classmethod
    def get_parsing_table(cls):
        return {
            Version("2.0.0"): BombNote.from_json_2_0_0,
            Version("3.0.0"): BombNote.from_json_3_0_0,
        }
    
    def to_dict(self):
        return {
            "type": self.elm_type,
            "beat": self.beat,
            "x": self.x,
            "y": self.y
        }

class Obstacle(Element):

    elm_type = ElementType.Obstacle

    def __init__(self, beat : float, x, y, duration, width, height):

        self.beat = beat
        self.x = x
        self.y = y
        self.duration = duration
        self.width = width
        self.height = height

    @classmethod
    def get_parsing_table(cls):
        return {
            Version("2.0.0"): Obstacle.from_json_2_0_0,
            Version("2.6.0"): Obstacle.from_json_2_0_0,
            Version("3.0.0"): Obstacle.from_json_3_0_0
        }
    
    @staticmethod
    def from_json_2_0_0(json: dict, **kwargs):

        match json["_type"]:
            case 0:
                return Obstacle(
                    json.get("_time", 0),
                    json.get("_lineIndex", 0),
                    0,
                    json.get("_duration", 0),
                    json.get("_width", 0),
                    5
                )
            case 1:
                return Obstacle(
                    json.get("_time", 0),
                    json.get("_lineIndex", 0),
                    2,
                    json.get("_duration", 0),
                    json.get("_width", 0),
                    3
                )

    @staticmethod
    def from_json_2_6_0(json: dict, **kwargs):
        
        match json["_type"]:
            case 0 | 1:
                return Obstacle.from_json_2_0_0(json)
            
            case 2:
                return Obstacle(
                    json.get("_time", 0),
                    json.get("_lineIndex", 0),
                    json.get("_lineLayer", 0),
                    json.get("_duration", 0),
                    json.get("_width", 0),
                    json.get("_height", 0)
                )
    
    @staticmethod
    def from_json_3_0_0(json: dict, **kwargs):
        return Obstacle(
            json.get("b", 0),
            json.get("d", 0),
            json.get("x", 0),
            json.get("y", 0),
            json.get("w", 0),
            json.get("h", 0)
        )
    
    def to_dict(self):
        return {
            "type": self.elm_type,
            "beat": self.beat,
            "x": self.x,
            "y": self.y,
            "duration": self.duration,
            "width": self.width,
            "height": self.height,
        }