import itertools
import copy
from os.path import join

offsets = set(itertools.product([1, 0, -1], repeat=3)) - {(0, 0, 0)}


class Bounds:
    def __init__(self, x, y, z) -> None:
        self.x_l = x[0]
        self.x_u = x[1]
        self.y_l = y[0]
        self.y_u = y[1]
        self.z_l = z[0]
        self.z_u = z[1]

    def expand(self, c):
        x, y, z = c

        if x < self.x_l:
            self.x_l = x

        if x > self.x_u:
            self.x_u = x

        if y < self.y_l:
            self.y_l = y

        if y > self.y_u:
            self.y_u = y

        if z < self.z_l:
            self.z_l = z

        if z > self.z_u:
            self.z_u = z

    def range(self):
        return itertools.product(
            range(self.x_l - 1, self.x_u + 2),
            range(self.y_l - 1, self.y_u + 2),
            range(self.z_l - 1, self.z_u + 2),
        )

    def x_range(self):
        return range(self.x_l, self.x_u)

    def y_range(self):
        return range(self.y_l, self.y_u)

    def z_range(self):
        return range(self.z_l, self.z_u)


def vec_add(a, b):
    return tuple(x + y for x, y in zip(a, b))


def count_live(space, c):
    return sum(vec_add(c, o) in space for o in offsets)


def print_s(space, bounds):
    for z in bounds.z_range():
        t = "\n".join(
            "".join("#" if (x, y, z) in space else "." for x in bounds.x_range())
            for y in bounds.y_range()
        )
        print(f"{z=}")
        print(t)


def step(space, bounds):
    out = set()
    new_bounds = copy.copy(bounds)

    for c in bounds.range():
        was_live = c in space
        live_n = count_live(space, c)

        if was_live:
            if live_n in (2, 3):
                out.add(c)
        else:
            if live_n == 3:
                out.add(c)
                new_bounds.expand(c)

    return out, new_bounds


def part1(inp):
    bounds = Bounds((0, len(inp[0])), (0, len(inp)), (0, 1))
    space = set()

    for y, row in enumerate(inp):
        for x, v in enumerate(row):
            if v:
                space.add((x, y, 0))

    for i in range(6):
        print(f"step = {i}\n")
        print_s(space, bounds)
        space, bounds = step(space, bounds)

    return len(space)


inp = """
#...#.#.
..#.#.##
..#..#..
.....###
...#.#.#
#.#.##..
#####...
.#.#.##.
""".strip().splitlines()

inp = [[x == "#" for x in l] for l in inp]

ex_inp = """
.#.
..#
###
""".strip().splitlines()

ex_inp = [[x == "#" for x in l] for l in ex_inp]
