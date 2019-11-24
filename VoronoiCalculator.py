import numpy as np
import matplotlib.pyplot as plt
import matplotlib.collections as mcoll
import matplotlib.colors as mcolors
from matplotlib.widgets import Button
import json as js
from queue import PriorityQueue
from DataType import *
from RBTree import *
from MaxMetric import *

class Scene:
    def __init__(self, points=[], lines=[]):
        self.points = points
        self.lines = lines


class PointsCollection:
    def __init__(self, points, **kwargs):
        self.points = points
        self.kwargs = kwargs

    def add_points(self, points):
        self.points = self.points + points


class LinesCollection:
    def __init__(self, lines, **kwargs):
        self.lines = lines
        self.kwargs = kwargs

    def add(self, line):
        self.lines.append(line)

    def get_collection(self):
        return mcoll.LineCollection(self.lines, **self.kwargs)


class Plot:
    def __init__(self, scenes=[Scene()], json=None):
        if json is None:
            self.scenes = scenes
        else:
            self.scenes = [Scene([PointsCollection(pointsCol) for pointsCol in scene["points"]],
                                 [LinesCollection(linesCol) for linesCol in scene["lines"]])
                           for scene in js.loads(json)]

    def __configure_buttons(self):
        plt.subplots_adjust(bottom=0.2)
        ax_prev = plt.axes([0.6, 0.05, 0.15, 0.075])
        ax_next = plt.axes([0.76, 0.05, 0.15, 0.075])
        ax_add_point = plt.axes([0.44, 0.05, 0.15, 0.075])
        ax_add_line = plt.axes([0.28, 0.05, 0.15, 0.075])
        ax_add_rect = plt.axes([0.12, 0.05, 0.15, 0.075])
        b_next = Button(ax_next, 'Następny')
        b_next.on_clicked(self.callback.next)
        b_prev = Button(ax_prev, 'Poprzedni')
        b_prev.on_clicked(self.callback.prev)
        b_add_point = Button(ax_add_point, 'Dodaj punkt')
        b_add_point.on_clicked(self.callback.add_point)
        b_add_line = Button(ax_add_line, 'Dodaj linię')
        b_add_line.on_clicked(self.callback.add_line)
        b_add_rect = Button(ax_add_rect, 'Dodaj figurę')
        b_add_rect.on_clicked(self.callback.add_rect)
        return [b_prev, b_next, b_add_point, b_add_line, b_add_rect]

    def add_scene(self, scene):
        self.scenes.append(scene)

    def add_scenes(self, scenes):
        self.scenes = self.scenes + scenes

    def toJson(self):
        return js.dumps([{"points": [np.array(pointCol.points).tolist() for pointCol in scene.points],
                          "lines": [linesCol.lines for linesCol in scene.lines]}
                         for scene in self.scenes])

    def get_added_points(self):
        if self.callback:
            return self.callback.added_points
        else:
            return None

    def get_added_lines(self):
        if self.callback:
            return self.callback.added_lines
        else:
            return None

    def get_added_figure(self):
        if self.callback:
            return self.callback.added_rects
        else:
            return None

    def get_added_elements(self):
        if self.callback:
            return Scene(self.callback.added_points, self.callback.added_lines + self.callback.added_rects)
        else:
            return None

    def draw(self):
        plt.close()
        fig = plt.figure()
        self.callback = _Button_callback(self.scenes)
        self.widgets = self.__configure_buttons()
        ax = plt.axes(autoscale_on=False)
        self.callback.set_axes(ax)
        fig.canvas.mpl_connect('button_press_event', self.callback.on_click)
        plt.show()
        self.callback.draw()

FIG_EPS = 0.5


def dist(point1, point2):
    return np.sqrt(np.power(point1[0] - point2[0], 2) + np.power(point1[1] - point2[1], 2))


