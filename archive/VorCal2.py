import numpy as np
from queue import PriorityQueue
from DataType import *
from RBTree import *
from MaxMetric import *
from Plot import *

from Plot import PlotFirst, PlotSecond


class Voronoi:
    def __init__(self, points):
        self.output = []  # list of line segment
        self.scenes = []  # list of scenes for visualization
        self.points = []  # for visualization
        self._current_key = -99999999999
        self._eps = 1e-10

        self.boundary_events = []
        self.events = PriorityQueue()
        self.active_cells = RBTree()

        # bounding box
        self.x0 = -1.5
        self.x1 = 1.5
        self.y0 = -1.5
        self.y1 = 1.5
        self._broom_location = 999

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

    def _make_scene(self, key, event):
        if not self._broom_location:
            self._broom_location = -self._current_key
        if self._broom_location > -self._current_key:
            self._broom_location = -self._current_key
        points_collection = PointsCollection(self.points)
        line_collection = LinesCollection(self.output.copy())
        broom = LinesCollection([[[self.x0, self._broom_location], [self.x1, self._broom_location]]], color='red')
        # PointsCollection(event,color='red')
        point=[event.x,event.y]
        self.scenes.append(Scene([points_collection, PointsCollection([point], color='orange')], [line_collection, broom]))

    # main part
    def process(self):
        while not self.events.empty():
            key, event = self.events.get()
            self._current_key = key
            print(f"valid? {event.valid} | event {event.type} at {event.x}, {event.y} | key {event.key} | cells:", end=' ')
            if event.left_cell:
                print(f"l-({event.left_cell.x},{event.left_cell.y})", end=" ")
            if event.right_cell:
                print(f"r-({event.right_cell.x},{event.right_cell.y})")
            print()
            # print(f"event segments: {event.segments}")
            # print(self.output)
            if event.valid:
                if event.type == EventTypes.CELL:
                    self._process_cell(event)
                elif event.type == EventTypes.BEND:
                    self._process_bend(event)
                elif event.type == EventTypes.INTERSECTION:
                    self._process_intersection(event)
                else:
                    raise ValueError
                if event.type == EventTypes.CELL or event.type == EventTypes.INTERSECTION or \
                        (event.type == EventTypes.BEND and event.segments):

                    self._make_scene(key, event)

        self._finish_edges()
        self._make_scene(key, event)

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
        return Voronoi._get_lower_point(a, b)  # get the point which is not the end of the line

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
    def _is_in_segment(segment, point, eps=1e-10):
        segment = segment.copy()
        lower_y = segment[0][1]
        if lower_y > segment[1][1]:
            lower_y = segment[1][1]
        higher_y = segment[0][1]
        if higher_y < segment[1][1]:
            higher_y = segment[1][1]
        if (segment[0][0] - eps < point[0] < segment[1][0] + eps and
                lower_y - eps < point[1] < higher_y + eps):
            return True
        return False

    @staticmethod
    def _extract_line_part(line, a, b, eps=1e-6):
        newline = []
        if a[0] > b[0]:  # now point 'a' will always be before 'b'
            a, b = b, a
        started = False
        print(f"extracting between: {a}, {b}")
        for seg in line:
            for point in seg:
                s, e = point
                print(f"({s:.02f},{e:.02f})-", end=" ")
        print()
        for segment in line:
            print(not started, Voronoi._is_in_segment(segment, a, eps)
                    , not same_point(a, segment[1], eps), not Voronoi._is_in_segment(segment, b, eps))
            if (not started and Voronoi._is_in_segment(segment, a, eps)
                    and not same_point(a, segment[1], eps) and not Voronoi._is_in_segment(segment, b, eps)):
                if abs(a[0] - b[0]) < eps:
                    return [[a,b]]
                else:
                    newline.append((a, segment[1]))
                started = True
            elif started and not Voronoi._is_in_segment(segment, b, eps):
                newline.append(segment)
            elif started:
                newline.append((segment[0], b))
                break
        for seg in newline:
            for point in seg:
                s, e = point
                print(f"({s:.02f},{e:.02f})-", end=" ")
        print()
        if newline:
            return newline
        else:
            return [(a, b)]

    @staticmethod
    def _get_bottom_end(line):
        return Voronoi._get_lower_point(line[0][0], line[-1][-1])

    # utility method for invalidating events
    @staticmethod
    def _invalidate_events(key, left_n, right_n, middle):
        # todo check correctness
        if left_n.right_event:
            print(f"old {left_n.right_event.key} new {key}")
             # assert left_n.right_event.key < key
            print(f"invalidating {left_n.right_event.type} at {left_n.right_event.x}"
                  f"{left_n.right_event.y} segments"
                  f"{left_n.right_event.segments}")
            left_n.right_event.valid = False
        if right_n.left_event:
            print(f"old {right_n.left_event.key} new {key}")
            print(f"invalidating {right_n.left_event.type} at {right_n.left_event.x}"
                  f"{right_n.left_event.y} segments"
                  f"{right_n.left_event.segments}")
            #  assert right_n.left_event.key < key
            right_n.left_event.valid = False
        if middle.left_event:
            middle.left_event.valid = False
        if middle.right_event:
            middle.right_event.valid = False


    # event processing methods
    def _intersection_to_event(self, key, node, left_n, right_n, intersection):
        if -key < self._current_key - self._eps:
            print(f"not adding intersection at {intersection} | key {key} curr_key {self._current_key}")
            return False

        if type(node) == RBNode:
            node = node.value

        self._invalidate_events(key, left_n, right_n, node)
        # add intersection event
        # print("intersection to event extracting segments")
        segments = self._extract_line_part(left_n.right_bisector, left_n.right_point_used, intersection)
        d = distance(intersection, (node.x, node.y))
        if eq(intersection[1] + d, node.y, self._eps):  # node is on the top of a circle
            segments += self._extract_line_part(right_n.left_bisector, right_n.left_point_used, intersection)
        # print(f"segments: {segments}")
        event = Event(intersection[0], intersection[1], left_cell=left_n, right_cell=right_n,
                      segments=segments, point_type=EventTypes.INTERSECTION, key=key)
        print(f"add intersection at {intersection}")
        self.events.put((-key, event))

        # update info in tree nodes
        right_n.left_event = left_n.right_event = node.left_event = node.right_event = event
        return True

    def _process_cell(self, event):
        node = self.active_cells.findNode(event.x)
        if node:  # adding exactly below active cell point (rare)
            event.x += self._eps

        node = self.active_cells.insert(event.x)
        node.value = Cell(event.x, event.y)
        # print(f"node.value: {node.value}")
        new_events = []  # node.value is set later with events

        # get neighbours
        left_n = right_n = None
        left_n_key = self.active_cells.predecessor(event.x)
        if left_n_key:
            left_n = self.active_cells.findNode(left_n_key)
            if left_n.value.right_point_used:
                node.value.left_point_used = left_n.value.right_point_used
            # print(f"left_n.value: {left_n.value}")
        right_n_key = self.active_cells.successor(event.x)
        if right_n_key:
            right_n = self.active_cells.findNode(right_n_key)
            if right_n.value.left_point_used:
                node.value.right_point_used = right_n.value.left_point_used
            # print(f"right_n.value: {right_n.value}")

        # calculate bisectors
        cell_point = (node.value.x, node.value.y)
        intersection = line_left = line_right = None
        if left_n:
            left_point = (left_n.value.x, left_n.value.y)
            line_left = self._bisector(cell_point, left_point)
            print(f"left bis {line_left}")
        if right_n:
            right_point = (right_n.value.x, right_n.value.y)
            line_right = self._bisector(cell_point, right_point)
            print(f"right bis {line_right}")
        if line_right and line_left:
            intersection = cross(line_left, line_right)
            print(f"intersection: {intersection}")

        if intersection and intersection[1] < left_n.value.right_point_used[1] - self._eps and \
                intersection[1] < right_n.value.left_point_used[1] - self._eps:
            key = cell_point[1]  # cell_point is on the bottom of circle -> the event will be processed next
            self._intersection_to_event(key, node, left_n.value, right_n.value, intersection)
            node.value.left_point_used = node.value.right_point_used = intersection
        elif intersection:
            if left_n.value.left_bisector:
                intersection = cross(line_left, left_n.value.left_bisector)
                if intersection and intersection[1] - self._eps > event.y:
                    node.value.left_point_used = intersection
                    left_n.value.right_point_used = intersection
                else:
                    node.value.left_point_used = left_n.value.right_point_used
                    left_n.value.right_point_used = left_n.value.right_point_used
            if right_n.value.right_bisector:
                intersection = cross(right_n.value.right_bisector, line_right)
                if intersection and intersection[1] - self._eps > event.y:
                    node.value.right_point_used = intersection
                    right_n.value.left_point_used = intersection
                else:
                    node.value.right_point_used = right_n.value.left_point_used
                    right_n.value.left_point_used = right_n.value.left_point_used
        else:  # there is none or one neighbour
            line = None
            is_left = False
            if line_left:
                line = line_left
                is_left = True
            elif line_right:
                line = line_right

            if line:  # there is one neighbour
                if LineType.get_type(line) == LineType.HORIZONTAL_PART:
                    # gets segments that can be added to Voronoi diagram
                    segments = [self._get_top_segment(line)]
                    #    print(f"seg from horiztonal: {segments}")
                    event_x, event_y = self._get_top_point(line)
                    key = event_y + self._eps  # key is above current key -> it will be added to Voronoi diagram in the next step
                    print(f"adding bend with key = {key}")
                    if is_left:
                        event = Event(event_x, event_y, left_cell=left_n.value, right_cell=node.value,
                                      segments=segments, point_type=EventTypes.BEND, key=key)
                        left_n.value.right_point_used = (event_x, event_y)
                        node.value.left_point_used = (event_x, event_y)
                        node.value.left_event = event
                        left_n.value.right_event = event
                    else:
                        event = Event(event_x, event_y, left_cell=node.value, right_cell=right_n.value,
                                      segments=segments, point_type=EventTypes.BEND, key=key)
                        right_n.value.left_point_used = (event_x, event_y)
                        node.value.right_point_used = (event_x, event_y)
                        node.value.right_event = event
                        right_n.value.left_event = event
                    self.events.put((-key, event))
                elif LineType.get_type(line) == LineType.VERTICAL_PART:
                    segments = [self._get_top_segment(line)]
                    event_x, event_y = self._get_top_point(line)
                    key = event_y + self._eps  # key is above current key -> it will be added to Voronoi diagram in the next step
                    print(f"adding bend with key = {key}")

                    if is_left:
                        event = Event(event_x, event_y, left_cell=left_n.value, right_cell=node.value,
                                      segments=segments, point_type=EventTypes.BEND, key=key)
                        left_n.value.right_point_used = (event_x, event_y)
                        node.value.left_point_used = (event_x, event_y)
                        node.value.left_event = event
                        left_n.value.right_event = event
                    else:
                        event = Event(event_x, event_y, left_cell=node.value, right_cell=right_n.value,
                                      segments=segments, point_type=EventTypes.BEND, key=key)
                        right_n.value.left_point_used = (event_x, event_y)
                        node.value.right_point_used = (event_x, event_y)
                        node.value.right_event = event
                        right_n.value.left_event = event
                    self.events.put((-key, event))
                else: # line consisting of only one segment
                    segment = line[0]
                    top_point = self._get_higher_point(segment[0], segment[1])
                    event = Event(0, 0, point_type=EventTypes.BOUNDARY, segments=line)
                    self.boundary_events.append(event)
                    if left_n:
                        left_n.right_event = event
                        node.value.left_event = event
                        node.value.left_point_used = top_point
                    elif right_n:
                        right_n.left_event = event
                        node.value.right_event = event
                        node.value.right_point_used = top_point


        # update bisectors and events in tree nodes
        if line_left:
            # print(f"update {left_n.value}")
            left_n.value.right_bisector = line_left
            node.value.left_bisector = line_left
        if line_right:
            # print(f"update {right_n.value}")
            node.value.right_bisector = line_right
            right_n.value.left_bisector = line_right

    def _process_intersection(self, event):
        for segment in event.segments:
            self.output.append(segment)

        # get bisectors which intersect at this event
        left_bisector = event.left_cell.right_bisector
        right_bisector = event.right_cell.left_bisector

        mid_cell_key = self.active_cells.successor(event.left_cell.x)
        mid_node = self.active_cells.findNode(mid_cell_key)
        mid_cell = mid_node.value

        intersection = (event.x, event.y)

        # deleting cell from active cells if it's on top of the circle
        mid_delete = False
        d = distance(intersection, (mid_cell.x, mid_cell.y))
        if eq(intersection[1] + d, mid_cell.y, self._eps):
            mid_delete = True

        for (line, is_left) in zip([left_bisector, right_bisector], [True, False]):
            new_event = None
            x, y = event.x, event.y
            key = event.key
            if is_left:
                key += 1e-15  # avoiding key collision

            if mid_delete:
                new_event = Event(x, y, point_type=EventTypes.BEND, right_cell=event.right_cell,
                                  left_cell=event.left_cell,
                                  segments=[], key=key)
                # print(f"new event: left cell {event.left_cell.x}, {event.left_cell.y} right cell "
                #       f"{event.right_cell.x}, {event.right_cell.y} \nright cell events"
                #       f"{event.right_cell.left_event.type}, {event.right_cell.right_event.type}")
                self.events.put((-key, new_event))
                break
            elif is_left:
                new_event = Event(x, y, point_type=EventTypes.BEND, right_cell=mid_cell, left_cell=event.left_cell,
                                  segments=[], key=key)
            else:
                new_event = Event(x, y, point_type=EventTypes.BEND, right_cell=event.right_cell, left_cell=mid_cell,
                                  segments=[], key=key)
            if new_event:
                self.events.put((-key, new_event))
            else:  # add boundary event
                if is_left:
                    endpoint = self._get_bottom_end(line)
                    segments = self._extract_line_part(line, endpoint, event.left_cell.right_point_used)
                    # print(f"adding boundart event line: {line} | endpoint {endpoint} | pointused {event.left_cell.right_point_used}")
                else:
                    endpoint = self._get_bottom_end(line)
                    print(f"endpoint {endpoint}")
                    segments = self._extract_line_part(line, endpoint, event.right_cell.left_point_used)
                #   print(f"adding boundart event line: {line} | endpoint {endpoint} | pointused {event.right_cell.left_point_used}")
                self.boundary_events.append((Event(0, 0, point_type=EventTypes.BOUNDARY, segments=segments)))

        # deleting middle cell
        if mid_delete:
            print(f"deleting cell at {mid_cell.x}, {mid_cell.y} events types: l-{mid_cell.left_event.type}"
                  f"r-{mid_cell.right_event.type}")
            if mid_cell.left_event: mid_cell.left_event.valid = False
            if mid_cell.right_event: mid_cell.right_event.valid = False
            self.active_cells.deleteNode(mid_node)

            # update bisectors in cells
            new_bisector = self._bisector((event.left_cell.x, event.left_cell.y), (event.right_cell.x, event.right_cell.y))
            event.left_cell.right_bisector = new_bisector
            event.right_cell.left_bisector = new_bisector
        else:  # update mid cell information
            mid_node.left_point_used = intersection
            mid_node.right_point_used = intersection

        # update information
        event.left_cell.right_point_used = intersection
        event.right_cell.left_point_used = intersection

    def _process_bend(self, event):
        for segment in event.segments:
            self.output.append(segment)

        # update info
        event.left_cell.right_point_used = (event.x, event.y)
        event.right_cell.left_point_used = (event.x, event.y)

        line_left = event.left_cell.left_bisector
        line_right = event.right_cell.right_bisector
        event_line = event.left_cell.right_bisector
        print(f"bend lines: \n left: {line_left} \n mid: {event_line} \n right: {line_right}")
        add_boundary = True
        if line_left:
            intersection = cross(line_left, event_line)
            if intersection and not same_point(intersection, (event.x, event.y, self._eps)) and \
                    (intersection[1] < event.left_cell.right_point_used[1] - self._eps or
                     intersection[1] < event.left_cell.left_point_used[1] - self._eps):
                print(f"bend event: (left) intersection found at {intersection}")
                print(f"left point used: {event.left_cell.left_point_used} right: {event.left_cell.right_point_used}")
                mid_cell = event.left_cell  # mid cell is on top of the circle
                left_cell_key = self.active_cells.predecessor(event.left_cell.x)
                left_cell = self.active_cells.findNode(left_cell_key).value
                d = distance(intersection, (mid_cell.x, mid_cell.y))
                key = intersection[1] - d
                added = self._intersection_to_event(key, mid_cell, left_cell, event.right_cell, intersection)
                if added:
                    add_boundary = False
        if line_right:
            intersection = cross(line_right, event_line)
            if intersection and not same_point(intersection, (event.x, event.y)) and \
                    (intersection[1] < event.right_cell.right_point_used[1] - self._eps or
                    intersection[1] < event.right_cell.left_point_used[1] - self._eps):
                print(f"bend event: (right) intersection found at {intersection}")
                print(f"left point used: {event.right_cell.left_point_used} right: {event.right_cell.right_point_used}")
                mid_cell = event.right_cell
                right_cell_key = self.active_cells.successor(event.right_cell.x)
                right_cell = self.active_cells.findNode(right_cell_key).value
                d = distance(intersection, (mid_cell.x, mid_cell.y))
                key = intersection[1] - d
                added = self._intersection_to_event(key, mid_cell, event.left_cell, right_cell, intersection)
                if added:
                    add_boundary = False
        if add_boundary:
            endpoint = self._get_bottom_end(event_line)
            print(f"bend add bound endpoint: {endpoint} | line: {event_line}")
            segments = self._extract_line_part(event_line, endpoint, event.right_cell.left_point_used)
            print(f"add bound | line {event_line} | a {endpoint} | b {event.right_cell.left_point_used}")
            new_event = Event(0, 0, point_type=EventTypes.BOUNDARY, segments=segments, key=-99999)
            event.left_cell.right_event = new_event
            event.right_cell.left_event = new_event
            self.boundary_events.append(new_event)

    def _process_bound(self, event):
        for segment in event.segments:
            self.output.append(segment)

    # other
    def _finish_edges(self):
        self._broom_location = -999999
        for event in self.boundary_events:
            print(
                f"processing boundary event at {event.x}, {event.y} | valid={event.valid} | segments: {event.segments}")
            if event.valid:
                self._process_bound(event)



def get_points():
    plot = PlotFirst()
    plot.draw()
    points = plot.get_added_points()[0].points
    #print(points)
    points = np.array(points, dtype=np.float64)
    idx = np.argsort(points[:, 1])
    idx = np.flip(idx)
    return points[idx, :]


if __name__ == "__main__":
    points = get_points()
    voronoi = Voronoi(points)
    voronoi.process()
    plot = PlotSecond(voronoi.scenes)
    plot.draw()
