import matplotlib.pyplot as plt
import heapq
from decimal import Decimal
from enum import Enum
from bstree import BSTree


ZERO = Decimal()
INF = Decimal("inf")


class Point:
    def __init__(self, x, y):
        self.x = x
        self.y = y

    def __lt__(self, other):
        return [self.x, self.y] < [other.x, other.y]

    def __eq__(self, other):
        return self.x == other.x and self.y == other.y

    def __hash__(self):
        return hash((self.x, self.y))

    def __str__(self):
        return f"({self.x}; {self.y})"


class Segment:
    def __init__(self, begin, end):
        self.begin = min(begin, end)
        self.end = max(begin, end)

    def __eq__(self, other):
        return self.begin == other.begin and self.end == other.end

    def __hash__(self):
        return hash((self.begin, self.end))

    def __str__(self):
        return f"{self.begin} -> {self.end}"

    def plot(self):
        plt.plot(
            [self.begin.x, self.end.x],
            [self.begin.y, self.end.y],
            "-b"
        )

    def value(self, x):
        k, b = self.to_line()

        return k * x + b

    def to_line(self):
        dx = self.end.x - self.begin.x

        # in this case method returns line in view x=b, where b=begin.x
        if dx == ZERO:
            return INF, self.begin.x

        dy = self.end.y - self.begin.y
        k = dy / dx

        b = self.begin.y - k * self.begin.x

        return k, b

    def compare_in_x(self, other, x):
        return self.value(x) < other.value(x)

    def projections_contain(self, point):
        x_begin, x_end = self.__projection("x")
        y_begin, y_end = self.__projection("y")

        return x_begin <= point.x <= x_end and y_begin <= point.y <= y_end

    def __projection(self, axis):
        if axis == "x":
            return min(self.begin.x, self.end.x), max(self.begin.x, self.end.x)

        return min(self.begin.y, self.end.y), max(self.begin.y, self.end.y)

    def get_endpoints(self):
        return self.begin, self.end


class Utils:
    @staticmethod
    def find_intersection(first, second):
        if first is None or second is None:
            return None

        k_1, b_1 = first.to_line()
        k_2, b_2 = second.to_line()

        if k_1 == k_2:
            return None

        if k_1 == INF:
            x = b_1
            y = k_2 * x + b_2
        elif k_2 == INF:
            x = b_2
            y = k_1 * x + b_1
        else:
            x = (b_2 - b_1) / (k_1 - k_2)
            y = k_1 * (b_2 - b_1) / (k_1 - k_2) + b_1

        intersection = Point(x, y)

        if first.projections_contain(intersection) \
                and second.projections_contain(intersection):
            return intersection

        return None


class EventType(Enum):
    BEGIN = 1
    END = 2
    INTERSECTION = 3


class Event:
    def __init__(self, point, segments, event_type):
        self.point = point
        self.segments = segments
        self.event_type = event_type

    def __lt__(self, other):
        return self.point < other.point


class SegmentComparator:
    def __init__(self, x=ZERO):
        self.x = x

    def key(self, segment):
        return segment.value(self.x)


class StatusStructure:
    def __init__(self):
        self.comparator = SegmentComparator()
        self.tree = BSTree()
        self.segments = dict()

    def set_x(self, x):
        self.comparator.x = x

    def insert(self, segment):
        inserted_node = self.tree.insert(segment,
                                         lambda e, c=self.comparator: c.key(e))
        self.segments[segment] = inserted_node

    def delete(self, segment):
        node_to_delete = self.segments[segment]
        self.tree.remove(node_to_delete)
        self.segments.pop(segment)

    def next(self, segment):
        node = self.segments[segment]
        next_node = self.tree.successor(node)

        if next_node is None:
            return None

        return next_node.value

    def prev(self, segment):
        node = self.segments[segment]
        prev_node = self.tree.predecessor(node)

        if prev_node is None:
            return None

        return prev_node.value

    def swap(self, lhs, rhs):
        if lhs not in self.segments and rhs not in self.segments:
            return

        lhs_node = self.segments[lhs]
        rhs_node = self.segments[rhs]

        lhs_node.value, rhs_node.value = rhs_node.value, lhs_node.value
        self.segments[lhs], self.segments[rhs] = rhs_node, lhs_node


