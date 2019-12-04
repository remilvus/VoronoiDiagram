import heapq
import itertools
from enum import Enum


class EventTypes(Enum):
    CELL = 0
    BEND = 1
    INTERSECTION = 2
    BOUNDARY = 3

class LineType(Enum):
    HORIZONTAL = 0
    VERTICAL = 1
    INCLINED = 2
    HORIZONTAL_PART = 4  # line consisting of three segments (middle segment horizontal)
    VERTICAL_PART = 5  # line consisting of three segments (middle segment vertical)

    @staticmethod
    def get_type(line):
        if len(line) == 1:
            if line[0][0][0] == line[0][1][0]:
                return LineType.VERTICAL
            if line[0][0][1] == line[0][1][1]:
                return LineType.HORIZONTAL
            return LineType.INCLINED
        elif len(line) == 3:
            if line[1][0][1] == line[1][1][1]:
                return LineType.HORIZONTAL_PART
            return LineType.VERTICAL_PART

class Cell:
    x = 0.0
    y = 0.0
    left_bisector = None
    right_bisector = None
    left_point_used = None
    right_point_used = None
    right_event = None
    left_event = None

    def __init__(self, x, y, left_bisector=None, right_bisector=None, left_point_used=None,
                 right_point_used=None, right_event=None, left_event=None):
        self.x = x
        self.y = y
        self.left_bisector = left_bisector
        self.right_bisector = right_bisector
        self.left_point_used = left_point_used
        self.right_point_used = right_point_used
        self.right_event = right_event
        self.left_event = left_event

    # def to_string(self):
    #     return f"x = {self.x} | y = {self.y}
    # self.left_bisector = None
    # self.right_bisector = None

# class Point:  # May be useless
#     x = 0.0
#     y = 0.0
#
#     def __init__(self, x, y):
#         self.x = x
#         self.y = y


class Event:
    y = 0.0
    x = 0.0
    type = None
    valid = True  # It its not useless
    right_cell = None
    left_cell = None
    segments = None  # line part which must be added
    key = None

    def __init__(self, x, y, point_type, right_cell=None, left_cell=None, segments=None, key=None):
        self.x = x
        self.y = y
        self.type = point_type
        self.valid = True
        self.right_cell = right_cell
        self.left_cell = left_cell
        self.segments = segments
        self.key = key

    def __gt__(self, other):
        return self.x > other.x

    def __lt__(self, other):
        return self.x < other.x

    def __eq__(self, other):
        return  self.x == other.y

# class Segment: #Nice
#     start = None
#     end = None
#     done = False
#
#     def __init__(self, p):
#         self.CELL = p
#         self.end = None
#         self.done = False
#
#     def finish(self, p):
#         if self.done: return
#         self.end = p
#         self.done = True