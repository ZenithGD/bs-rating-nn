from packaging.version import Version

from bsrating.game.element import Element, ElementType

class BPMEvent(Element):

    elm_type = ElementType.BPMEvent

    def __init__(self, beat, bpm):
        self.beat = beat
        self.bpm = bpm

    @classmethod
    def get_parsing_table(cls):
        return {
            Version("2.5.0"): BPMEvent.from_json_2_5_0,
            Version("3.0.0"): BPMEvent.from_json_3_0_0
        }
    
    @staticmethod
    def from_json_2_5_0(json: dict, **kwargs):

        return BPMEvent(
            json.get("_time", 0),
            json.get("_floatValue", 0)
        )
    
    @staticmethod
    def from_json_3_0_0(json: dict, **kwargs):
        return BPMEvent(
            json.get("b", 0),
            json.get("m", 0)
        )
    
    def to_dict(self):
        return {
            "type": self.elm_type,
            "beat": self.beat,
            "bpm": self.bpm
        }
    
    @classmethod
    def get_enum_type(cls) -> ElementType:
        pass