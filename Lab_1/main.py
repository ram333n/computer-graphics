import math
import bisect
import matplotlib.pyplot as plt


class Constants:
    POINT_TEXT_X_MARGIN = 0.03
    POINT_TEXT_Y_MARGIN = 0.03


class Point:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.in_edges = []
        self.out_edges = []

    def __str__(self):
        return f"({self.x}, {self.y})"

    def __lt__(self, other):
        return [self.y, self.x] < [other.y, other.x]

    def w_in(self):
        return sum(edge.w for edge in self.in_edges)

    def w_out(self):
        return sum(edge.w for edge in self.out_edges)

    def add_edge(self, edge):
        end_point = edge.end
        array_to_insert = self.in_edges if end_point == self else self.out_edges
        bisect.insort(array_to_insert, edge, key=lambda elem: elem.angle)


class Edge:
    def __init__(self, start, end):
        if start < end:
            self.start = start
            self.end = end
        else:
            self.start = end
            self.end = start

        dy = self.end.y - self.start.y
        dx = self.end.x - self.start.x
        self.angle = math.pi / 2 - math.atan2(dy, dx)

        self.w = 0

    def __str__(self):
        return f"{self.start} -> {self.end}, angle={self.angle}, w={self.w}"


class Graph:
    def __init__(self, points_file, edges_file):
        self.points = []
        self.edges = []

        points_strs = open(points_file).read().split()
        edges_strs = open(edges_file).read().split()

        self.__init_points(points_strs)
        self.__init_edges(edges_strs)

        self.points.sort()

    def __init_points(self, points_strs):
        for i in range(0, len(points_strs) - 1, 2):
            x = float(points_strs[i])
            y = float(points_strs[i + 1])
            self.points.append(Point(x, y))

    def __init_edges(self, edges_strs):
        for i in range(0, len(edges_strs) - 1, 2):
            from_point = self.points[int(edges_strs[i])]
            to_point = self.points[int(edges_strs[i + 1])]

            edge_to_add = Edge(from_point, to_point)
            self.edges.append(edge_to_add)

            from_point.add_edge(edge_to_add)
            to_point.add_edge(edge_to_add)

    def print(self):
        for point in self.points:
            print(f"Point: {point}")

            for in_edge in point.in_edges:
                print(f"'In' edge: {in_edge}")

            for out_edge in point.out_edges:
                print(f"'Out' edge: {out_edge}")

            print()

    def plot(self, point_to_locate):
        self.__plot_edges()
        self.__plot_points(point_to_locate)
        plt.show()

    def __plot_points(self, point_to_locate):
        for i in range(len(self.points)):
            point = self.points[i]
            plt.plot(point.x, point.y, "ok")

            plt.text(
                point.x + Constants.POINT_TEXT_X_MARGIN,
                point.y + Constants.POINT_TEXT_Y_MARGIN,
                i
            )

        plt.plot(point_to_locate.x, point_to_locate.y, "or")

    def __plot_edges(self):
        for edge in self.edges:
            plt.plot(
                [edge.start.x, edge.end.x],
                [edge.start.y, edge.end.y],
                "-b"
            )


def main():
    graph = Graph("points.txt", "edges.txt")
    graph.print()
    graph.plot(Point(2, 2.7))


if __name__ == "__main__":
    main()
