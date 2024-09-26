from enum import Enum


class WaitConditions(Enum):
    PRESENCE = "presence"
    VISIBILITY = "visibility"
    CLICKABLE = "clickable"
    TEXT = "text"
    PRESENCE_OF_ALL = "presence_of_all"
    VISIBILITY_OF_ALL = "visibility_of_all"
    SELECTED = "selected"
