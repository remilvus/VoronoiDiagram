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
        self.arc = None  # binary tree for parabola arcs

        self.events = PriorityQueue()
        self.broom = RBTree()

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
            self.process_event()  # handle circle event

        self.finish_edges()

    @staticmethod
    def _get_bot_segment(line):
        if line[1][1] > line[2][1]:
            return line[2:]
        else:
            return line[:2]

    @staticmethod
    def _get_mid_segment(line):
        return line[1:3]

    @staticmethod
    def _get_top_segment(line):
        if line[1][1] > line[2][1]:
            return line[:2]
        else:
            return line[2:]

    @staticmethod
    def _get_top_point(line):
        if line[1][1] > line[2][1]:
            return line[1]
        else:
            return line[2]

    @staticmethod
    def _get_bot_point(line):
        if line[1][1] > line[2][1]:
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

    def _process_intersection(self, intersection, line_pred, line_succ):
        unused_segments = []
        for use_left, line in zip([True, False], [line_pred, line_succ]):
            line = line.copy()
            assert len(line) == 4  # not horizontal, vertical nor diagonal
            unused, line = self._cut_to_intersection(line, intersection, use_left)
            unused_segments.append(unused)
            for segment in line:
                self.output.append(segment)
        event = Event(intersection[0], intersection[1], point_type=PointTypes.MID, segments=unused_segments)
        # TODO make sure the middle point 

    def process_event(self):
        # get next event from circle pq
        event = self.event.pop()

        if event.valid:
            if event.point_type == PointTypes.CELL:
                # push to broom
                node = self.broom.findNode(event.x)
                if node: # adding exactly below active cell point (rare)
                    # TODO
                    pass
                node = self.broom.insert(event.x)
                new_events = []  # node.value is set later with events

                # get neighbours
                pred = self.broom.predecessor(event.x)
                succ = self.broom.successor(event.x)

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


            # CELL new edge
            s = Segment(e.p)
            self.output.append(s)

            # remove associated arc (parabola)
            a = e.a
            if a.pprev is not None:
                a.pprev.pnext = a.pnext
                a.pprev.s1 = s
            if a.pnext is not None:
                a.pnext.pprev = a.pprev
                a.pnext.s0 = s

            # finish the edges before and after a
            if a.s0 is not None: a.s0.finish(e.p)
            if a.s1 is not None: a.s1.finish(e.p)

            # recheck circle events on either side of p
            if a.pprev is not None: self.check_circle_event(a.pprev, e.x)
            if a.pnext is not None: self.check_circle_event(a.pnext, e.x)

    def arc_insert(self, p):
        if self.arc is None:
            self.arc = Arc(p)
        else:
            # find the current arcs at p.y
            i = self.arc
            while i is not None:
                flag, z = self.intersect(p, i)
                if flag:
                    # new parabola intersects arc i
                    flag, zz = self.intersect(p, i.pnext)
                    if (i.pnext is not None) and (not flag):
                        i.pnext.pprev = Arc(i.p, i, i.pnext)
                        i.pnext = i.pnext.pprev
                    else:
                        i.pnext = Arc(i.p, i)
                    i.pnext.s1 = i.s1

                    # add p between i and i.pnext
                    i.pnext.pprev = Arc(p, i, i.pnext)
                    i.pnext = i.pnext.pprev

                    i = i.pnext  # now i points to the new arc

                    # add new half-edges connected to i's endpoints
                    seg = Segment(z)
                    self.output.append(seg)
                    i.pprev.s1 = i.s0 = seg

                    seg = Segment(z)
                    self.output.append(seg)
                    i.pnext.s0 = i.s1 = seg

                    # check for new circle events around the new arc
                    self.check_circle_event(i, p.x)
                    self.check_circle_event(i.pprev, p.x)
                    self.check_circle_event(i.pnext, p.x)

                    return

                i = i.pnext

            # if p never intersects an arc, append it to the list
            i = self.arc
            while i.pnext is not None:
                i = i.pnext
            i.pnext = Arc(p, i)

            # insert new segment between p and i
            x = self.x0
            y = (i.pnext.p.y + i.p.y) / 2.0;
            CELL = Point(x, y)

            seg = Segment(CELL)
            i.s1 = i.pnext.s0 = seg
            self.output.append(seg)

    def check_circle_event(self, i, x0):
        # look for a new circle event for arc i
        if (i.e is not None) and (i.e.x != self.x0):
            i.e.valid = False
        i.e = None

        if (i.pprev is None) or (i.pnext is None): return

        flag, x, o = self.circle(i.pprev.p, i.p, i.pnext.p)
        if flag and (x > self.x0):
            i.e = Event(x, o, i)
            self.event.push(i.e)

    def circle(self, a, b, c):
        # check if bc is a "right turn" from ab
        if ((b.x - a.x) * (c.y - a.y) - (c.x - a.x) * (b.y - a.y)) > 0: return False, None, None

        # Joseph O'Rourke, Computational Geometry in C (2nd ed.) p.189
        A = b.x - a.x
        B = b.y - a.y
        C = c.x - a.x
        D = c.y - a.y
        E = A * (a.x + b.x) + B * (a.y + b.y)
        F = C * (a.x + c.x) + D * (a.y + c.y)
        G = 2 * (A * (c.y - b.y) - B * (c.x - b.x))

        if (G == 0): return False, None, None  # Points are co-linear

        # point o is the center of the circle
        ox = 1.0 * (D * E - B * F) / G
        oy = 1.0 * (A * F - C * E) / G

        # o.x plus radius equals max x coord
        x = ox + math.sqrt((a.x - ox) ** 2 + (a.y - oy) ** 2)
        o = Point(ox, oy)

        return True, x, o

    def intersect(self, p, i):
        # check whether a new parabola at point p intersect with arc i
        if (i is None): return False, None
        if (i.p.x == p.x): return False, None

        a = 0.0
        b = 0.0

        if i.pprev is not None:
            a = (self.intersection(i.pprev.p, i.p, 1.0 * p.x)).y
        if i.pnext is not None:
            b = (self.intersection(i.p, i.pnext.p, 1.0 * p.x)).y

        if ((i.pprev is None) or (a <= p.y)) and ((i.pnext is None) or (p.y <= b)):
            py = p.y
            px = 1.0 * ((i.p.x) ** 2 + (i.p.y - py) ** 2 - p.x ** 2) / (2 * i.p.x - 2 * p.x)
            res = Point(px, py)
            return True, res
        return False, None

    def intersection(self, p0, p1, l):
        # get the intersection of two parabolas
        p = p0
        if (p0.x == p1.x):
            py = (p0.y + p1.y) / 2.0
        elif (p1.x == l):
            py = p1.y
        elif (p0.x == l):
            py = p0.y
            p = p1
        else:
            # use quadratic formula
            z0 = 2.0 * (p0.x - l)
            z1 = 2.0 * (p1.x - l)

            a = 1.0 / z0 - 1.0 / z1;
            b = -2.0 * (p0.y / z0 - p1.y / z1)
            c = 1.0 * (p0.y ** 2 + p0.x ** 2 - l ** 2) / z0 - 1.0 * (p1.y ** 2 + p1.x ** 2 - l ** 2) / z1

            py = 1.0 * (-b - math.sqrt(b * b - 4 * a * c)) / (2 * a)

        px = 1.0 * (p.x ** 2 + (p.y - py) ** 2 - l ** 2) / (2 * p.x - 2 * l)
        res = Point(px, py)
        return res

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
    