class Node:
    def __init__(self, value, left=None, right=None, parent=None):
        self.value = value
        self.left = left
        self.right = right
        self.parent = parent

    def is_leaf(self):
        return self.left is None and self.right is None


class BSTree:
    def __init__(self):
        self.root = None

    def insert(self, value, key):
        to_insert = Node(value)
        current = self.root
        pos_to_insert = None

        while current is not None:
            pos_to_insert = current

            if key(value) < key(current.value):
                current = current.left
            else:
                current = current.right

        to_insert.parent = pos_to_insert

        if pos_to_insert is None:
            self.root = to_insert
        elif key(value) < key(pos_to_insert.value):
            pos_to_insert.left = to_insert
        else:
            pos_to_insert.right = to_insert

        return to_insert

    def remove(self, node):
        if node is None:
            return

        if node.left is None:
            self.__transplant(node, node.right)
        elif node.right is None:
            self.__transplant(node, node.left)
        else:
            y = self.__leftmost(node.right)

            if y.parent != node:
                self.__transplant(y, y.right)
                y.right = node.right
                y.right.parent = y

            self.__transplant(node, y)
            y.left = node.left
            y.left.parent = y

    def __transplant(self, first, second):
        if first.parent is None:
            self.root = second
        elif first == first.parent.left:
            first.parent.left = second
        else:
            first.parent.right = second

        if second is not None:
            second.parent = first.parent

    def __leftmost(self, node):
        current = node

        while current.left is not None and not current.is_leaf():
            current = current.left

        return current

    def successor(self, node):
        if node.right is not None:
            return self.__minimum(node.right)

        current = node.parent

        while current is not None and node == current.right:
            node = current
            current = current.parent

        return current

    def __minimum(self, node):
        current = node

        while current.left is not None:
            current = current.left

        return current

    def predecessor(self, node):
        if node.left is not None:
            return self.__maximum(node.left)

        current = node.parent

        while current is not None and node == current.left:
            node = current
            current = current.parent

        return current

    def __maximum(self, node):
        current = node

        while current.right is not None:
            current = current.right

        return current
