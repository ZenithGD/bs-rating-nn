from packaging.version import Version

from bsrating.game.element import Element

class ColorNote(Element):

    def __init__(self, time : float, x: float, y: float, color: int, cut_dir: float, angle_offset: float):

        self.time = time
        self.x = x
        self.y = y
        self.color = color
        self.cut_dir = cut_dir
        self.angle_offset = angle_offset

    @staticmethod
    def from_json_2_0_0(json: dict, **kwargs):
        return ColorNote(
            json["_time"],
            json["_lineIndex"],
            json["_lineLayer"],
            json["_type"],
            json["_cutDirection"],
            0
        )

    @staticmethod
    def from_json_3_0_0(json: dict, **kwargs):
        return ColorNote(
            json["b"],
            json["x"],
            json["y"],
            json["c"],
            json["d"],
            json["a"]
        )

    @classmethod
    def get_parsing_table(cls):
        return {
            Version("2.0.0"): ColorNote.from_json_2_0_0,
            Version("3.0.0"): ColorNote.from_json_3_0_0
        }
    
    def to_dict(self):
        return {
            "type": "color_note",
            "time": self.time,
            "x": self.x,
            "y": self.y,
            "color": self.color,
            "cut_dir": self.cut_dir,
            "angle_offset": self.angle_offset,
        }

class BombNote(Element):

    def __init__(self, time : float, x, y):

        self.time = time
        self.x = x
        self.y = y

    @staticmethod
    def from_json_2_0_0(json: dict, **kwargs):
        return BombNote(
            json["_time"],
            json["_lineIndex"],
            json["_lineLayer"]
        )

    @staticmethod
    def from_json_3_0_0(json: dict, **kwargs):
        return BombNote(
            json["b"],
            json["x"],
            json["y"]
        )

    @classmethod
    def get_parsing_table(cls):
        return {
            Version("2.0.0"): BombNote.from_json_2_0_0,
            Version("3.0.0"): BombNote.from_json_3_0_0,
        }
    
    def to_dict(self):
        return {
            "type": "bomb_note",
            "time": self.time,
            "x": self.x,
            "y": self.y
        }

class Obstacle(Element):

    def __init__(self, time : float, x, y, duration, width, height):

        self.time = time
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
                    json["_time"],
                    json["_lineIndex"],
                    0,
                    json["_duration"],
                    json["_width"],
                    5
                )
            case 1:
                return Obstacle(
                    json["_time"],
                    json["_lineIndex"],
                    2,
                    json["_duration"],
                    json["_width"],
                    3
                )

    @staticmethod
    def from_json_2_6_0(json: dict, **kwargs):
        
        match json["_type"]:
            case 0 | 1:
                return Obstacle.from_json_2_0_0(json)
            
            case 2:
                return Obstacle(
                    json["_time"],
                    json["_lineIndex"],
                    json["_lineLayer"],
                    json["_duration"],
                    json["_width"],
                    json["_height"]
                )
    
    @staticmethod
    def from_json_3_0_0(json: dict, **kwargs):
        return Obstacle(
            json["b"],
            json["d"],
            json["x"],
            json["y"],
            json["w"],
            json["h"]
        )
    
    def to_dict(self):
        return {
            "type": "obstacle",
            "time": self.time,
            "x": self.x,
            "y": self.y,
            "duration": self.duration,
            "width": self.width,
            "height": self.height,
        }