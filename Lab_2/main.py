import copy
import statistics

import matplotlib.pyplot as plt


class Point:
    def __init__(self, x, y):
        self.x = x
        self.y = y

    def __eq__(self, other):
        return self.x == other.x and self.y == other.y

    def __hash__(self):
        return hash((self.x, self.y))


class Rectangle:
    def __init__(self, vertex, height, width):
        self.vertex = vertex
        self.height = height
        self.width = width

    def contains_point(self, point):
        return 0 <= point.x - self.vertex.x <= self.width \
               and 0 <= self.vertex.y - point.y <= self.height

    def intersects(self, other):
        return not (
            self.vertex.x + self.width < other.vertex.x
            or self.vertex.x > other.vertex.x + other.width
            or self.vertex.y < other.vertex.y - other.height
            or self.vertex.y - self.height > other.vertex.y
        )

    def contains_rectangle(self, other):
        return self.intersects(other) \
               and self.vertex.x <= other.vertex.x \
               and self.vertex.y >= other.vertex.y \
               and self.width >= other.width \
               and self.height >= other.height

    def plot(self, color):
        # draw rectangle clockwise
        x_coords = [
            self.vertex.x,
            self.vertex.x + self.width,
            self.vertex.x + self.width,
            self.vertex.x,
            self.vertex.x
        ]

        y_coords = [
            self.vertex.y,
            self.vertex.y,
            self.vertex.y - self.height,
            self.vertex.y - self.height,
            self.vertex.y
        ]

        plt.plot(x_coords, y_coords, "-" + color)


class Node:
    def __init__(self, data, region):
        self.data = data
        self.region = region
        self.left = None
        self.right = None

    def is_leaf(self):
        return self.data is None


# 2-d tree
class Tree:
    def __init__(self, points, border):
        self.root = self.__build_tree(points, border, 0)

    def __build_tree(self, points, border, depth):
        if len(points) == 1:
            return Node(points[0], None)
        elif depth % 2 == 0:
            x_coords = self.__retrieve_coords(points, depth)
            median = statistics.median(x_coords)
            left_region = Rectangle(
                border.vertex,
                border.height,
                median - border.vertex.x
            )
            #TODO: check it carefully
            right_region = Rectangle(
                Point(median, border.vertex.y),
                border.height,
                border.vertex.x
            )

    def __retrieve_coords(self, points, axis):
        return set(map(
            lambda p: p.x if axis == 0 else lambda p: p.y,
            points)
        )


class RangeSearcher:
    def __init__(self, points, region_to_search):
        self.points = points
        self.region_to_search = region_to_search
        self.border = self.__define_border()

    def __define_border(self):
        iterator = iter(self.points)
        left_border = next(iterator)
        right_border = copy.deepcopy(left_border)
        top_border = copy.deepcopy(left_border)
        bottom_border = copy.deepcopy(left_border)

        for point in iterator:
            left_border = point if left_border.x > point.x else left_border
            right_border = point if right_border.x < point.x else right_border
            top_border = point if top_border.y < point.y else top_border
            bottom_border = point if bottom_border.y > point.y else bottom_border

        # just to handle degeneracy, when borders are on the same line
        padding_value = 1
        vertex_x = left_border.x - padding_value
        vertex_y = top_border.y + padding_value
        vertex = Point(vertex_x, vertex_y)

        height = vertex_y - bottom_border.y + padding_value
        width = right_border.x - left_border.x + 2 * padding_value

        return Rectangle(vertex, height, width)

    def plot(self):
        self.__plot_points()
        self.__plot_rectangles()
        plt.show()

    def __plot_points(self):
        for point in self.points:
            plt.plot(point.x, point.y, "ob")

    def __plot_rectangles(self):
        self.region_to_search.plot("r")
        self.border.plot("b")


def main():
    points = {
        Point(1, 2),
        Point(1, 3),
        Point(0, 0),
        Point(3, 1),
        Point(15, 1.5),
        Point(10, 2.5),
        Point(5, 2.3),
        Point(7, 0),
        Point(12.5, -0.5),
        Point(-4, 4),
        Point(6, 1),
        Point(7, 1.5)
    }

    region_to_search = Rectangle(Point(0.5, 3.5), 3, 10)
    range_searcher = RangeSearcher(points, region_to_search)
    range_searcher.plot()


if __name__ == "__main__":
    main()
