from decimal import Decimal
from enum import Enum
from sortedcontainers import SortedList
import bisect
import matplotlib.pyplot as plt
import heapq


ZERO = Decimal()
INF = Decimal("inf")


class Point:
    def __init__(self, x, y):
        self.x = x
        self.y = y

    def __lt__(self, other):
        return [self.x, self.y] < [other.x, other.y]

    def __str__(self):
        return f"({self.x}; {self.y})"


class Segment:
    def __init__(self, begin, end):
        self.begin = min(begin, end)
        self.end = max(begin, end)

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
    def __init__(self, point, segment, event_type):
        self.point = point
        self.segment = segment
        self.event_type = event_type

    def __lt__(self, other):
        return self.point < other.point

# TODO: impl it
class StatusStructure:
    # def __init__(self):
    #     self.sorted_list = []
    #
    # def insert(self, elem, key=None):
    #     bisect.insort(self.sorted_list, elem, key=key)
    #
    # def remove(self, elem):
    #     idx = self.__binary_search(elem)
    #
    #     if idx == -1:
    #         return False
    #
    #     self.sorted_list.pop(idx)
    #
    #     return True
    #
    # def next(self, elem):
    #     return self.__binary_search(elem) + 1
    #
    # def prev(self, elem):
    #     return self.__binary_search(elem) - 1
    #
    # def swap(self, lhs, rhs):
    #     lhs_idx = self.__binary_search(lhs)
    #
    #     if lhs_idx == -1:
    #         return
    #
    #     rhs_idx = self.__binary_search(rhs)
    #
    #     if rhs_idx == -1:
    #         return
    #
    #     self.sorted_list[lhs_idx], self.sorted_list[lhs_idx] = rhs, lhs
    #
    # def __binary_search(self, elem, key):
    #     low = 0
    #     high = len(elem) - 1
    #
    #     while high - low > 1:
    #         mid = (low + high) // 2
    #
    #         if self.sorted_list[mid] < elem:
    #             low = mid + 1
    #         elif self.sorted_list[mid] > elem:
    #             high = mid - 1
    #         else:
    #             return mid
    #
    #     return -1


class IntersectionDeterminator:
    def __init__(self, segments):
        self.segments = segments
        self.event_queue = []
        self.status = StatusStructure()

    def demo(self):
        self.__plot_segments()
        self.__init_event_queue()
        result = self.__find_intersections()

        # plt.show()

    def __plot_segments(self):
        for segment in self.segments:
            segment.plot()

    def __init_event_queue(self):
        for segment in self.segments:
            begin, end = segment.get_endpoints()
            self.event_queue.append(Event(begin, segment, EventType.BEGIN))
            self.event_queue.append(Event(end, segment, EventType.END))

        heapq.heapify(self.event_queue)

    def __find_intersections(self):
        # TODO: impl it
        # result = []
        #
        # while len(self.event_queue) != 0:
        #     cur_event = heapq.heappop(self.event_queue)
        #     cur_point = cur_event.point
        #
        #     if cur_event.event_type == EventType.BEGIN:
        #         segment =


def main():
    segments = [
        Segment(Point(Decimal(-2), Decimal(0)), Point(Decimal(2), Decimal(1))),
        Segment(Point(Decimal(0), Decimal(0)), Point(Decimal(0), Decimal(2)))
    ]

    for s in segments:
        print(s)

    intersection_determinator = IntersectionDeterminator(segments)
    intersection_determinator.demo()

    intersection = Utils.find_intersection(segments[0], segments[1])
    # if intersection is not None:
    #     plt.scatter(intersection.x, intersection.y, color="red")
    #     print(intersection)

    plt.show()


if __name__ == "__main__":
    main()
