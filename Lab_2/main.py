import copy
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
        return self.data is not None



# 2-d tree
# TODO: rewrite logic of tree
class Tree:
    def __init__(self, points, border):
        self.root = self.__build_tree(points, border, 0)

    def __build_tree(self, points, border, depth):
        if len(points) == 1:
            return Node(points[0], border)
        else:
            # data to create left subtree
            points_1 = {}
            region_1 = None

            # data to create right subtree
            points_2 = {}
            region_2 = None

            mid_idx = len(points) // 2 - 1 # TODO: investigate about  - 1

            if depth % 2 == 0:
                sorted_points = sorted(points, key=lambda p: p.x)
                median = sorted_points[mid_idx].x

                points_1 = sorted_points[:mid_idx + 1]
                region_1 = Rectangle(
                    border.vertex,
                    border.height,
                    median - border.vertex.x
                )

                points_2 = sorted_points[mid_idx + 1:]
                region_2 = Rectangle(
                    Point(median, border.vertex.y),
                    border.height,
                    border.width - (median - border.vertex.x)
                )
            else:
                sorted_points = sorted(points, key=lambda p: p.y)
                median = sorted_points[mid_idx].y

                points_1 = sorted_points[:mid_idx + 1]
                region_1 = Rectangle(
                    Point(border.vertex.x, median),
                    border.height - (border.vertex.y - median),
                    border.width
                )

                points_2 = sorted_points[mid_idx + 1:]
                region_2 = Rectangle(
                    border.vertex,
                    border.height - median,
                    border.width
                )

            left_node = self.__build_tree(points_1, region_1, depth + 1)
            right_node = self.__build_tree(points_2, region_2, depth + 1)

            result = Node(None, border)
            result.left = left_node
            result.right = right_node

            return result

    def search(self, range_to_search):
        result = []
        self.__search(self.root, range_to_search, result)

        return result

    def __search(self, node, range_to_search, output):
        if node.is_leaf():
            if range_to_search.contains_point(node.data):
                output.append(node.data)
        else:
            if range_to_search.contains_rectangle(node.left.region):
                self.__report_subtree(node.left, output)
            else:
                if node.left.region.intersects(range_to_search):
                    self.__search(node.left, range_to_search, output)

            if range_to_search.contains_rectangle(node.right.region):
                self.__report_subtree(node.right, output)
            else:
                if node.right.region.intersects(range_to_search):
                    self.__search(node.right, range_to_search, output)

    def __report_subtree(self, node, output):
        if node.is_leaf():
            output.append(node.data)
        else:
            self.__report_subtree(node.left, output)
            self.__report_subtree(node.right, output)


class RangeSearcher:
    def __init__(self, points, range_to_search):
        self.points = points
        self.range_to_search = range_to_search
        self.border = self.__define_border()
        self.tree = Tree(points, self.border)
        self.result = []

    def __define_border(self):
        iterator = iter(self.points)
        left_border = next(iterator)
        right_border = copy.deepcopy(left_border)
        top_border = copy.deepcopy(left_border)
        bottom_border = copy.deepcopy(left_border)

        for point in iterator:
            if left_border.x > point.x:
                left_border = point

            if right_border.x < point.x:
                right_border = point

            if top_border.y < point.y:
                top_border = point

            if bottom_border.y > point.y:
                bottom_border = point

        # just to handle degeneracy, when points are on the same line
        padding_value = 1
        vertex_x = left_border.x - padding_value
        vertex_y = top_border.y + padding_value
        vertex = Point(vertex_x, vertex_y)

        height = vertex_y - bottom_border.y + padding_value
        width = right_border.x - left_border.x + 2 * padding_value

        return Rectangle(vertex, height, width)

    def demo(self):
        self.__plot_input_points()
        self.__plot_rectangles()
        self.result = self.tree.search(self.range_to_search)
        self.__plot_result_points()
        plt.show()

    def __plot_input_points(self):
        for point in self.points:
            plt.plot(point.x, point.y, "ob")

    def __plot_rectangles(self):
        self.range_to_search.plot("r")
        self.border.plot("b")

    def __plot_result_points(self):
        for point in self.points:
            plt.plot(point.x, point.y, "oy")


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
        Point(7, 1.5)
    ]

    range_to_search = Rectangle(Point(0.5, 3.5), 3, 10)
    range_searcher = RangeSearcher(points, range_to_search)
    range_searcher.demo()


if __name__ == "__main__":
    main()
