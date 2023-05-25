import matplotlib
matplotlib.use('TkAgg')

import matplotlib.pyplot as plt
import copy
import numpy
from enum import Enum


class PointClassification(Enum):
    CONVEX = 1
    CONCAVE = 2
    SUPPORTING = 3
    ERROR = -1


class DynamicConvexHull:
    def __init__(self):
        self.upper_convex_hull = UpperConvexHull()
        self.lower_convex_hull = LowerConvexHull()

    def insert(self, point):
        self.upper_convex_hull.insert(point)
        self.lower_convex_hull.insert(point)

    def delete(self, point):
        self.upper_convex_hull.delete(point)
        self.lower_convex_hull.delete(point)

    def plot(self, figure, axis):
        self.upper_convex_hull.plot(figure, axis)
        self.lower_convex_hull.plot(figure, axis)


class UpperConvexHull:
    def __init__(self):
        self.tree = ConvexHullTree()

    def insert(self, point):
        self.tree.insert(point)

    def delete(self, point):
        self.tree.delete(point)

    def plot(self, figure, axes):
        return self.tree.plot(figure, axes)


class LowerConvexHull:
    def __init__(self):
        self.tree = ConvexHullTree()

    def insert(self, point):
        to_insert = copy.deepcopy(point)
        to_insert.y *= -1

        self.tree.insert(to_insert)

    def delete(self, point):
        to_delete = copy.deepcopy(point)
        to_delete.y *= -1

        self.tree.delete(to_delete)

    def plot(self, figure, axes):
        return self.tree.plot(figure, axes, lower=True)


class Point:
    i = 0

    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.id = Node.i
        Node.i += 1

    def __repr__(self):
        return str(f"({self.x}; {self.y})")

    def __lt__(self, other):
        return (self.x, self.y) < (other.x, other.y)


class NodeData:
    def __init__(self, key=None):
        self.left_most_right = None
        self.left_most_right_point = key
        self.points_array = []
        self.separating_index = 0
        self.convex_hull = []
        self.graph_hull = []
        self.convex_hull.append(key)

    def __lt__(self, other):
        return self.left_most_right_point < other.left_most_right_point

    def __repr__(self):
        return str(f"{self.left_most_right_point}; {self.points_array}; {self.separating_index}")


class NodeColor(Enum):
    RED = 1
    BLACK = 2


class Node:
    i = 0

    def __init__(self, data):
        self.data = data
        self.parent = None
        self.left = None
        self.right = None
        self.color = NodeColor.RED
        self.id = Node.i
        Node.i += 1

    def __lt__(self, other):
        return self.data < other.data

    def __repr__(self):
        return str(f"{self.id}: {self.data}")

    def plot(self, figure, axis, TNULL, lower=False):
        if self is None or self == TNULL:
            return figure, axis

        if self.left == TNULL:
            point_x, point_y = self.data.left_most_right_point.x, self.data.left_most_right_point.y
            point_id = self.data.left_most_right_point.id

            if lower:
                point_y *= -1

            axis.scatter([point_x], [point_y], color="red")
            axis.annotate(f"{point_id}",
                          (point_x, point_y),
                          xytext=(point_x - 0.025, point_y + 0.1))
            return figure, axis

        chain = self.data.graph_hull
        if self.parent == TNULL:
            chain = self.data.points_array

        for i in range(1, len(chain)):
            if lower:
                axis.plot([chain[i - 1].x, chain[i].x], [-1 * chain[i - 1].y, -1 * chain[i].y], color="blue")
            else:
                axis.plot([chain[i - 1].x, chain[i].x], [chain[i - 1].y, chain[i].y], color="blue")

        if self.left != TNULL:
            self.left.data.graph_hull = chain[:self.data.separating_index + 1] + self.left.data.points_array

        if self.right != TNULL:
            self.right.data.graph_hull = self.right.data.points_array + chain[self.data.separating_index + 1:]

        self.left.plot(figure, axis, TNULL, lower)
        return self.right.plot(figure, axis, TNULL, lower)


