import math
from PIL import Image as image
from PIL.Image import Image
from aggdraw import Draw, Pen
from typing import Iterator, TypeAlias, Iterable
from argparse import ArgumentParser
from dataclasses import dataclass


Point: TypeAlias = tuple[float, float]


def splice(points: Iterable[Point]) -> Iterator[float]:
    for x, y in points:
        yield x
        yield y


class Hexagon:
    def __init__(self, radius: float, center: Point):
        self._radius = radius
        self._center = center

    def points(self) -> Iterator[Point]:
        x, y = self._center
        for angle in range(0, 360, 60):
            x += math.cos(math.radians(angle)) * self._radius
            y += math.sin(math.radians(angle)) * self._radius
            yield (x, y)


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

    def draw(self, img: Image, pen: Pen) -> None:
        draw = Draw(img)
        row, col = (-1, 0)
        while True:
            points = list(self.hexagon(row, col).points())
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


@dataclass
class PaperSize:
    width: float
    height: float

    def img(self, resolution: int) -> Image:
        size = (int(self.width * resolution), int(self.height * resolution))
        return image.new("RGB", size, "white")


PAPER_SIZES = {"a4": PaperSize(8.3, 11.7)}


def create_parser() -> ArgumentParser:
    parser = ArgumentParser()
    parser.add_argument("--resolution", type=int, default=300)
    parser.add_argument("--radius", type=float, default=0.65)
    parser.add_argument("--width", "-w", type=int, default=3)
    parser.add_argument("--color", "-c", type=str, default="black")
    parser.add_argument("--paper", "-p", choices=list(PAPER_SIZES.keys()), default="a4")
    return parser


def main():
    args = create_parser().parse_args()
    tiling = Tiling(radius=args.radius * args.resolution)
    img = PAPER_SIZES[args.paper].img(args.resolution)
    tiling.draw(img, Pen(args.color, args.width))
    img.show()


if __name__ == "__main__":
    main()