class _Button_callback(object):
    def __init__(self, scenes):
        self.i = 0
        self.scenes = scenes
        self.adding_points = False
        self.added_points = []
        self.adding_lines = False
        self.added_lines = []
        self.adding_rects = False
        self.added_rects = []

    def set_axes(self, ax):
        self.ax = ax

    def next(self, event):
        self.i = (self.i + 1) % len(self.scenes)
        self.draw(autoscaling=True)

    def prev(self, event):
        self.i = (self.i - 1) % len(self.scenes)
        self.draw(autoscaling=True)

    def add_point(self, event):
        self.adding_points = not self.adding_points
        self.new_line_point = None
        if self.adding_points:
            self.adding_lines = False
            self.adding_rects = False
            self.added_points.append(PointsCollection([]))

    def add_line(self, event):
        self.adding_lines = not self.adding_lines
        self.new_line_point = None
        if self.adding_lines:
            self.adding_points = False
            self.adding_rects = False
            self.added_lines.append(LinesCollection([]))

    def add_rect(self, event):
        self.adding_rects = not self.adding_rects
        self.new_line_point = None
        if self.adding_rects:
            self.adding_points = False
            self.adding_lines = False
            self.new_rect()

    def new_rect(self):
        self.added_rects.append(LinesCollection([]))
        self.rect_points = []

    def on_click(self, event):
        if event.inaxes != self.ax:
            return
        new_point = (event.xdata, event.ydata)
        if self.adding_points:
            self.added_points[-1].add_points([new_point])
            self.draw(autoscaling=False)
        elif self.adding_lines:
            if self.new_line_point is not None:
                self.added_lines[-1].add([self.new_line_point, new_point])
                self.new_line_point = None
                self.draw(autoscaling=False)
            else:
                self.new_line_point = new_point
        elif self.adding_rects:
            if len(self.rect_points) == 0:
                self.rect_points.append(new_point)
            elif len(self.rect_points) == 1:
                self.added_rects[-1].add([self.rect_points[-1], new_point])
                self.rect_points.append(new_point)
                self.draw(autoscaling=False)
            elif len(self.rect_points) > 1:
                if dist(self.rect_points[0], new_point) < FIG_EPS:
                    self.added_rects[-1].add([self.rect_points[-1], self.rect_points[0]])
                    self.new_rect()
                else:
                    self.added_rects[-1].add([self.rect_points[-1], new_point])
                    self.rect_points.append(new_point)
                self.draw(autoscaling=False)

    def draw(self, autoscaling=True):
        if not autoscaling:
            xlim = self.ax.get_xlim()
            ylim = self.ax.get_ylim()
        self.ax.clear()
        for collection in (self.scenes[self.i].points + self.added_points):
            if len(collection.points) > 0:
                self.ax.scatter(*zip(*(np.array(collection.points))), **collection.kwargs)
        for collection in (self.scenes[self.i].lines + self.added_lines + self.added_rects):
            self.ax.add_collection(collection.get_collection())
        self.ax.autoscale(autoscaling)
        if not autoscaling:
            self.ax.set_xlim(xlim)
            self.ax.set_ylim(ylim)
        plt.draw()