class ConvexHullTree:
    def __init__(self):
        self.TNULL = Node(NodeData())
        self.TNULL.color = NodeColor.BLACK
        self.TNULL.left = None
        self.TNULL.right = None
        self.root = self.TNULL

    def insert(self, key):
        node = Node(NodeData(key))
        node.parent = None
        node.data.left_most_right = node
        node.left = self.TNULL
        node.right = self.TNULL
        node.color = NodeColor.RED

        x = self.root

        if x == self.TNULL:
            self.root = node
            return

        left_neighbour, right_neighbour = self.down(x, key)

        new_node_parent = Node(NodeData())
        node.parent = new_node_parent

        if left_neighbour is None:
            new_node_parent.left = node
            new_node_parent.right = right_neighbour

            new_node_parent.parent = right_neighbour.parent
            if right_neighbour.parent is None:
                self.root = new_node_parent
                new_node_parent.parent = self.TNULL
            else:
                right_neighbour.parent.left = new_node_parent

            right_neighbour.parent = new_node_parent

        elif right_neighbour is None:
            new_node_parent.right = node
            new_node_parent.left = left_neighbour

            new_node_parent.parent = left_neighbour.parent
            if left_neighbour.parent is None:
                self.root = new_node_parent
                new_node_parent.parent = self.TNULL
            else:
                left_neighbour.parent.right = new_node_parent

            left_neighbour.parent = new_node_parent

        elif self.find_brother(left_neighbour)[0] == right_neighbour:
            new_node_parent.left = left_neighbour
            new_node_parent.right = node

            new_node_parent.parent = left_neighbour.parent
            left_neighbour.parent.left = new_node_parent

            left_neighbour.parent = new_node_parent
        else:
            new_node_parent.left = node
            new_node_parent.right = right_neighbour

            new_node_parent.parent = right_neighbour.parent

            neighbour_side = self.node_side(right_neighbour)
            if neighbour_side == -1:
                right_neighbour.parent.left = new_node_parent
            else:
                right_neighbour.parent.right = new_node_parent

            right_neighbour.parent = new_node_parent

        self.up(node)

    def node_side(self, node):
        if node.parent.left == node:
            return -1
        elif node.parent.right == node:
            return 1
        else:
            return 0

    def down(self, current_node: Node, point: Point, left_neighbour: Node=None, right_neighbour: Node=None):
        if current_node.left == self.TNULL:
            if point.x <= current_node.data.left_most_right_point.x:
                right_neighbour = current_node
            else:
                left_neighbour = current_node
            return left_neighbour, right_neighbour

        left_queue = current_node.data.convex_hull[:current_node.data.separating_index + 1]
        right_queue = current_node.data.convex_hull[current_node.data.separating_index + 1:]

        left_son = current_node.left
        right_son = current_node.right

        if left_son.left != self.TNULL:
            left_son.data.convex_hull = left_queue + left_son.data.points_array

        if right_son.left != self.TNULL:
            right_son.data.convex_hull = right_son.data.points_array + right_queue

        if point.x <= current_node.data.left_most_right_point.x:
            right_neighbour = current_node
            current_node = current_node.left
        else:
            left_neighbour = current_node.data.left_most_right
            current_node = current_node.right

        return self.down(current_node, point, left_neighbour, right_neighbour)

    def up(self, current_node: Node):
        if current_node == self.get_root():
            current_node.data.points_array = current_node.data.convex_hull
            return

        current_brother, side = self.find_brother(current_node)

        q_1, q_2, q_3, q_4, j = [], [], [], [], 0
        if side == -1:
            q_1, q_2, q_3, q_4, j = merge_chains(current_brother.data.convex_hull, current_node.data.convex_hull)
        elif side == 1:
            q_1, q_2, q_3, q_4, j = merge_chains(current_node.data.convex_hull, current_brother.data.convex_hull)

        current_node.parent.left.data.points_array = q_2
        current_node.parent.right.data.points_array = q_3

        current_node.parent.data.convex_hull = q_1 + q_4
        current_node.parent.data.separating_index = j

        current_node.parent.data.left_most_right = self.find_left_most_right(current_node.parent)
        current_node.parent.data.left_most_right_point = current_node.parent.data.left_most_right.data.left_most_right_point

        self.up(current_node.parent)

    def find_brother(self, node: Node):
        if node.parent.left == node:
            return node.parent.right, 1
        elif node.parent.right == node:
            return node.parent.left, -1
        return self.TNULL

    def find_left_most_right(self, node: Node):
        current_node = node

        if current_node.left != self.TNULL:
            current_node = current_node.left

        while current_node.right != self.TNULL:
            current_node = current_node.right

        return current_node.data.left_most_right

    def get_root(self):
        return self.root

    def delete(self, data):
        node = Node(NodeData(data))
        node.parent = None
        node.data.left_most_right = node
        node.left = self.TNULL
        node.right = self.TNULL
        node.color = NodeColor.RED

        x = self.root

        _, to_delete_node = self.down(x, data)

        if to_delete_node == self.get_root():
            self.root = self.TNULL
        elif to_delete_node.parent.parent == self.TNULL:
            brother, _ = self.find_brother(to_delete_node)

            brother.data.points_array = brother.data.convex_hull

            self.root = brother
            brother.parent = self.TNULL
        else:
            node_parent = to_delete_node.parent
            brother, _ = self.find_brother(to_delete_node)

            side = self.node_side(node_parent)

            if side == -1:
                node_parent.parent.left = brother
            elif side == 1:
                node_parent.parent.right = brother

            brother.parent = node_parent.parent
            self.up(brother)

    def plot(self, fig, ax, lower=False):
        return self.get_root().plot(fig, ax, self.TNULL, lower=lower)


