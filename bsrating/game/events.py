from packaging.version import Version

from bsrating.game.element import Element

class BPMEvent(Element):

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
            json["_time"],
            json["_floatValue"]
        )
    
    @staticmethod
    def from_json_3_0_0(json: dict, **kwargs):
        return BPMEvent(
            json["b"],
            json["m"]
        )
    
    def to_dict(self):
        return {
            "type": "bpm_event",
            "beat": self.beat,
            "bpm": self.bpm
        }