class Voronoi:
    def __init__(self, points):
        self.output = []  # list of line segment

        self.events = PriorityQueue()
        self.active_cells = RBTree()

        # bounding box
        self.x0 = 0.5
        self.x1 = 0.5
        self.y0 = 0.5
        self.y1 = 0.5

        # insert points to site event
        for (x, y) in points:
            self.events.push((-y, Event(x=x, y=y, point_type=PointTypes.CELL)))
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

    def process(self):
        while not self.events.empty():
            event = event.get()
            if event.valid:
                if event.type == PointTypes.CELL:
                    self._process_cell(event)
                elif event.type == PointTypes.BEND:
                    self._process_bend(event)
                elif event.type == PointTypes.INTERSECTION:
                    self._process_intersection(event)
                else:
                    print("UNIMPLEMENTED EVENT")  # for intersections with boundary?
                
        self.finish_edges() # TODO check what it does; is it useless?

    @staticmethod
    def _get_bot_segment(line): # TODO probably delete
        if line[1][1] > line[2][1]:
            return line[2:]
        else:
            return line[:2]

    @staticmethod
    def _get_mid_segment(line):
        return line[1:3]

    @staticmethod
    def _get_top_segment(line):
        if LineType.get_type(line) == LineType.VERTICAL_PART:
            if line[1][1] > line[2][1]:
                return line[:2]
            else:
                return line[2:]
        if LineType.get_type(line) == LineType.HORIZONTAL_PART:
            if line[0][1] > line[3][1]:
                return line[:2]
            else:
                return line[2:]

    @staticmethod
    def _get_top_point(line):
        """gets point on line which is closest to the top end of the line"""
        top_segment = Voronoi._get_top_segment(line)
        return top_segment[1]

    @staticmethod
    def _get_bot_point(line):
        """gets point on line which is closest to the bottom end of the line"""
        if LineType.get_type(line) == LineType.VERTICAL_PART:
            return Voronoi._get_lower_point(line[1], line[2])
        if LineType.get_type(line) == LineType.HORIZONTAL_PART:
            if line[0][1] > line[3][1]:
                return line[2]
            else:
                return line[1]

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
    def _segments_from_horizontal(line):
        return [Voronoi._get_top_segment(line), Voronoi._get_mid_segment(line)]

    # calculates segment for voronoi
    def _process_line(self, line, cell):
        events = []
        line_type = LineType.get_type(line)
        if line_type == LineType.VERTICAL: #  only one segment
            # TODO
            pass
        elif line_type == LineType.HORIZONTAL:
            # TODO
            pass
        elif line_type == LineType.VERTICAL_PART:
            # add top to voronoi
            line_top = self._get_top_segment(line)
            self.output.append(line_top)
            # add bot to events
            bot_point = self._get_bot_point(line)
            mid_segment = self._get_mid_segment(line)
            dist = self.metric.distance(bot_point, cell)
            event = Event(x=bot_point[0], y=bot_point[1], point_type=PointTypes.BEND, segment=mid_segment)
            self.events.push((bot_point[1] - dist, event))

            pass
        elif line_type == LineType.HORIZONTAL_PART:
            # add both to voronoi
            for segment in self._segments_from_horizontal(line):
                self.output.append(segment)
            pass
        elif line_type == LineType.INCLINED:
            # TODO
            pass
        else:
            # should never occur
            raise AssertionError
        return event
    
    def _cut_to_intersection(self, line, intersection, use_left):
        # TODO 
        pass

    def _process_intersection(self, intersection, line_pred, line_succ): # todo write from scratch
        unused_segments = []
        for use_left, line in zip([True, False], [line_pred, line_succ]):
            line = line.copy()
            assert len(line) == 4  # not horizontal, vertical nor diagonal
            unused, line = self._cut_to_intersection(line, intersection, use_left)
            unused_segments.append(unused)
            for segment in line:
                self.output.append(segment)
        event = Event(intersection[0], intersection[1], point_type=PointTypes.MID, segments=unused_segments)

    @staticmethod
    def _is_above(a, b):
        """checks if a is above b"""
        return a[1] > b[1]

    def _process_cell(self, event):
        node = self.active_cells.findNode(event.x)
        if node:  # adding exactly below active cell point (rare)
            # TODO
            pass

        node = self.active_cells.insert(event.x)
        node.value = Cell(event.x, event.y)
        new_events = []  # node.value is set later with events

        # get neighbours
        left_n = self.active_cells.predecessor(event.x)
        right_n = self.active_cells.successor(event.x)

        # calculate bisectors
        cell_point = (node.value.x, node.value.y)
        left_point = (left_n.value.x, right_n.value.y)
        right_point = (right_n.value.x, left_n.value.y)
        line_left = self.metric.bisector(cell_point, left_point)
        line_right = self.metric.bisector(cell_point, right_point)

        if line_right and line_left:
            intersection = self.metric.getCross(line_left, line_right)

        if intersection: # TODO make function that does it
            key = cell_point[1]  # cell point is on circle bottom (because its in between the other 2 points)
            self._invalidate_events(key, left_n, right_n)

            # add intersection event
            segments = self._get_line_part(start=left_n.value.right_point_used, end=intersection,
                                          line=left_n.value.right_bisector)
            event = Event(intersection[0], intersection[1], left_cell=left_n.value, right_cell=right_n.value,
                          segments=segments, point_type=PointTypes.INTERSECTION, key=key)

            key += 1  # intersection point should be put into voronoi diagram as the next event
            self.events.push((-key, event))

            # update info in tree nodes
            left_n.value.right_point_used = intersection
            right_n.value.left_point_used = intersection
            node.value.left_point_used = intersection
            node.value.right_point_used = intersection
            node.value.left_event = node.value.right_event = event
        else:  # there is none or one neighbour
            # TODO make function that does this part
            # TODO make sure it's not a possible situation if left and right neighbours exist
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

                    event_x, event_y = self._get_bot_point(line)
                    key = event_y # key is above current key -> it will be added to Voronoi diagram in the next step
                    if is_left:
                        event = Event(event_x, event_y,  left_cell=left_n.value, right_cell=node.value,
                                      segments=segments, point_type=PointTypes.BEND, key=key)
                        left_n.value.right_point_used = (event_x, event_y)
                        node.value.left_point_used = (event_x, event_y)
                        node.value.left_event = event
                    else:
                        event = Event(event_x, event_y,  left_cell=node.value, right_cell=right_n.value,
                                      segments=segments, point_type=PointTypes.BEND, key=key)
                        right_n.value.left_point_used = (event_x, event_y)
                        node.value.right_point_used = (event_x, event_y)
                        node.value.right_event = event
                    self.events.push((-key, event))
                elif LineType.get_type(line) == LineType.VERTICAL_PART:
                    segments = [self._get_top_segment(line)]
                    event_x, event_y = self._get_top_point(line)
                    key = event_y  # key is above current key -> it will be added to Voronoi diagram in the next step

                    if is_left:
                        event = Event(event_x, event_y, left_cell=left_n.value, right_cell=node.value,
                                      segments=segments, point_type=PointTypes.BEND, key=key)
                        left_n.value.right_point_used = (event_x, event_y)
                        node.value.left_point_used = (event_x, event_y)
                        node.value.left_event = event
                    else:
                        event = Event(event_x, event_y, left_cell=node.value, right_cell=right_n.value,
                                      segments=segments, point_type=PointTypes.BEND, key=key)
                        right_n.value.left_point_used = (event_x, event_y)
                        node.value.right_point_used = (event_x, event_y)
                        node.value.right_event = event
                    self.events.push((-key, event))
                else:
                    # TODO process other types of lines
                    pass

        # update bisectors and events in tree nodes
        if line_left:
            left_n.value.right_bisector = line_left
            node.value.left_bisector = line_left
        if line_right:
            node.value.right_bisector = line_right
            right_n.value.left_bisector = line_right

    def _process_intersection(self, event):
        for segment in event.segments:
            self.output.append(segment)

        # TODO check for intersections with left bisector of left cell and right bisector of right cell
        # if intersection
        #   add intersection event
        # else
        #   add bend/boundary events
    def process_event(self):
        # get next event from circle pq
        event = self.event.pop()

        if event.valid:
            if event.point_type == PointTypes.CELL:
                # push to active_cells
                node = self.active_cells.findNode(event.x)
                if node: # adding exactly below active cell point (rare)
                    # TODO
                    pass
                node = self.active_cells.insert(event.x)
                new_events = []  # node.value is set later with events

                # get neighbours
                pred = self.active_cells.predecessor(event.x)
                succ = self.active_cells.successor(event.x)

                # calculate bisectors
                cell_point = (node.value.x, node.value.y)
                pred_point = (pred.value.x, pred.value.y)
                succ_point = (succ.value.x, succ.value.y)
                line_pred = self.metric.bisector(cell_point, pred_point)
                line_succ = self.metric.bisector(cell_point, succ_point)
                # line format - ordered list of points starts from left (or bottom)

                # calculate middle point (if it exists)
                intersection = None
                if line_pred and line_succ:
                    intersection = self.metric.getCross(line_pred, line_succ)
                    key = self.metric(intersection, cell_point)
                    self.events.push((-key, Event(x=event.x, y=event.y, point_type=PointTypes.MID)))

                # add calculated points to Voronoi or events
                if not intersection:
                    for line in [line_pred, line_succ]:
                        # adds points to events and voronoi
                        event = self._process_line(line, self._get_lower_point(pred.value, succ.value))
                        if event:
                            assert type(event) != list
                            new_events.append[event]
                else:  # there is intersection point
                    # adds only points before the intersections (close to cell point)
                    event = self._process_intersection(intersection, line_pred, line_succ)
                    if event:
                        new_events.append(event)

                # TODO:  flag some events as invalid; use node.value.events

                node.value = Cell(event.x, event.y, new_events)  # what else should be here?
            else: # bending/middle point
                # TODO
                pass






    def finish_edges(self):
        l = self.x1 + (self.x1 - self.x0) + (self.y1 - self.y0)
        i = self.arc
        while i.pnext is not None:
            if i.s1 is not None:
                p = self.intersection(i.p, i.pnext.p, l * 2.0)
                i.s1.finish(p)
            i = i.pnext

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
    