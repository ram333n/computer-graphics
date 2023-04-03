import matplotlib.pyplot as plt


class Point:
    def __init__(self, x, y):
        self.x = x
        self.y = y

    def get_coord_by_axis(self, axis):
        return self.x if axis == 0 else self.y


class Rectangle:
    def __init__(self, vertex, height, width):
        self.vertex = vertex
        self.height = height
        self.width = width

    def contains_point(self, point):
        return 0 <= point.x - self.vertex.x <= self.width \
               and 0 <= self.vertex.y - point.y <= self.height

    def get_range_by_axis(self, axis):
        if axis == 0:
            return self.vertex.x, self.vertex.x + self.width

        return self.vertex.y - self.height, self.vertex.y

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
    def __init__(self, point, line, axis, left=None, right=None):
        self.point = point
        self.line = line
        self.axis = axis
        self.left = left
        self.right = right

    def is_leaf(self):
        return self.left is None and self.right is None


# 2-d tree
class Tree:
    def __init__(self, points):
        self.root = self.__build_tree(points, 0)

    def __build_tree(self, points, depth):
        if len(points) == 0:
            return None

        axis = depth % 2

        points.sort(key=lambda p: p.get_coord_by_axis(axis))
        mid_idx = len(points) // 2
        median = points[mid_idx].get_coord_by_axis(axis)

        return Node(
            points[mid_idx],
            median,
            axis,
            self.__build_tree(points[:mid_idx], depth + 1),
            self.__build_tree(points[mid_idx + 1:], depth + 1)
        )

    def search(self, range_to_search):
        result = []
        self.__search(self.root, range_to_search, result)

        return result

    def __search(self, node, range_to_search, output):
        if node is None:
            return

        left, right = range_to_search.get_range_by_axis(node.axis)

        if range_to_search.contains_point(node.point):
            output.append(node.point)

        if left < node.line:
            self.__search(node.left, range_to_search, output)

        if node.line < right:
            self.__search(node.right, range_to_search, output)


class RangeSearcher:
    def __init__(self, points, range_to_search):
        self.points = points
        self.range_to_search = range_to_search
        self.tree = Tree(points)
        self.result = []

    def demo(self):
        self.__plot_input_points()
        self.__plot_rectangles()
        self.result = self.tree.search(self.range_to_search)
        self.__plot_result_points()
        self.__print_result()
        plt.show()

    def __plot_input_points(self):
        for point in self.points:
            plt.scatter(point.x, point.y, color="blue")

    def __plot_rectangles(self):
        self.range_to_search.plot("r")

    def __plot_result_points(self):
        for point in self.result:
            plt.scatter(point.x, point.y, color="orange")

    def __print_result(self):
        print(f"Count: {len(self.result)}")
        print("Result:")
        for point in self.result:
            print(f"({point.x}, {point.y})")


def main():
    points = [
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
        Point(7, 1.5),
        Point(0.5, 3.5),
        Point(1.5, 3.5),
        Point(0.5, 3.0),
    ]

    range_to_search = Rectangle(Point(0.5, 3.5), 3, 10)
    range_searcher = RangeSearcher(points, range_to_search)
    range_searcher.demo()


if __name__ == "__main__":
    main()
