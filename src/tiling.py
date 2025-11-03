import math
from PIL import Image as image
from PIL.Image import Image
from aggdraw import Draw, Pen
from typing import Iterator, TypeAlias, Iterable
from argparse import ArgumentParser


class HexagonGenerator(object):
    """Returns a hexagon generator for hexagons of the specified size."""

    def __init__(self, edge_length):
        self.edge_length = edge_length

    @property
    def col_width(self):
        return self.edge_length * 3

    @property
    def row_height(self):
        return math.sin(math.pi / 3) * self.edge_length

    def __call__(self, row, col):
        x = (col + 0.5 * (row % 2)) * self.col_width
        y = row * self.row_height
        for angle in range(0, 360, 60):
            x += math.cos(math.radians(angle)) * self.edge_length
            y += math.sin(math.radians(angle)) * self.edge_length
            yield x
            yield y


def hexagon_generator(edge_length, offset):
    """Generator for coordinates in a hexagon."""
    x, y = offset
    for angle in range(0, 360, 60):
        x += math.cos(math.radians(angle)) * edge_length
        y += math.sin(math.radians(angle)) * edge_length
        yield x
        yield y


Point: TypeAlias = tuple[float, float]


def splice(points: Iterable[Point]) -> Iterator[float]:
    for x, y in points:
        yield x
        yield y


class Hexagon:
    def __init__(self, radius: float, center: Point):
        self._radius = radius
        self._center = center

    def points(self) -> list[Point]:
        def it():
            x, y = self._center
            for angle in range(0, 360, 60):
                x += math.cos(math.radians(angle)) * self._radius
                y += math.sin(math.radians(angle)) * self._radius
                yield (x, y)

        return list(it())


def lines(points: list[Point]) -> list[tuple[Point, Point]]:
    def it():
        p = None
        for q in points:
            if p is not None:
                yield (p, q)
            p = q
        yield (points[-1], points[1])

    return list(it())


class Tiling:
    def __init__(self, radius: float):
        self._radius = radius

    def center(self, row: int, col: int) -> Point:
        x = (col + 0.5 * (row % 2)) * self._radius * 3
        y = row * math.sin(math.pi / 3) * self._radius
        return (x, y)

    def hexagon(self, row: int, col: int) -> Hexagon:
        return Hexagon(self._radius, self.center(row, col))

    def draw(self, img: Image) -> None:
        draw = Draw(img)
        row, col = (-1, 0)
        pen = Pen("black", 3)
        while True:
            hexagon = self.hexagon(row, col)
            points = hexagon.points()
            if row == -1:
                draw.polygon(list(splice(points)), pen)
            else:
                for line in lines(points)[:4]:
                    draw.line(list(splice(line)), pen)
            if any(p[0] > img.size[0] for p in points):
                row += 1
                col = 0
                if any(p[1] > img.size[1] for p in points):
                    break
            else:
                col += 1
        draw.flush()


def a4(resolution: int = 300) -> Image:
    return image.new("RGB", (int(8.3 * resolution), int(11.7 * resolution)), "white")


def create_parser() -> ArgumentParser:
    parser = ArgumentParser()
    parser.add_argument("--resolution", type=int, default=300)
    parser.add_argument("--radius", type=float, default=0.65)
    return parser


def main():
    args = create_parser().parse_args()
    tiling = Tiling(radius=args.radius * args.resolution)
    img = a4(args.resolution)
    tiling.draw(img)
    img.show()


if __name__ == "__main__":
    main()
