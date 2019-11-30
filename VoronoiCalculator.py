import numpy as np
from queue import PriorityQueue
from DataType import *
from RBTree import *
from MaxMetric import *
from Plot import *


# def dist(point1, point2):
#     return np.sqrt(np.power(point1[0] - point2[0], 2) + np.power(point1[1] - point2[1], 2))

class Voronoi:
    def __init__(self, points):
        self.output = []  # list of line segment
        self.scenes = []  # list of scenes for visualization
        self.points = []  # for visualization

        self.events = PriorityQueue()
        self.active_cells = RBTree()

        # bounding box
        self.x0 = 0.5
        self.x1 = 0.5
        self.y0 = 0.5
        self.y1 = 0.5

        # insert points to site event
        for (x, y) in points:
            self.points.append((x, y))
            self.events.put((-y, Event(x=x, y=y, point_type=EventTypes.CELL, key=y)))
            # keep track of bounding box size
            if x < self.x0: self.x0 = x
            if y < self.y0: self.y0 = y
            if x > self.x1: self.x1 = x
            if y > self.y1: self.y1 = y

        # add margins to the bounding box
        dx = (self.x1 - self.x0 + 1) / 5.0
        dy = (self.y1 - self.y0 + 1) / 5.0
        self.x0 = self.x0 - dx
        self.x1 = self.x1 + dx
        self.y0 = self.y0 - dy
        self.y1 = self.y1 + dy

        self._bisector = lambda a, b: bisector(list(a).copy(), list(b).copy(), [self.x0, self.x1], [self.y0, self.y1])

    def _make_scene(self):
        points_collection = PointsCollection(self.points)
        line_collection = LinesCollection(self.output.copy())
        self.scenes.append(Scene([points_collection], [line_collection]))

    # main part
    def process(self):
      #  i = 0
        while not self.events.empty():
            key, event = self.events.get()
            print(f"valid? {event.valid} | event {event.type} at {event.x}, {event.y} | key {event.key} | cells: {event.left_cell} "
                  f"{event.right_cell}")
            if event.valid:
                # i+=1
                # if i>20:
                #     continue
                if event.type == EventTypes.CELL:
                    self._process_cell(event)
                elif event.type == EventTypes.BEND:
                    self._process_bend(event)
                elif event.type == EventTypes.INTERSECTION:
                    print("processing intersection")
                    self._process_intersection(event)
                else:  # boundary event
                    self._process_bound(event)
                self._make_scene()

        self._make_scene()

    # utility functions for line processing
    @staticmethod
    def _get_top_segment(line):
        if line[0][0][1] > line[0][1][1]:
            return line[0]
        else:
            return line[-1]

    @staticmethod
    def _get_mid_segment(line):
        return line[1]

    @staticmethod
    def _get_bot_segment(line):
        if line[0][0][1] < line[0][1][1]:
            return line[0]
        else:
            return line[-1]

    @staticmethod
    def _get_top_point(line):
        """gets point on line which is closest to the top end of the line"""
        a, b = Voronoi._get_top_segment(line)
        return Voronoi._get_lower_point(a, b) # get the point which is not the end of the line

    @staticmethod
    def _get_bot_point(line):
        """gets point on line which is closest to the bottom end of the line"""
        a, b = Voronoi._get_bot_segment(line)
        return Voronoi._get_higher_point(a, b)  # get the point which is not the end of the line

    @staticmethod
    def _get_lower_point(a, b):
        if a[1] > b[1]:
            return b
        else:
            return a

    @staticmethod
    def _get_higher_point(a, b):
        if a[1] < b[1]:
            return b
        else:
            return a

    @staticmethod
    def _extract_line_part(line, a, b):
        # todo extract part of line between points a and b
        # line = line.copy()
        # if a[0] > b[0]:
        #     a, b = b, a
        # elif a[0]==b[0]:
        #     if a[1] > b[1]:
        #         a, b = b, a
        # # "a" is on the left of or below b
        # line_type = LineType.get_type(line)
        # if line_type==LineType.HORIZONTAL_PART:
        #     if a in line:
        #         i = line.index(a)
        #         line = line[i:]
        #     else:
        #         for i in range(len(line)-1):
        #             if line[i+1][0] > a[0]:
        #                 line = line[i:]
        #                 line[0] = a
        #     if b in line:
        #         i = line.index(b)
        #         line = line[:(i+1)]
        #     else:
        #         for i in range(len(line) - 1):
        #             if line[i + 1][0] > b[0]:
        #                 line = line[:(i+2)]
        #                 line[-1] = b
        # elif line_type == LineType.VERTICAL_PART:
        #     if a in line:
        #         i = line.index(a)
        #         line = line[i:]
        #     else:
        #         for i in range(len(line)-1):
        #             if line[i+1][1] > a[1]:
        #                 line = line[i:]
        #                 line[0] = a
        #     if b in line:
        #         i = line.index(b)
        #         line = line[:(i+1)]
        #     else:
        #         for i in range(len(line) - 1):
        #             if line[i + 1][1] > b[1]:
        #                 line = line[:(i+2)]
        #                 line[-1] = b
        return line

    @staticmethod
    def _segments_from_horizontal(line): # gets top two segments from line
        return [Voronoi._get_top_segment(line), line[1]]

    def _cut_to_intersection(self, line, intersection, use_left):
        if use_left:
            line = self._extract_line_part(line, intersection, line[0])
        else:
            line = self._extract_line_part(line, intersection, line[-1])
        return line

    @staticmethod
    def _is_above(a, b):
        """checks if a is above b"""
        return a[1] > b[1]

    # event processing methods

    def _intersection_to_event(self, key, node, left_n, right_n, intersection):
        self._invalidate_events(key, left_n, right_n)
        if type(node) == RBNode:
            node = node.value

        # add intersection event
        segments = self._extract_line_part(left_n.right_bisector, left_n.right_point_used, intersection)
        event = Event(intersection[0], intersection[1], left_cell=left_n, right_cell=right_n,
                      segments=segments, point_type=EventTypes.INTERSECTION, key=key)

        self.events.put((-key, event))

        # update info in tree nodes
        left_n.right_point_used = intersection
        right_n.left_point_used = intersection
        node.left_point_used = intersection
        node.right_point_used = intersection
        node.left_event = node.right_event = event

    def _process_cell(self, event):
        node = self.active_cells.findNode(event.x)
        if node:  # adding exactly below active cell point (rare)
            # TODO (low priority)
            pass

        node = self.active_cells.insert(event.x)
        node.value = Cell(event.x, event.y)
       # print(f"node.value: {node.value}")
        new_events = []  # node.value is set later with events

        # get neighbours
        left_n = right_n = None
        left_n_key = self.active_cells.predecessor(event.x)
        if left_n_key:
            left_n = self.active_cells.findNode(left_n_key)
           # print(f"left_n.value: {left_n.value}")
        right_n_key = self.active_cells.successor(event.x)
        if right_n_key:
            right_n = self.active_cells.findNode(right_n_key)
           # print(f"right_n.value: {right_n.value}")

        # calculate bisectors
        cell_point = (node.value.x, node.value.y)
        intersection = line_left = line_right = None
        if left_n:
            left_point = (left_n.value.x, left_n.value.y)
            line_left = self._bisector(cell_point, left_point)
           # print(f"left bis {line_left}")
        if right_n:
            right_point = (right_n.value.x, right_n.value.y)
            line_right = self._bisector(cell_point, right_point)
           # print(f"right bis {line_right}")
        if line_right and line_left:
            intersection = cross(line_left, line_right)

        if intersection:
            key = cell_point[1] # cell_point is on the bottom of circle -> the event will be processed next
            self._intersection_to_event(key, node, left_n.value, right_n.value, intersection)
        else:  # there is none or one neighbour
            # TODO make method that does this part (low priority)
            # make sure it can't happen with two neighbours
            line = None
            is_left = False
            if line_left:
                line = line_left
                is_left = True
            elif line_right:
                line = line_right

            if line: # there is one neighbour
                if LineType.get_type(line) == LineType.HORIZONTAL_PART:

                    # gets segments that can be added to Voronoi diagram
                    segments = self._segments_from_horizontal(line)
                    print(f"seg from horiztonal: {segments}")
                    event_x, event_y = self._get_bot_point(line)
                    key = event_y # key is above current key -> it will be added to Voronoi diagram in the next step
                    if is_left:
                        event = Event(event_x, event_y,  left_cell=left_n.value, right_cell=node.value,
                                      segments=segments, point_type=EventTypes.BEND, key=key)
                        left_n.value.right_point_used = (event_x, event_y)
                        node.value.left_point_used = (event_x, event_y)
                        node.value.left_event = event
                    else:
                        event = Event(event_x, event_y,  left_cell=node.value, right_cell=right_n.value,
                                      segments=segments, point_type=EventTypes.BEND, key=key)
                        right_n.value.left_point_used = (event_x, event_y)
                        node.value.right_point_used = (event_x, event_y)
                        node.value.right_event = event
                    self.events.put((-key, event))
                elif LineType.get_type(line) == LineType.VERTICAL_PART:
                    segments = [self._get_top_segment(line)]
                    event_x, event_y = self._get_top_point(line)
                    key = event_y  # key is above current key -> it will be added to Voronoi diagram in the next step

                    if is_left:
                        event = Event(event_x, event_y, left_cell=left_n.value, right_cell=node.value,
                                      segments=segments, point_type=EventTypes.BEND, key=key)
                        left_n.value.right_point_used = (event_x, event_y)
                        node.value.left_point_used = (event_x, event_y)
                        node.value.left_event = event
                    else:
                        event = Event(event_x, event_y, left_cell=node.value, right_cell=right_n.value,
                                      segments=segments, point_type=EventTypes.BEND, key=key)
                        right_n.value.left_point_used = (event_x, event_y)
                        node.value.right_point_used = (event_x, event_y)
                        node.value.right_event = event
                    self.events.put((-key, event))
                else:
                    # TODO process other types of lines (pure vertical, inclined, ?horizontal?) (low priority)
                    pass

        # update bisectors and events in tree nodes
        if line_left:
            print(f"update {left_n.value}")
            left_n.value.right_bisector = line_left
            node.value.left_bisector = line_left
        if line_right:
            print(f"update {right_n.value}")
            node.value.right_bisector = line_right
            right_n.value.left_bisector = line_right

    def _process_intersection(self, event):
        for segment in event.segments:
            self.output.append(segment)

        # get bisectors which intersect at this event
        left_bisector = event.left_cell.right_bisector
        right_bisector = event.right_cell.left_bisector

        mid_cell_key = self.active_cells.successor(event.left_cell.x)
        mid_cell = self.active_cells.findNode(mid_cell_key).value

        # TODO process intersection if mid_cell is on top
        # now assuming mid_cell is on circle bottom

        intersection = (event.x, event.y)

        for (line, is_left) in zip([left_bisector, right_bisector], [True, False]):
            new_event = None
            if LineType.get_type(line) == LineType.VERTICAL_PART:
                segments = self._extract_line_part(line, intersection, self._get_top_point(line))
                if len(segments) == 1: # add new bend event at intersection
                    x, y = intersection
                    key = y
                else:
                    if len(segments) == 3:
                        top_point = self._get_top_point(line)
                        segment = self._extract_line_part(line, intersection, top_point)[0]
                        self.output.append(segment)
                        segments = self._cut_to_intersection(line, top_point, use_left=is_left)
                    x, y = self._get_bot_point(line)
                    key = y

            if LineType.get_type(line) == LineType.HORIZONTAL_PART:
                segments = self._extract_line_part(line, intersection, self._get_bot_point(line))
                if len(segments) == 1:  # add new bend event at intersection
                    x, y = intersection
                    key = y
                else:
                    x, y = self._get_bot_point(line)
                    key = y

                if is_left:
                    new_event = Event(x, y, point_type=EventTypes.Bend, right_cell=mid_cell, left_cell=event.left_cell,
                                  segments=segments, key=key)
                else:
                    new_event = Event(x, y, point_type=EventTypes.Bend, right_cell=event.right_cell, left_cell=mid_cell,
                                  segments=segments, key=key)
            if new_event:
                self.events.put((-key, new_event))
            else:
                # todo add boundary event
                pass

        # todo if middle cell point is on circle top delete it from active cells

    def _process_bend(self, event):
        for segment in event.segments:
            self.output.append(segment)

        line_left = event.left_cell.left_bisector
        line_right = event.right_cell.right_bisector
        event_line = event.left_cell.right_bisector
        #print(f"cells: \n left: {event.left_cell} \n right: {event.right_cell}")
        #print(f"bend lines: \n left: {line_left} \n mid: {event_line} \n right: {line_right}")

        if line_left:
            intersection = cross(line_left, event_line)
            if intersection:
                #print(f"bend event: (left) intersection found at {intersection}")
                mid_cell = event.left_cell  # mid cell is on top of the circle
                left_cell_key = self.active_cells.predecessor(event.left_cell.x)
                left_cell = self.active_cells.findNode(left_cell_key).value
                d = distance(intersection, (mid_cell.x, mid_cell.y))
                key = intersection[1] - d
                self._intersection_to_event(key, mid_cell, left_cell, event.right_cell, intersection)
            else:
                # todo add bound event
                pass
        if line_right:
            intersection = cross(line_left, event_line)
            if intersection:
              #  print(f"bend event: (right) intersection found at {intersection}")
                mid_cell = event.right_cell
                right_cell_key = self.active_cells.successor(event.right_cell.x)
                right_cell = self.active_cells.findNode(right_cell_key).value
                d = distance(intersection, (mid_cell.x, mid_cell.y))
                key = intersection[1] - d
                self._intersection_to_event(key, mid_cell, event.left_cell, right_cell, intersection)
            else:
                # todo add bound event
                pass

    def _process_bound(self, event):
        for segment in event.segments:
            self.output.append(segment)

        # TODO
        pass

    # other

    def _process_line(self, line, cell):
        events = []
        line_type = LineType.get_type(line)
        if line_type == LineType.VERTICAL: #  only one segment
            pass
        elif line_type == LineType.HORIZONTAL:
            pass
        elif line_type == LineType.VERTICAL_PART:
            # add top to voronoi
            line_top = self._get_top_segment(line)
            self.output.append(line_top)
            # add bot to events
            bot_point = self._get_bot_point(line)
            mid_segment = self._get_mid_segment(line)
            dist = distance(bot_point, cell)
            event = Event(x=bot_point[0], y=bot_point[1], point_type=EventTypes.BEND, segment=mid_segment)
            self.events.put((bot_point[1] - dist, event))

            pass
        elif line_type == LineType.HORIZONTAL_PART:
            # add both to voronoi
            for segment in self._segments_from_horizontal(line):
                self.output.append(segment)
            pass
        elif line_type == LineType.INCLINED:
            # TODO (low priority)
            pass
        else:
            # should never occur
            raise AssertionError
        return event


    def print_output(self):
        it = 0
        for o in self.output:
            it = it + 1
            p0 = o.CELL
            p1 = o.end
            print(p0.x, p0.y, p1.x, p1.y)

    def get_output(self):
        res = []
        for o in self.output:
            p0 = o.CELL
            p1 = o.end
            res.append((p0.x, p0.y, p1.x, p1.y))
        return res

    def _invalidate_events(self, key, left_n, right_n):
        # todo invalidate events in nodes based on key of a new event
        pass


def get_points():
    plot = Plot()
    plot.draw()
    points = plot.get_added_points()[0].points
    points = np.array(points, dtype=np.float64)
    idx = np.argsort(points[:, 1])
    idx = np.flip(idx)
    return points[idx, :]


if __name__ == "__main__":
    points = get_points()
    voronoi = Voronoi(points)
    voronoi.process()
    plot = Plot(voronoi.scenes)
    plot.draw()
