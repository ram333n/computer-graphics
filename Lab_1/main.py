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

        start.add_edge(self)
        end.add_edge(self)

    def __str__(self):
        return f"{self.start} -> {self.end}, ctg={self.ctg}, w={self.w}"

    def get_point_direction(self, point):
        x_1 = self.start.x
        x_2 = self.end.x
        x_3 = point.x

        y_1 = self.start.y
        y_2 = self.end.y
        y_3 = point.y

        det = x_1 * y_2 + x_3 * y_1 + x_2 * y_3 - x_3 * y_2 - x_2 * y_1 - x_1 * y_3

        if det == 0:
            return 0  # lies on the edge

        return -1 if det > 0 else 1  # -1 - left side, 1 - right side


class Chain:
    def __init__(self, edges, number):
        self.edges = edges
        self.number = number

    def get_point_direction(self, point):
        edge = self.__localize_point_by_y(point)

        if edge is None:
            return None

        return edge.get_point_direction(point)

    def __localize_point_by_y(self, point):
        if point.y > self.edges[-1].end.y or point.y < self.edges[0].start.y:
            return None

        low = 0
        high = len(self.edges) - 1
        result = 0
        is_found = False

        while not is_found:
            mid = (high + low) // 2
            edge = self.edges[mid]

            if edge.start.y <= point.y <= edge.end.y:
                is_found = True
                result = mid
            elif point.y > edge.end.y:
                low = mid + 1
            else:
                high = mid - 1

        return self.edges[result]

    def print(self):
        for edge in self.edges:
            print(edge)


def __between_chains(point, lhs_chain, rhs_chain):
    return lhs_chain.get_point_direction(point) == 1 \
            and rhs_chain.get_point_direction(point) == -1


