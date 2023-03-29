import matplotlib.pyplot as plt


class Point:
    def __init__(self, x, y):
        self.x = x
        self.y = y


class Rectangle:
    def __init__(self, vertex, height, width):
        self.vertex = vertex
        self.height = height
        self.width = width

    def contains(self, point):
        return 0 <= point.x - self.vertex.x <= self.width \
           and 0 <= self.vertex.y - point.y <= self.height

# 2D tree
# class Tree:
#     # TODO: impl it


class RangeSearcher:
    def __init__(self, points, rectangle):
        self.points = points
        self.rectangle = rectangle

    def plot(self):
        self.__plot_points()
        self.__plot_region()
        plt.show()

    def __plot_points(self):
        for point in self.points:
            plt.plot(point.x, point.y, "ob")

    def __plot_region(self):
        # draw rectangle clockwise
        x_coords = [
            self.rectangle.vertex.x,
            self.rectangle.vertex.x + self.rectangle.width,
            self.rectangle.vertex.x + self.rectangle.width,
            self.rectangle.vertex.x,
            self.rectangle.vertex.x
        ]

        y_coords = [
            self.rectangle.vertex.y,
            self.rectangle.vertex.y,
            self.rectangle.vertex.y - self.rectangle.height,
            self.rectangle.vertex.y - self.rectangle.height,
            self.rectangle.vertex.y
        ]

        plt.plot(x_coords, y_coords, "-r")


def main():
    points = [
        Point(1, 2),
        Point(-5, 3),
        Point(0, 0),
        Point(3, 1),
        Point(2, 2),
    ]

    rectangle = Rectangle(Point(0.5, 3.5), 3, 10)
    range_searcher = RangeSearcher(points, rectangle)
    range_searcher.plot()


if __name__ == "__main__":
    main()