class IntersectionDeterminator:
    def __init__(self, segments):
        self.segments = segments
        self.event_queue = []
        self.status = StatusStructure()
        self.result = []

    def demo(self):
        self.__plot_segments()
        self.__init_event_queue()
        self.__find_intersections()
        self.__plot_intersections()
        self.__report()

        plt.show()

    def __plot_segments(self):
        for segment in self.segments:
            segment.plot()

    def __init_event_queue(self):
        for segment in self.segments:
            begin, end = segment.get_endpoints()
            self.event_queue.append(Event(begin, (segment,), EventType.BEGIN))
            self.event_queue.append(Event(end, (segment,), EventType.END))

        heapq.heapify(self.event_queue)

    def __find_intersections(self):
        while len(self.event_queue) != 0:
            event = heapq.heappop(self.event_queue)
            point = event.point
            self.status.set_x(point.x)

            if event.event_type == EventType.BEGIN:
                self.__handle_begin_event(event)
            elif event.event_type == EventType.END:
                self.__handle_end_event(event)
            elif event.event_type == EventType.INTERSECTION:
                self.__handle_intersection_event(event)

    def __handle_begin_event(self, event):
        segment = event.segments[0]
        self.status.insert(segment)

        segment_above = self.status.next(segment)
        segment_below = self.status.prev(segment)

        above_current = Utils.find_intersection(segment_above, segment)
        below_current = Utils.find_intersection(segment_below, segment)

        if above_current is not None:
            self.__add_event(
                Event(above_current,
                      (segment, segment_above),
                      EventType.INTERSECTION)
            )

        if below_current is not None:
            self.__add_event(
                Event(below_current,
                      (segment_below, segment),
                      EventType.INTERSECTION)
            )

    def __add_event(self, event):
        heapq.heappush(self.event_queue, event)

    def __handle_end_event(self, event):
        point = event.point
        segment = event.segments[0]
        segment_above = self.status.next(segment)
        segment_below = self.status.prev(segment)

        self.status.delete(segment)

        above_below = Utils.find_intersection(segment_above, segment_below)

        if above_below is not None \
                and point.x < above_below.x \
                and self.__is_not_in_queue(above_below):
            self.__add_event(
                Event(above_below,
                      (segment_below, segment_above),
                      EventType.INTERSECTION)
            )

    def __is_not_in_queue(self, point):
        return next(
            (e for e in self.event_queue if e.point == point),
            None
        ) is None

    def __handle_intersection_event(self, event):
        point = event.point
        self.result.append(point)

        lhs, rhs = event.segments
        self.status.swap(lhs, rhs)  # lhs < rhs -> rhs < lhs

        segment_above = self.status.next(lhs)
        segment_below = self.status.prev(rhs)

        above_lhs = Utils.find_intersection(segment_above, lhs)
        below_rhs = Utils.find_intersection(segment_below, rhs)

        if above_lhs is not None \
                and point.x < above_lhs.x \
                and self.__is_not_in_queue(above_lhs):
            self.__add_event(
                Event(above_lhs, (lhs, segment_above), EventType.INTERSECTION)
            )

        if below_rhs is not None \
                and point.x < below_rhs.x \
                and self.__is_not_in_queue(below_rhs):
            self.__add_event(
                Event(below_rhs, (segment_below, rhs), EventType.INTERSECTION)
            )

    def __plot_intersections(self):
        for point in self.result:
            plt.scatter(point.x, point.y, color="red")

    def __report(self):
        print(f"Count: {len(self.result)}")
        print("Intersections: ")

        for point in self.result:
            print(point)


def create_segment(x_begin, y_begin, x_end, y_end):
    return Segment(Point(Decimal(x_begin),
                         Decimal(y_begin)),
                   Point(Decimal(x_end),
                         Decimal(y_end)))


def main():
    segments = [
        create_segment(-3, 0, 2, 1),
        create_segment(1, 5, 3, 3),
        create_segment(0, 5, 2, 0),
        create_segment(1, 2, 2, 7),
        create_segment(-2, 1, 3, 0),
        create_segment(3, 5, -3, -1),
        create_segment(-0.5, -1, 0, 3),
        create_segment(0, 4, 1, 7),
        create_segment(-4, -0.5, 3, -0.5),
        create_segment(-1, 4.5, 1.5, 0),
        create_segment(-2, 3.5, 4, 3.5),
        create_segment(2, 5, 4, 2),
        create_segment(2, -1, 4, 5),
        create_segment(-1, 3, -0.5, 5)
    ]

    intersection_determinator = IntersectionDeterminator(segments)
    intersection_determinator.demo()

    plt.show()


if __name__ == "__main__":
    main()