def merge_chains(chain_1: [], chain_2: []):
    if len(chain_2) == 1:
        if len(chain_1) == 1:
            return chain_1, [], [], chain_2, 0

        if len(chain_1) == 2:
            if is_point_left(chain_1[0], chain_1[1], chain_2[0]):
                return chain_1[:1], chain_1[1:], [], chain_2, 0
            else:
                return chain_1, [], [], chain_2, 1

    if len(chain_1) == 1:
        if is_point_left(chain_2[0], chain_2[1], chain_1[0]):
            return chain_1, [], chain_2[:1], chain_2[1:], 0
        else:
            return chain_1, [], [], chain_2, 0

    index_1 = int((len(chain_1) - 1) / 2)
    index_2 = int((len(chain_2) - 1) / 2)

    temp_min_1 = 0
    temp_max_1 = len(chain_1) - 1

    temp_min_2 = 0
    temp_max_2 = len(chain_2) - 1

    extreme_left_1 = False
    extreme_right_1 = False

    extreme_left_2 = False
    extreme_right_2 = False

    while True:
        extreme_left_1 = False
        extreme_right_1 = False

        extreme_left_2 = False
        extreme_right_2 = False

        if index_1 == temp_min_1:
            extreme_left_1 = True
        if index_1 == temp_max_1:
            extreme_right_1 = True

        if index_2 == temp_min_2:
            extreme_left_2 = True
        if index_2 == temp_max_2:
            extreme_right_2 = True

        type_1 = PointClassification.ERROR
        type_2 = PointClassification.ERROR

        if extreme_left_1 and extreme_right_1:
            type_1 = PointClassification.SUPPORTING

        elif extreme_left_1:
            type_1 = define_point_type_left(Point(chain_1[index_1].x, chain_1[index_1].y - 1),
                                            chain_1[index_1],
                                            chain_1[index_1 + 1], chain_2[index_2])
        elif extreme_right_1:
            type_1 = define_point_type_left(chain_1[index_1 - 1], chain_1[index_1],
                                            Point(chain_1[index_1].x, chain_1[index_1].y - 1),
                                            chain_2[index_2])
        else:
            type_1 = define_point_type_left(chain_1[index_1 - 1], chain_1[index_1], chain_1[index_1 + 1],
                                            chain_2[index_2])

        if extreme_left_2 and extreme_right_2:
            type_2 = PointClassification.SUPPORTING

        elif extreme_left_2:
            type_2 = define_point_type_right(Point(chain_2[index_2].x, chain_2[index_2].y - 1),
                                             chain_2[index_2],
                                             chain_2[index_2 + 1], chain_1[index_1])
        elif extreme_right_2:
            type_2 = define_point_type_right(chain_2[index_2 - 1], chain_2[index_2],
                                             Point(chain_2[index_2].x, chain_2[index_2].y - 1),
                                             chain_1[index_1])
        else:
            type_2 = define_point_type_right(chain_2[index_2 - 1], chain_2[index_2], chain_2[index_2 + 1],
                                             chain_1[index_1])

        if type_1 == PointClassification.CONCAVE and type_2 == PointClassification.CONCAVE:
            check_result = concave_concave_case(chain_1[index_1], chain_1[index_1 + 1], chain_1[temp_max_1],
                                                chain_2[temp_min_2], chain_2[index_2 - 1], chain_2[index_2])
            if check_result == -1:
                temp_min_1 = index_1
                if temp_max_1 - index_1 != 1:
                    index_1 = int((index_1 + temp_max_1) / 2)
                else:
                    index_1 = temp_max_1
            elif check_result == 1:
                temp_max_2 = index_2
                index_2 = int((temp_min_2 + index_2) / 2)
            else:
                temp_min_1 = index_1
                if temp_max_1 - index_1 != 1:
                    index_1 = int((index_1 + temp_max_1) / 2)
                else:
                    index_1 = temp_max_1
                temp_max_2 = index_2
                index_2 = int((temp_min_2 + index_2) / 2)

        elif type_1 == PointClassification.CONCAVE and type_2 == PointClassification.SUPPORTING:
            temp_min_1 = index_1
            if temp_max_1 - index_1 != 1:
                index_1 = int((index_1 + temp_max_1) / 2)
            else:
                index_1 = temp_max_1

            temp_min_2 = index_2
            # index_2 = int((index_2 + temp_max_2) / 2)

        elif type_1 == PointClassification.CONCAVE and type_2 == PointClassification.CONVEX:
            temp_min_2 = index_2
            if temp_max_2 - index_2 != 1:
                index_2 = int((index_2 + temp_max_2) / 2)
            else:
                index_2 = temp_max_2

        elif type_1 == PointClassification.SUPPORTING and type_2 == PointClassification.CONCAVE:
            temp_max_1 = index_1
            # index_1 = int((temp_min_1 + index_1) / 2)

            temp_max_2 = index_2
            index_2 = int((temp_min_2 + index_2) / 2)

        elif type_1 == PointClassification.SUPPORTING and type_2 == PointClassification.SUPPORTING:
            break

        elif type_1 == PointClassification.SUPPORTING and type_2 == PointClassification.CONVEX:
            temp_max_1 = index_1
            # index_1 = int((temp_min_1 + index_1) / 2)

            temp_min_2 = index_2
            if temp_max_2 - index_2 != 1:
                index_2 = int((index_2 + temp_max_2) / 2)
            else:
                index_2 = temp_max_2

        elif type_1 == PointClassification.CONVEX and type_2 == PointClassification.CONCAVE:
            temp_max_1 = index_1
            index_1 = int((temp_min_1 + index_1) / 2)

        elif type_1 == PointClassification.CONVEX and type_2 == PointClassification.SUPPORTING:
            temp_max_1 = index_1
            index_1 = int((temp_min_1 + index_1) / 2)

            temp_min_2 = index_2
            # index_2 = int((index_2 + temp_max_2) / 2)

        elif type_1 == PointClassification.CONVEX and type_2 == PointClassification.CONVEX:
            temp_max_1 = index_1
            index_1 = int((temp_min_1 + index_1) / 2)

            temp_min_2 = index_2
            if temp_max_2 - index_2 != 1:
                index_2 = int((index_2 + temp_max_2) / 2)
            else:
                index_2 = temp_max_2

    return chain_1[:index_1 + 1], \
           chain_1[index_1 + 1:], \
           chain_2[:index_2], \
           chain_2[index_2:], \
           index_1


