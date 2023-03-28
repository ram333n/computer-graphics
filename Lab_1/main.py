import math
import bisect
import matplotlib.pyplot as plt


class Utils:
    POINT_TEXT_X_MARGIN = 0.05
    POINT_TEXT_Y_MARGIN = 0.05

    @staticmethod
    def ctg(edge):
        dx = edge.end.x - edge.start.x
        dy = edge.end.y - edge.start.y

        return dx / dy


class Point:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.in_edges = []
        self.out_edges = []

    def __str__(self):
        return f"({self.x}, {self.y})"

    def __eq__(self, other):
        return self.x == other.x and self.y == other.y

    def __lt__(self, other):
        return [self.y, self.x] < [other.y, other.x]

    def w_in(self):
        return sum(edge.w for edge in self.in_edges)

    def w_out(self):
        return sum(edge.w for edge in self.out_edges)

    def add_edge(self, edge):
        if self == edge.start:
            bisect.insort(self.out_edges, edge, key=lambda elem: elem.ctg)
        else:
            bisect.insort(self.in_edges, edge, key=lambda elem: -elem.ctg)


class Edge:
    def __init__(self, start, end):
        if start < end:
            self.start = start
            self.end = end
        else:
            self.start = end
            self.end = start

        self.ctg = Utils.ctg(self)
        self.w = 1

    def __str__(self):
        return f"{self.start} -> {self.end}, ctg={self.ctg}, w={self.w}"


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
        self.__balance()
        for point in self.points:
            print(f"Point: {point}")

            for in_edge in point.in_edges:
                print(f"'In' edge: {in_edge}")

            for out_edge in point.out_edges:
                print(f"'Out' edge: {out_edge}")

            print()

        chains = self.__build_chains()
        print("Chains: ")

        for i in range(len(chains)):
            print(f"Chain: {i}")

            for e in chains[i]:
                print(e)

    def plot(self, point_to_locate):
        self.__plot_edges()
        self.__plot_points(point_to_locate)
        plt.show()

    def __plot_points(self, point_to_locate):
        for i in range(len(self.points)):
            point = self.points[i]
            plt.plot(point.x, point.y, "ok")

            plt.text(
                point.x + Utils.POINT_TEXT_X_MARGIN,
                point.y + Utils.POINT_TEXT_Y_MARGIN,
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

            text_x = (edge.start.x + edge.end.x) / 2
            text_y = (edge.start.y + edge.end.y) / 2

            plt.text(
                text_x,
                text_y,
                f"w={edge.w}",
            )

    def __balance(self):
        self.__forward_balance()
        self.__backward_balance()

    def __forward_balance(self):
        for i in range(1, len(self.points) - 1):
            point = self.points[i]
            w_in = point.w_in()
            leftmost_edge = point.out_edges[0]

            if w_in > len(point.out_edges):
                leftmost_edge.w = w_in - len(point.out_edges) + 1

    def __backward_balance(self):
        for i in range(len(self.points) - 1, 0, -1):
            point = self.points[i]
            w_out = point.w_out()
            w_in = point.w_in()
            leftmost_edge = point.in_edges[0]

            if w_out > w_in:
                leftmost_edge.w += w_out - w_in

    def __build_chains(self):
        result = []

        while True:
            cur_point = self.points[0]

            start_edge = next(
                (edge for edge in cur_point.out_edges if edge.w > 0),
                None
            )

            if start_edge is None:
                break

            start_edge.w -= 1
            chain = [start_edge]
            cur_point = start_edge.end

            while cur_point != self.points[-1]:
                edge_to_add = next(edge for edge in cur_point.out_edges if edge.w > 0)
                edge_to_add.w -= 1
                chain.append(edge_to_add)
                cur_point = edge_to_add.end

            result.append(chain)

        return result


def main():
    print(Point(2, 1) == Point(2, 2))
    graph = Graph("points_1.txt", "edges_1.txt")
    graph.print()
    # graph.plot(Point(2.5, 4))


if __name__ == "__main__":
    main()
