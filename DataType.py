import heapq
import itertools
from enum import Enum


class PointTypes(Enum):
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
        if len(line) == 2:
            if line[0][0] == line[1][0]:
                return LineType.VERTICAL
            if line[0][1] == line[1][1]:
                return LineType.HORIZONTAL
            return LineType.INCLINED
        else:
            if line[1][0] == line[2][0]:
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


class Point:  # May be useless
    x = 0.0
    y = 0.0

    def __init__(self, x, y):
        self.x = x
        self.y = y


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
        self.right_cell = None
        self.left_cell = None
        self.segments = segments
        self.key = key


class Arc: #useless?
    p = None
    pprev = None
    pnext = None
    e = None
    s0 = None
    s1 = None

    def __init__(self, p, a=None, b=None):
        self.p = p
        self.pprev = a
        self.pnext = b
        self.e = None
        self.s0 = None
        self.s1 = None


class Segment: #Nice
    start = None
    end = None
    done = False

    def __init__(self, p):
        self.CELL = p
        self.end = None
        self.done = False

    def finish(self, p):
        if self.done: return
        self.end = p
        self.done = True


class PriorityQueue:
    def __init__(self):
        self.pq = []
        self.entry_finder = {}
        self.counter = itertools.count()

    def push(self, item):
        # check for duplicate
        if item in self.entry_finder: return
        count = next(self.counter)
        # use x-coordinate as a primary key (heapq in python is min-heap)
        entry = [item.x, count, item]
        self.entry_finder[item] = entry
        heapq.heappush(self.pq, entry)

    def remove_entry(self, item):
        entry = self.entry_finder.pop(item)
        entry[-1] = 'Removed'

    def pop(self):
        while self.pq:
            priority, count, item = heapq.heappop(self.pq)
            if item is not 'Removed':
                del self.entry_finder[item]
                return item
        raise KeyError('pop from an empty priority queue')

    def top(self):
        while self.pq:
            priority, count, item = heapq.heappop(self.pq)
            if item is not 'Removed':
                del self.entry_finder[item]
                self.push(item)
                return item
        raise KeyError('top from an empty priority queue')

    def empty(self):
        return not self.pq