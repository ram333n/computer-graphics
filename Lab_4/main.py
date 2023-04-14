

class Point:
    def __init__(self, x, y):
        self.x = x
        self.y = y

    def __str__(self):
        return f"({self.x}; {self.y})"


def main():
    print(Point(3, 2))


if __name__ == "__main__":
    main()