def concave_concave_case(q1, q1_successor, max_left, min_right, q2_predecessor, q2):
    center_line_x = (max_left.x + min_right.x) / 2
    if get_intersection_point(q1, q1_successor, q2_predecessor, q2).x < center_line_x:
        return -1
    elif get_intersection_point(q1, q1_successor, q2_predecessor, q2).x > center_line_x:
        return 1
    else:
        return 0


def get_intersection_point(a, b, c, d):
    return Point(((a.x * b.y - a.y * b.x) * (c.x - d.x) - (a.x - b.x) * (c.x * d.y - c.y * d.x))
                 / ((a.x - b.x) * (c.y - d.y) - (a.y - b.y) * (c.x - d.x)),
                 ((a.x * b.y - a.y * b.x) * (c.y - d.y) - (a.y - b.y) * (c.x * d.y - c.y * d.x))
                 / ((a.x - b.x) * (c.y - d.y) - (a.y - b.y) * (c.x - d.x)))


def define_point_type_left(q1_pred: Point, q1: Point, q1_suc: Point, q2: Point):
    if is_point_left(q2, q1, q1_pred) and is_point_left(q2, q1, q1_suc):
        return PointClassification.SUPPORTING
    if is_point_left(q2, q1, q1_pred) and not is_point_left(q2, q1, q1_suc):
        return PointClassification.CONCAVE
    else:
        return PointClassification.CONVEX


def define_point_type_right(q2_pred: Point, q2: Point, q2_suc: Point, q1: Point):
    if not is_point_left(q1, q2, q2_pred) and not is_point_left(q1, q2, q2_suc):
        return PointClassification.SUPPORTING
    if is_point_left(q1, q2, q2_pred) and not is_point_left(q1, q2, q2_suc):
        return PointClassification.CONCAVE
    else:
        return PointClassification.CONVEX


def is_point_left(chain_point_1, chain_point_2, point):
    return ((chain_point_2.x - chain_point_1.x) * (point.y - chain_point_1.y) - (chain_point_2.y - chain_point_1.y) * (
        point.x - chain_point_1.x)) >= 0


def main():
    points_set = [
        Point(0, 0),
        Point(2, 4),
        Point(5, 0),
        Point(2, 1.5),
        Point(4, 3),
        Point(3, 2),
        Point(-1, 2)
    ]

    dynamic_convex_hull = DynamicConvexHull()

    for point in points_set:
        dynamic_convex_hull.insert(point)

    dynamic_convex_hull.delete(Point(2, 1.5))
    dynamic_convex_hull.delete(Point(2, -1))
    # dynamic_convex_hull.delete(Point(3, 2))
    # dynamic_convex_hull.delete(Point(2, 4))

    figure, axis = plt.subplots(nrows=1, ncols=1, figsize=(5, 5))
    dynamic_convex_hull.plot(figure, axis)

    plt.show()


if __name__ == "__main__":
    main()
