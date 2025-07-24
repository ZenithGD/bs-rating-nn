from packaging.version import Version

class BPMEvent:

    def __init__(self, beat, bpm):
        self.beat = beat
        self.bpm = bpm

    @classmethod
    def get_parsing_table():
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