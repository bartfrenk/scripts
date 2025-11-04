import math
from PIL import Image as image
from PIL.Image import Image
from aggdraw import Draw, Pen, Brush, Font
from typing import Iterator, TypeAlias, Iterable
from argparse import ArgumentParser, Namespace
from dataclasses import dataclass
from pathlib import Path
import random


Point: TypeAlias = tuple[float, float]
Pixel: TypeAlias = tuple[int, int, int]


def splice(points: Iterable[Point]) -> Iterator[float]:
    for x, y in points:
        yield x
        yield y


class Hexagon:
    def __init__(self, radius: float, center: Point):
        self._radius = radius
        self.center = center

    def points(self) -> Iterator[Point]:
        x, y = self.center
        for angle in range(0, 360, 60):
            u = x + math.cos(math.radians(angle)) * self._radius
            v = y + math.sin(math.radians(angle)) * self._radius
            yield (u, v)

    def sample(self) -> Iterator[tuple[int, int]]:
        x, y = self.center
        while True:
            radius = random.uniform(0, math.sin(math.pi / 3) * self._radius)
            angle = random.uniform(0, 360)
            yield (
                int(x + math.cos(math.radians(angle)) * radius),
                int(y + math.sin(math.radians(angle) * radius)),
            )


def lines(points: list[Point]) -> list[tuple[Point, Point]]:
    def it():
        p = None
        for q in points:
            if p is not None:
                yield (p, q)
            p = q
        yield (points[-1], points[1])

    return list(it())


def take[X](n: int, it: Iterable[X]) -> Iterator[X]:
    for i, x in enumerate(it):
        if i >= n:
            break
        yield x


def merge(pixels: list[Pixel]) -> Pixel:
    n = len(pixels)
    if n == 0:
        return (0, 0, 0)
    p = [0, 0, 0]
    for pixel in pixels:
        p[0] += pixel[0]
        p[1] += pixel[1]
        p[2] += pixel[2]
    return (int(p[0] / n), int(p[1] / n), int(p[2] / n))


def valid_pixels(img: Image, it: Iterable[tuple[int, int]]) -> Iterator[Pixel]:
    for attempt, point in enumerate(it):
        try:
            yield img.getpixel(point)  # type: ignore
        except IndexError:
            pass
        attempt += 1
        if attempt > 200:
            break


class Tiling:
    def __init__(self, radius: float):
        self._radius = radius

    def center(self, row: int, col: int) -> Point:
        # TODO: Offset should be configurable
        x = 172 + (col + 0.5 * (row % 2)) * self._radius * 3
        y = 204 + row * math.sin(math.pi / 3) * self._radius
        return (x, y)

    def hexagon(self, row: int, col: int) -> Hexagon:
        return Hexagon(self._radius, self.center(row, col))

    def draw(self, img: Image, pen: Pen, opacity: int = 255) -> None:
        print(opacity)
        SIZE = 84
        # TODO: Should have the same color as the hexes
        font = Font("white", "/usr/local/share/fonts/ttf/hack/HackNerdFont-Bold.ttf", SIZE)
        draw = Draw(img)
        row, col = (-1, 0)
        count = 0
        while True:
            hexagon = self.hexagon(row, col)
            pixels = list(take(100, valid_pixels(img, hexagon.sample())))
            color = merge(pixels)
            brush = Brush((color[0], color[1], color[2], opacity))
            points = list(hexagon.points())

            if True:  # row == -1:
                draw.polygon(list(splice(points)), pen, brush)
                draw.text(
                    (int(hexagon.center[0] - SIZE / 2), int(hexagon.center[1] - SIZE / 2)),
                    str(count),
                    font,
                )
                count += 1
            if any(p[0] > img.size[0] for p in points):
                row += 1
                col = 0
                if all(p[1] > img.size[1] for p in points):
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
    parser.add_argument("--stroke", "-s", type=int, default=3)
    parser.add_argument("--color", "-c", type=str, default="black")
    parser.add_argument("--paper", "-p", choices=list(PAPER_SIZES.keys()), default="a4")
    parser.add_argument("--input", "-i", type=Path)
    parser.add_argument("--opacity", "-o", type=float, default=1)
    return parser


def get_base_image(args: Namespace):
    if args.input:
        return image.open(args.input)
    return PAPER_SIZES[args.paper].img(args.resolution)


def main():
    args = create_parser().parse_args()
    tiling = Tiling(radius=args.radius * args.resolution)
    img = get_base_image(args)
    tiling.draw(img, Pen(args.color, args.stroke), int(args.opacity * 255))
    img.show()


if __name__ == "__main__":
    main()
