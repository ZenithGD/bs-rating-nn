from packaging.version import Version

from abc import ABC, abstractmethod
from enum import IntEnum

class ElementType(IntEnum):
    ColorNoteRed = 0,
    ColorNoteBlue = 1,
    BombNote = 2,
    Obstacle = 3,
    Other = 4,
    BPMEvent = 100,

class Element:
    
    elm_type = ElementType.Other

    """A generic element that can be parsed. The parsing table associates a version
    with the function that generates the object from its JSON representation. For example:
    
    ```code
    parsing_table = {
        Version("1.0.0"): ColorNote.from_json_1_0_0),
        Version("1.5.0"): ColorNote.from_json_2_0_0),
        Version("2.0.0"): ColorNote.from_json_2_2_0),
        Version("2.2.0"): ColorNote.from_json_2_2_0)
    }
    ```

    Args:
        parsing_table (list): _description_
    """

    def __init__(self):
        if type(self) is Element:
            raise TypeError("Element is an abstract base class and cannot be instantiated directly.")
    
    @classmethod
    @abstractmethod
    def get_parsing_table(cls) -> dict:
        pass

    def get_enum_type(cls) -> ElementType:
        return cls.type

    @classmethod
    def from_json(cls, version : Version, json: dict, **kwargs):

        table = cls.get_parsing_table()
        versions = list(table.keys())
        target = versions[0]
        for vl in versions:
            
            if vl > version:
                break
            else:
                target = vl

        return table[target](json, **kwargs)
            
    @abstractmethod
    def to_dict(self) -> dict:
        pass