class Graph:
    def __init__(self, points_file, edges_file):
        self.points = []
        self.edges = []
        self.chains = []

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

    def demo(self, point_to_locate):
        if not self.__is_regular():
            print("Graph isn't regular. Regularization started.")
            self.__regularize()

        self.__balance()
        self.__print_graph()
        self.__plot_edges()
        self.__plot_points(point_to_locate)
        self.__build_chains()
        self.__print_chains()

        borders = self.__localize_point(point_to_locate)
        self.__inform_about_localization(borders)
        self.__plot_result_chains(borders)

        plt.show()

    def __is_regular(self):
        for i in range(1, len(self.points) - 1):
            if len(self.points[i].in_edges) == 0 \
                    or len(self.points[i].out_edges) == 0:
                return False

        return True

    def __regularize(self):
        self.__forward_regularize()
        self.__backward_regularize()

    def __forward_regularize(self):
        status_edges = self.points[0].out_edges[:]
        status_points = [self.points[0]] * (len(status_edges) + 1)

        for i in range(1, len(self.points)):
            cur_point = self.points[i]

            if len(cur_point.in_edges) == 0:
                if len(status_edges) != 0:
                    idx = self.__localize_point_in_status(status_edges, cur_point)

                    edge_to_append = Edge(cur_point, status_points[idx])
                    print(f"Added:\n{edge_to_append}")
                    self.edges.append(edge_to_append)

                    status_edges = \
                        status_edges[:idx] \
                        + cur_point.out_edges \
                        + status_edges[idx:]

                    status_points = \
                        status_points[:idx] \
                        + [cur_point] * (len(cur_point.out_edges) + 1) \
                        + status_points[:idx + 1]
                else:
                    edge_to_append = Edge(cur_point, status_points[0])
                    print(f"Added:\n{edge_to_append}")
                    self.edges.append(edge_to_append)

                    status_edges = cur_point.out_edges[:]
                    status_points = [cur_point] * (len(status_edges) + 1)
            else:
                idx = status_edges.index(cur_point.in_edges[0])
                status_edges = \
                    status_edges[:idx] \
                    + cur_point.out_edges \
                    + status_edges[:idx + len(cur_point.in_edges)]

                status_points = \
                    status_points[:idx] \
                    + [cur_point] * (len(cur_point.out_edges) + 1) \
                    + status_points[:idx + len(cur_point.in_edges) + 1]

                if len(status_points) == 0:
                    status_points.append(cur_point)

    def __backward_regularize(self):
        status_edges = self.points[-1].in_edges[:]
        status_points = [self.points[-1]] * (len(status_edges) + 1)

        for i in range(len(self.points) - 2, -1, -1):
            cur_point = self.points[i]

            if len(cur_point.out_edges) == 0:
                if len(status_edges) != 0:
                    idx = self.__localize_point_in_status(status_edges, cur_point)

                    edge_to_append = Edge(cur_point, status_points[idx])
                    print(f"Added:\n{edge_to_append}")
                    self.edges.append(edge_to_append)

                    status_edges = \
                        status_edges[:idx] \
                        + cur_point.in_edges \
                        + status_edges[idx:]

                    status_points = \
                        status_points[:idx] \
                        + [cur_point] * (len(cur_point.in_edges) + 1) \
                        + status_points[idx + 1:]
                else:
                    edge_to_append = Edge(cur_point, status_points[0])
                    print(f"Added:\n{edge_to_append}")
                    self.edges.append(edge_to_append)

                    status_edges = cur_point.in_edges[:]
                    status_points = [cur_point] * (len(status_edges) + 1)
            else:
                idx = status_edges.index(cur_point.out_edges[0])

                status_edges = \
                    status_edges[:idx] \
                    + cur_point.in_edges \
                    + status_edges[idx + len(cur_point.out_edges):]

                status_points = \
                    status_points[:idx] \
                    + [cur_point] * (len(cur_point.in_edges) + 1) \
                    + status_points[idx + len(cur_point.out_edges) + 1:]

                if len(status_points) == 0:
                    status_points.append(cur_point)

    def __localize_point_in_status(self, status_edges, point):
        low = 0
        high = len(status_edges) - 1

        while high - low > 1:
            mid = (low + high) // 2

            if status_edges[mid].get_point_direction(point) == -1:
                high = mid
            else:
                low = mid

        if status_edges[high].get_point_direction(point) == 1:
            return high + 1

        if status_edges[low].get_point_direction(point) == -1:
            return low

        return high

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

    def __build_chains(self):
        chains_counter = 0

        while True:
            cur_point = self.points[0]

            start_edge = next(
                (edge for edge in cur_point.out_edges if edge.w > 0),
                None
            )

            if start_edge is None:
                break

            start_edge.w -= 1
            chain = Chain([start_edge], chains_counter)
            cur_point = start_edge.end

            while cur_point != self.points[-1]:
                edge_to_add = next(
                    edge for edge in cur_point.out_edges if edge.w > 0)
                edge_to_add.w -= 1
                chain.edges.append(edge_to_add)
                cur_point = edge_to_add.end

            self.chains.append(chain)
            chains_counter += 1

    def __print_graph(self):
        for point in self.points:
            print(f"Point: {point}")

            for in_edge in point.in_edges:
                print(f"'In' edge: {in_edge}")

            for out_edge in point.out_edges:
                print(f"'Out' edge: {out_edge}")

    def __print_chains(self):
        print("Chains: ")

        for i in range(len(self.chains)):
            print(f"Chain: {i}")
            self.chains[i].print()

    def __localize_point(self, point):
        if self.chains[0].get_point_direction(point) is None or \
           self.chains[0].get_point_direction(point) == -1 or \
           self.chains[-1].get_point_direction(point) == 1:
            return []

        low = 0
        high = len(self.chains) - 1

        while high - low > 1:
            mid = (low + high) // 2
            current_chain_direction = self.chains[mid].get_point_direction(point)

            if current_chain_direction == 0:
                return [self.chains[mid]]
            elif current_chain_direction == 1:
                low = mid
            else:
                high = mid

        if self.chains[low].get_point_direction(point) == 0:
            return [self.chains[low]]
        elif self.chains[high].get_point_direction(point) == 0:
            return [self.chains[high]]

        return [self.chains[low], self.chains[high]]

    def __inform_about_localization(self, chains):
        if len(chains) == 0:
            print("The point is outside graph")
            return

        if len(chains) == 1:
            print(f"The point is on the chain: {chains[0].number}")
        else:
            print(f"The point is between chains: {chains[0].number} and {chains[1].number}")

    def __plot_result_chains(self, chains):
        for chain in chains:
            for edge in chain.edges:
                plt.plot(
                    [edge.start.x, edge.end.x],
                    [edge.start.y, edge.end.y],
                    "-y"
                )


def main():
    arr = [0, 1, 2, 3, 4, 5, 6]
    print(arr[:1] + [-1, -2] + arr[2:])
    graph = Graph("points_1.txt", "edges_1.txt")
    graph.demo(Point(1.5, -5))


if __name__ == "__main__":
    main()
