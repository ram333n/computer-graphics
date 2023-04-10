from decimal import Decimal
import matplotlib.pyplot as plt


ZERO = Decimal()
INF = Decimal("inf")


class Point:
    def __init__(self, x, y):
        self.x = x
        self.y = y

    def __str__(self):
        return f"({self.x}; {self.y})"


class Segment:
    def __init__(self, start, end):
        self.start = start
        self.end = end

    def plot(self):
        plt.plot(
            [self.start.x, self.end.x],
            [self.start.y, self.end.y],
            "-b"
        )

    def to_line(self):
        dx = self.end.x - self.start.x

        # in this case method returns line in view x=b, where b=start.x
        if dx == ZERO:
            return INF, self.start.x

        dy = self.end.y - self.start.y
        k = dy / dx

        b = self.start.y - k * self.start.x

        return k, b

    def projections_contain(self, point):
        x_begin, x_end = self.__projection("x")
        y_begin, y_end = self.__projection("y")

        return x_begin <= point.x <= x_end and y_begin <= point.y <= y_end

    def __projection(self, axis):
        if axis == "x":
            return min(self.start.x, self.end.x), max(self.start.x, self.end.x)

        return min(self.start.y, self.end.y), max(self.start.y, self.end.y)


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


class IntersectionDeterminator:
    def __init__(self, segments):
        self.segments = segments

    def demo(self):
        self.__plot_segments()

        # plt.show()

    def __plot_segments(self):
        for segment in self.segments:
            segment.plot()


def main():
    segments = [
        Segment(Point(Decimal(-2), Decimal(0)), Point(Decimal(2), Decimal(1))),
        Segment(Point(Decimal(0), Decimal(0)), Point(Decimal(0), Decimal(2)))
    ]

    intersection_determinator = IntersectionDeterminator(segments)
    intersection_determinator.demo()

    intersection = Utils.find_intersection(segments[0], segments[1])
    if intersection is not None:
        plt.scatter(intersection.x, intersection.y, color="red")
        print(intersection)

    plt.show()


if __name__ == "__main__":
    main()
