from collections import defaultdict
import math
from itertools import product
from dataclasses import dataclass
from typing import Dict, Set, Tuple, List, Optional
from copy import copy


@dataclass
class Tile:
    number: int
    data: List[str]
    top: str
    bottom: str
    left: str
    right: str

@dataclass(frozen=True)
class TileInformation:
    position: int

@dataclass
class Assignment:
    tile_no: int
    ti: TileInformation

    top: Optional[int] = None
    bottom: Optional[int] = None
    left: Optional[int] = None
    right: Optional[int] = None


@dataclass(frozen=True)
class AssignmentToFill:
    tile_no: int
    side: str

def generate_possible_joins(tile: Tile, side: str) -> List[Tuple[int, str]]:
    out = []
    for pos in range(8):
        top, bottom, left, right = tile.top, tile.bottom, tile.left, tile.right

        for _ in range(pos % 4):
            top, right, bottom, left = left[::-1], top, right[::-1], bottom

        if pos >= 4:
            bottom = bottom[::-1]
            top = top[::-1]
            left, right = right, left

        side_to_use = {"top": top,
                       "right": right,
                       "bottom": bottom,
                       "left": left }[side]
        out.append((pos, side_to_use))
    return out

def invert_side(side: str) -> str:
    return {"left": "right", "right": "left", "top": "bottom", "bottom": "top"}[side]

def update_with_assignment(current: Dict[int, Assignment], to_add: Assignment) -> Dict[int, Assignment]:
    existing = current.get(to_add.tile_no)

    new_assigns = {**current}

    if existing is None:
        new_assigns[to_add.tile_no] = to_add
        return new_assigns

    existing = copy(existing)

    for attr in ["top", "bottom", "left", "right"]:
        val = getattr(to_add, attr)
        if val is not None:
            setattr(existing, attr, val)

    new_assigns[to_add.tile_no] = existing
    return new_assigns

def count_assignments(assignments: Dict[int, Assignment]) -> int:
    total = 0
    for ass in assignments.values():
        for_this = 0
        for attr in ["top", "bottom", "left", "right"]:
            val = getattr(ass, attr)
            if val is not None:
                for_this += 1
        if for_this not in (2, 3, 4):
            return 0  # invalid
    return total

def try_with_assignment(
        # map of (side, value) to [(tile number, rotation_info)]
        inverse_side_map: Dict[Tuple[str, str], List[Tuple[int, TileInformation]]],
        # map of (tile number, side, tileinfo) to value
        specific_side_map: Dict[Tuple[int, str, TileInformation], str],
        # map of (tile number, side) to [(value, tileinfo)]
        all_side_map: Dict[Tuple[int, str], List[Tuple[str, TileInformation]]],
        # map of tile num to tile
        tiles: Dict[int, Tile],
        # map of tile num to assigment for that tile
        assignments: Dict[int, Assignment],
        to_fill: Set[AssignmentToFill],
        total_assignnments: int,
        needed_assignments: int,
        depth: int = 0,
) -> Optional[Dict[int, Assignment]]:
    if not to_fill:
        if count_assignments(assignments) == needed_assignments:
            return assignments
        print(f"giving up with {count_assignments(assignments)} of {needed_assignments} assignments")
        return None

    to_fill = set(to_fill)

    while to_fill:
        side_to_fill = to_fill.pop()
        assignment = assignments.get(side_to_fill.tile_no)
        if assignment and getattr(assignment, side_to_fill.side) is not None:
            continue

        if assignment:
            possible_values = [(specific_side_map[(side_to_fill.tile_no, side_to_fill.side, assignment.ti)], assignment.ti)]
        else:
            possible_values = all_side_map[(side_to_fill.tile_no, side_to_fill.side)]


        candidate_side = invert_side(side_to_fill.side)
        candidates = []

        # print(' ' * depth, "ps", possible_values)

        for v, ti in possible_values:
            c = inverse_side_map.get((candidate_side, v))
            if c is None:
                continue

            for candi_n, candi_in in c:
                if candi_n == side_to_fill.tile_no:
                    continue

                candi_ass = assignments.get(candi_n)
                # if the candidate tile has an assignnment and the rotation/flips does not match,
                # or if it has an assignment to the side we're wanting to assign,
                # skip it
                if candi_ass is not None and ((candi_in != candi_ass.ti) or getattr(candi_ass, candidate_side) is not None):
                    if getattr(candi_ass, candidate_side) is not None:
                        print(f"[{side_to_fill}] skipping candidate {candi_n}: {candi_ass} because it is already assigned")
                    continue

                # otherwise it is a valid candidate
                candidates.append((ti, candi_n, candi_in))

        # print(' ' * depth, "candidates", candidates)

        # now try each candidate side
        for this_ti, candi_n, candi_ti in candidates:
            this_assignment = Assignment(side_to_fill.tile_no, this_ti)
            setattr(this_assignment, side_to_fill.side, candi_n)

            candi_assignment = Assignment(candi_n, candi_ti)
            setattr(candi_assignment, candidate_side, side_to_fill.tile_no)

            assignments_next = update_with_assignment(assignments, this_assignment)
            assignments_next = update_with_assignment(assignments_next, candi_assignment)

            # all sides for the current tile are already there
            # just generate the sides to fill for the candidate

            unfilled_candidate_sides = generate_remaining_assignments(candi_n, unfilled_sides(assignments_next[candi_n]))

            to_fill_next = to_fill | unfilled_candidate_sides

            # print(specific_side_map[(side_to_fill.tile_no, side_to_fill.side, this_ti)],
            #     specific_side_map[(candi_n, candidate_side, candi_ti)]
            #     )

            # print(f"{' ' * depth}trying to assign the {side_to_fill.side} of {side_to_fill.tile_no} {this_ti} to the {candidate_side} of {candi_n} {candi_ti}")

            res = try_with_assignment(inverse_side_map, specific_side_map, all_side_map,
                                      tiles, assignments_next, to_fill_next, total_assignnments + 2,
                                      needed_assignments, depth + 1)
            if res is not None:
                return res


    if total_assignnments == needed_assignments:
        return assignments

    # dead end
    return None

def unfilled_sides(ass: Assignment) -> List[str]:
    return [i for i in ["top", "left", "bottom", "right"] if getattr(ass, i) is None]

def generate_remaining_assignments(tile_no: int, unfilled: List[str]) -> Set[AssignmentToFill]:
    return {AssignmentToFill(tile_no, s) for s in unfilled}

def find_corner(assignments: Dict[int, Assignment], dirs: Tuple[str, str]) -> int:
    curr = next(iter(assignments.values()))
    while True:
        n = getattr(curr, dirs[0])
        if n is None:
            n = getattr(curr, dirs[1])
        if n is None:
            return curr.tile_no
        curr = assignments[n]

def part1(tiles: List[Tile]):
    width = int(math.sqrt(len(tiles)))
    tiles_map = {tile.number: tile for tile in tiles}

    inverse_side_map = defaultdict(list)
    specific_side_map = {}
    all_side_map = defaultdict(list)

    for t in tiles:
        for s in ["top", "left", "bottom", "right"]:
            for pos, val in generate_possible_joins(t, s):
                info = TileInformation(pos)
                inverse_side_map[(s, val)].append((t.number, info))
                specific_side_map[(t.number, s, info)] = val
                all_side_map[(t.number, s)].append((val, info))

    first_tile = tiles[-1]
    initial_to_fill = generate_remaining_assignments(first_tile.number, ["top", "left", "bottom", "right"])
    total_assignments = 4 * width * width - 4 * width

    r = try_with_assignment(
        inverse_side_map,
        specific_side_map,
        all_side_map,
        tiles_map,
        {},
        initial_to_fill,
        0,
        total_assignments
    )

    assert r is not None, "fuck"

    corners = [find_corner(r, c) for c in product(["top", "bottom"], ["left", "right"])]

    return r, math.prod(corners)

import numpy as np

def generate_tile_array(tile: Tile, info: TileInformation) -> np.array:
    data = tile.data

    for _ in range(info.position % 4):
        data = list(zip(*data[::-1]))

    if info.position >= 4:
        data = [x[::-1] for x in data]

    arr = np.array([[x == "#" for x in row] for row in data])
    return arr

def get_at_coord(x: int, y: int, assignments: Dict[int, Assignment], top_left: int) -> Assignment:
    curr = top_left
    for _ in range(y):
        curr = assignments[curr].bottom
        assert curr is not None
    for _ in range(x):
        curr = assignments[curr].right
        assert curr is not None
    return assignments[curr]

def match_pattern(input_array, pattern):

    pattern_shape = pattern.shape
    input_shape = input_array.shape

    if len(pattern_shape) != len(input_shape):
        raise ValueError("Input array and pattern must have the same dimension")

    shape_difference = [i_s - p_s for i_s, p_s in zip(input_shape, pattern_shape)]

    if any((diff < -1 for diff in shape_difference)):
        raise ValueError("Input array cannot be smaller than pattern in any dimension")

    dimension_iterators = [range(0, s_diff + 1) for s_diff in shape_difference]

    positions = []

    # This loop will iterate over every possible "window" given the shape of the pattern
    for start_indexes in product(*dimension_iterators):
        range_indexes = [slice(start_i, start_i + p_s) for start_i, p_s in zip(start_indexes, pattern_shape)]
        input_match_candidate = input_array[tuple(range_indexes)]

        # This checks that for the current "window" - the candidate - every element is equal
        #  to the pattern OR the element in the pattern is a wildcard
        if np.all(
                (input_match_candidate & pattern) == pattern
        ):
            positions.append(tuple(range_indexes))

    return positions

def print_image(a: np.array):
    print("\n".join(
        "".join(("#" if x else ".") + (" " if i % 10 == 9 else "") for i, x in enumerate(row))
        + ("\n" if y % 10 == 9 else "")
        for y, row in enumerate(a)
    ))

def part2(tiles: List[Tile]):
    tiles_map = {tile.number: tile for tile in tiles}
    solution, _ = part1(tiles)

    length = int(math.sqrt(len(tiles)))
    tile_length = len(tiles[0].data) - 2
    img_length = tile_length * length

    top_left = find_corner(solution, ("top", "left"))
    print("top left: ", top_left)

    image = np.zeros((img_length, img_length), dtype=np.bool)
    print(image.shape)

    for x, y in product(range(length), repeat=2):
        tile_assign = get_at_coord(x, y, solution, top_left)
        tile = tiles_map[tile_assign.tile_no]
        print(f"tile {tile_assign.tile_no} at position {tile_assign.ti}")
        arr = generate_tile_array(tile, tile_assign.ti)[1:-1,1:-1]
        image[y * tile_length : y * tile_length + arr.shape[0], x * tile_length : x * tile_length + arr.shape[1]] = arr

    nessie = np.array([
        [i == "1" for i in "00000000000000000010"],
        [i == "1" for i in "10000110000110000111"],
        [i == "1" for i in "01001001001001001000"]
    ])


    print_image(image)
    print(nessie)

    for i in range(8):
        tmp_image = np.copy(image)
        for _ in range(i % 4):
            tmp_image = np.rot90(tmp_image)
        if i >= 4:
            tmp_image = np.fliplr(tmp_image)
        nessies_here = match_pattern(tmp_image, nessie)
        if not nessies_here:
            continue

        for nessie_pos in nessies_here:
            tmp_image[nessie_pos] &= ~nessie

        return np.sum(tmp_image)

def parse_tile(tile: str) -> Tile:
    num, *data = tile.splitlines()
    num = int(num[len("Tile ") :].strip(":"))

    top = data[0]

    bottom = data[-1]

    left = "".join(l[0] for l in data)

    right = "".join(l[-1] for l in data)

    return Tile(num, data, top, bottom, left, right)


inp_o = """
Tile 3571:
##..##....
..##..#..#
#...##....
.....#...#
..........
...###....
#......##.
#...#...#.
#...##...#
#.####.##.

Tile 2687:
#..##..###
..........
.....##..#
.#.#..##.#
#.#..#..##
#.....#...
#...#.....
##....##..
#...#...##
..#.#.#.##

Tile 3049:
##.#.#.###
....##.###
....##....
#.........
#.#...#..#
#..##....#
#.#......#
#..#..##..
#......###
#.#..#...#

Tile 1597:
###..##...
##.....###
.#..#..#.#
#.......#.
#.#.......
.#..#.....
#.....#...
#........#
##.#...##.
.....#.###

Tile 1301:
#.##.#.###
#........#
....#.....
#.....####
.#....#.##
.....#....
#..##..#.#
.....#..##
.#.##..#.#
#...######

Tile 3259:
..#####.#.
.....#...#
#...#.....
...##...#.
.#..#..##.
.#.......#
........##
#.......#.
.#.#...#..
#...#.#..#

Tile 3989:
#..#..####
..........
#........#
.#....#...
..........
#.........
.#........
#........#
...##.####
.######.##

Tile 3803:
#.####...#
.###.#..#.
....##..#.
#........#
..##..#...
####.#....
..#...#...
#..#.....#
..##....#.
#....#...#

Tile 2897:
.#..##.#.#
..#.#...##
#........#
###.#..#.#
...#..#.##
...#....##
....##...#
.....##..#
.#....#...
..##....##

Tile 2843:
##.###..##
#.#.......
#....#....
#..##.##..
.##..#.##.
#....#....
#.#...#.##
..........
.#...#...#
###..#..##

Tile 3023:
.#..###.#.
.........#
..........
.#........
#.#....#.#
....#...#.
#.......#.
##.#.....#
..#...#..#
.....####.

Tile 2887:
#....##...
#...#.....
##...##...
#.....##.#
.......#..
#......#.#
..##..#..#
....#....#
#.###.....
#.####..#.

Tile 1013:
#..####.#.
#.##...#.#
#..#..#...
#..#..#..#
...#......
#.####...#
.#..##..##
...#.#..##
....##..##
#.##.#.#.#

Tile 3733:
###.##.#.#
..#....#..
#...#.#..#
....###..#
.#........
.....#....
........##
##........
#........#
#.#...#..#

Tile 3691:
.##...####
##..##....
#.#.##..##
#........#
#.....##.#
.....#....
##.#.....#
#..#.....#
..#.......
####....#.

Tile 3061:
##.....#..
.....#...#
....##...#
###.#.....
#..#..###.
#.#.###..#
..#......#
#..#.#...#
..#.......
..#.#..#..

Tile 1489:
###.......
.....##...
..#...##..
#.....#...
#.#......#
##.#..####
...##.#...
...#...#.#
..........
.##.##.#.#

Tile 1637:
#########.
.#.....#..
#........#
#........#
.##.....##
.........#
#....#..##
#.....####
...###...#
.#..##..##

Tile 1069:
#.#...####
##...#...#
.....#...#
.......##.
......#..#
#........#
#...#.....
......#...
#.#..#....
####.##.#.

Tile 1039:
#..#######
###.......
.....#....
#.........
....#....#
...####...
.#...##...
#.#....#.#
........##
#.#..#..#.

Tile 2767:
.#.#..#.##
.#..#....#
#..#.#....
#.#..##..#
.####.#.##
#....##...
....##..##
###.....#.
..........
....#.###.

Tile 2957:
####.#####
.......##.
...#.....#
...##..##.
...##.##..
#..#..#..#
.....#....
#..#....#.
.##.......
.##..#.##.

Tile 2789:
.##..#.#.#
#.#.....##
#....#...#
#....##...
..#..#....
#.........
#.#..#..##
#........#
.#.......#
#####...##

Tile 2837:
.....#...#
.....#.#.#
#.......#.
#...#...#.
..#.....#.
..#.#..#..
##.......#
....#....#
#...#.....
##.###....

Tile 3251:
.######...
...#......
.#.#..###.
#..#.##..#
###.#....#
#.#......#
..#..###..
##.#..#..#
...#...###
##.#..##..

Tile 3137:
#####.#..#
#.#..#.##.
#.#..#....
#.........
.........#
.........#
...#......
#...#...#.
....#..#.#
.#.###.#.#

Tile 3433:
.##..####.
...#......
#..##....#
....#....#
#..###....
..#......#
.#..###...
.##.#.....
.........#
.....#....

Tile 2551:
#.########
#.#.......
##..#...##
#.#..###.#
#........#
.#.#....#.
#........#
.##....#..
#........#
##..##.#..

Tile 2647:
..####..##
##....#..#
#.........
###.#.....
#......#..
....#...##
.#..##.#.#
.#.#..#...
.....##.##
.#.#...#..

Tile 1087:
#..###..##
#...#.#.#.
.......#..
..#.#.#..#
#.......#.
#....#....
....#....#
##...##..#
#..#......
.#..#.###.

Tile 1423:
..#....#.#
#........#
.#.##.##..
#.###.#.#.
#.#......#
...##...##
#....#....
....#....#
.........#
#####....#

Tile 1759:
..#.#..#..
##...#...#
....#..#..
#....#....
.##..##..#
...#.#...#
#..#.....#
##.......#
......#..#
#.##......

Tile 1583:
.###.####.
......###.
......#..#
.#...##...
#...#....#
..#.##....
#...##..#.
......#...
#.....###.
####.#....

Tile 1171:
###......#
#...##...#
#####..##.
#.......#.
#.#...#..#
#....#....
....#....#
##.....#.#
#.#..#..##
#.#.#..##.

Tile 2801:
.###.####.
......#...
##..##.#.#
.....#....
#......#..
###..##..#
##.#..##.#
#..#..#...
#..#.#...#
#..###.###

Tile 1559:
.##..#...#
#.##..#...
...##..#..
..#.#.....
...#...#..
.........#
...#.....#
#..##.#..#
##..##....
...###...#

Tile 2609:
##.#..####
..........
#........#
##.###...#
#.#..#....
..#..##..#
#....#.#.#
#.#.......
#....#...#
#.####.#.#

Tile 2287:
#......#.#
.....#.#.#
..#..#...#
##.#..#...
..#..#.###
.......###
#......##.
#.##.##...
......#..#
#####.##.#

Tile 3659:
.###.#####
#.#.......
..........
..#.....##
#..#......
#.#.#...##
#.........
.#...#....
##.....#..
#####.##.#

Tile 3539:
.......#.#
..##...#..
.....#.#.#
##.#......
####......
...#..#...
#.......##
#...#.....
#..#.....#
.##.#....#

Tile 3121:
..##.#...#
.###..#...
##.#.#....
#.....#..#
#.#.......
#.........
....#...##
......###.
#........#
#..###..##

Tile 2237:
...##.....
..........
...#......
#....#...#
#.........
.......#..
#...###..#
.....#...#
.........#
#.####.##.

Tile 1277:
.###...##.
.......###
#.....##..
#.##..###.
#.#..#....
.....#....
#...#....#
#.#......#
#...###..#
...##...##

Tile 2161:
..#####..#
#....##..#
#.....#..#
....#....#
.....#.##.
..........
#......#.#
#..#......
#....#..##
.##.....#.

Tile 3709:
.#..#...##
#..#.....#
...#....#.
..........
.#...#....
..........
....##....
#.........
.........#
..####....

Tile 1117:
##.##.#..#
.....##...
.#.#..#.##
.#...#..#.
#.##.#....
####.....#
##..#.....
#.........
#...##...#
####..#.#.

Tile 2081:
##.##.###.
#...#.....
#.....#...
#.#..#.#..
#.....#..#
...#.....#
#....#....
......#..#
.#.##..#..
###..#.#.#

Tile 1709:
##...#.##.
###..#....
#.......#.
#.....##..
.........#
#....#..##
..#...##..
#...#.....
#...#.#..#
.###.#....

Tile 2927:
...###..##
##.#......
..........
##........
#....#...#
.......##.
#.....#..#
##.#.#....
#......#..
...#.####.

Tile 1499:
#....##.#.
......#...
#........#
......#...
.#.......#
#.#...#.##
..#....#.#
#...#.....
.........#
#.....##.#

Tile 1453:
#.##.####.
..#...##..
.........#
.........#
#..#..#...
.........#
#....#.#..
#.....#..#
.#........
#....#....

Tile 1283:
.#.##..###
..#...#.#.
...##..#..
#.......#.
#......#..
#..##.....
#.......##
....##...#
..#.....##
##.#.#...#

Tile 2063:
......#.##
.........#
....##..#.
.#....##..
##........
.###.###.#
#.#....#..
....#...#.
#......###
#....####.

Tile 3529:
...###.##.
#....#...#
...#.....#
...#.#..#.
.#.#.....#
#...#.....
##..#..#..
#.....#..#
.#........
.#..#####.

Tile 2657:
..#.##..#.
##..#...##
#.....#...
#....##...
.....#..##
#.#..##.##
#.........
#.#...##.#
##....#...
##..####.#

Tile 2089:
.#########
##.#.##..#
#........#
#..###..##
...#......
##..#....#
#...#..#..
#..#....#.
..#.#....#
...###...#

Tile 3779:
#.#...##.#
.##...##..
.....##...
.#....##.#
###..##..#
#.#..#.#..
....##...#
##...#....
.#...#....
#######...

Tile 3217:
...##.....
....##....
.....##..#
##...#.#.#
###.......
...#...#..
...#.....#
#..#.#.###
##.#...#.#
.#.#..##..

Tile 3907:
..#..##.##
#.#.....##
#.......#.
.#...###..
..###.####
##.#..##..
#.........
##...#..#.
#....#....
.#.....#.#

Tile 3547:
#..#.##...
#..###...#
##.......#
.....#....
#...#...#.
#..#..#...
........#.
......##.#
.......#..
.##.#..##.

Tile 3187:
##.#.##...
#...#.##.#
#...#.....
#....#..##
....#.#..#
.....#....
.....#..##
....##...#
..........
#######.##

Tile 1217:
##.#####..
#.......#.
...#....##
#........#
#.#......#
.....#...#
#.........
....#...##
#...#.....
.#...###.#

Tile 3821:
#.###.###.
#.#......#
#..#.#...#
.##...#.##
...#....##
#...#..##.
#......#.#
###..#...#
.........#
#....##.##

Tile 1607:
##..#..##.
#.##....##
###.##.##.
.#....##.#
#.#..#...#
.....#.#..
#.#..#..#.
#.#..#....
..........
......##.#

Tile 1459:
.###.##..#
#.......#.
##........
..#...####
###.......
#....#....
.#.....#.#
###..#..##
.....#....
..#..#..##

Tile 2129:
....#.#..#
#.....##.#
#........#
..........
..#......#
#.....#..#
.#..##...#
#.#.#..#.#
#.........
#.##....##

Tile 1601:
.#.#.#.#.#
..#..##...
#.#.#...#.
....##....
....##.#..
..#.......
#.....#..#
#..##.#...
.........#
...####.#.

Tile 1801:
#.#...#.#.
..#....#..
#..#...#..
......#...
.....#....
#.#..##.##
#.........
...#.#...#
.#....#..#
#.....##..

Tile 2447:
..#.....##
.#..#...##
.....#.#..
.#....#..#
#...####.#
##.##..###
.#.......#
#.##.....#
#.......##
.###.#...#

Tile 2203:
#.....##..
#.#.......
........##
###...#...
..........
#..#.....#
....#.##.#
..##.....#
.#...#...#
#.###..#..

Tile 1381:
.#...#...#
....#.....
##.......#
#.....#...
.........#
.#.......#
.......##.
#.#.....##
.#..#.##..
##.#.##.#.

Tile 3163:
#...####.#
#......##.
...###.#.#
#....##...
#......###
.....#..##
.#..###...
#..##..#..
#.....#...
#.#####.##

Tile 3673:
.#....##.#
..#..####.
#.....#...
...#....#.
#....#...#
#....##.#.
##...#.#..
.#..#.#...
#..#.....#
####.##...

Tile 3919:
....##.##.
##..##....
...##...##
#...#.....
..........
....#..###
.#.....#..
....#..#.#
.##..#....
.#...###.#

Tile 2437:
..##...#.#
#....#...#
#..#.....#
..#.#...##
.......#..
........##
........##
.......#.#
#....#.#.#
##..#.###.

Tile 2969:
##.#.##.#.
#.##....#.
.##......#
#.#.#....#
#.#.......
.........#
....#.#.##
.#.......#
...#..#.##
##.#.##..#

Tile 2621:
.##.##.#..
.##...#...
..........
#.........
#.#.#.#..#
..#..#...#
.......#.#
#.#.....##
...#..#...
#.......##

Tile 3613:
##..#....#
#..##.....
..#.......
..#...#...
...#...#..
...#.....#
..#.....#.
..#.###..#
..........
..#.####..

Tile 2777:
##.#####.#
#.##.#...#
..#.......
.##...##.#
.........#
.#.###.##.
#......##.
#......##.
#...##..##
#..#....##

Tile 2711:
#..#..##..
..........
#.#......#
#.....####
..........
##.......#
........#.
#.......#.
#.#..#...#
#.#.####.#

Tile 2281:
.#.###...#
###....#..
..........
#.#..#..##
.........#
###..#.##.
####..#..#
##..#.....
##..#..#..
#.....#..#

Tile 1579:
....#..#..
#........#
#...#..#..
..##.#.#..
.###.#...#
....##..#.
...##.#...
.#.##....#
.#.......#
##...#...#

Tile 2411:
#.#....##.
..#...#..#
.#..##....
.#..##...#
.....#.#.#
......##..
#.#....###
.#.##....#
..#..#....
..#.###..#

Tile 2963:
.......##.
.....#....
.........#
#.....#..#
.....#.#..
.....#.##.
.#.#...###
#.#.......
.#.......#
###..#..#.

Tile 1693:
#.##..##..
..........
.........#
.##..#...#
.........#
#........#
###......#
..#...#...
.#.##....#
...#.#...#

Tile 2399:
###.#.##..
#...#.....
...#...#.#
###.......
.##.##....
##.....#.#
####......
##.......#
#..#...#.#
#...#.....

Tile 1913:
##.....###
........##
#.....###.
..........
....#...#.
#.#.....#.
#....#...#
..#...#...
....#..#..
#..####...

Tile 3343:
.....#.##.
..#...#...
####.....#
....#.....
......#..#
......#...
#........#
#.......#.
..#...#.#.
.....###.#

Tile 2557:
#.......##
....#...##
#......#.#
#.#.#.#.##
#..##.....
..###.#.#.
#..#......
#...#.....
....#....#
#.##...#.#

Tile 1097:
.#.#.#..##
..#.#.....
##........
.##...##..
..#..#...#
#........#
........##
#.#.#.....
.#.#.....#
#.##..#...

Tile 2591:
##..#..###
......#...
...###.#..
#.......#.
#.#.....#.
#.##..#...
....##.#..
#.#..#...#
#.###..#.#
##........

Tile 3413:
...##...##
..#....#..
##.#....#.
#..#....#.
#........#
#..#......
#.....#.##
##.....#.#
#....#....
####.#...#

Tile 2087:
###..###.#
##......#.
#..#...#.#
#.#.......
##.#.....#
#.#.#.....
...#.....#
..........
#.........
#.##..###.

Tile 3037:
......##..
..#..#....
#.#.......
#.#....#..
.#.#.##..#
#.....#.##
#.....#.#.
.#..##...#
#....##...
...#..###.

Tile 2239:
.####..#..
#.........
.#.......#
#..##.....
##..##..##
#.#....#..
.........#
#.......#.
....#.....
#.###..#.#

Tile 3313:
##.##.#..#
.#.#..#...
.##...##.#
.#.##..#..
##........
..........
#..#.#....
#.........
..........
.##..#..#.

Tile 3361:
.###.#...#
##..#.#..#
...##....#
#..##.....
..........
#......#.#
.........#
..#..##.#.
#..#...###
#...#.#.#.

Tile 3167:
..##..####
#.....#.#.
.....#.#..
...#......
....#.#.##
...#.#.#..
.......#..
##........
#..#...#.#
####.##..#

Tile 1979:
#.#.###...
..#.....##
...#...##.
#.......##
........##
..##..#...
..#......#
#.#....#.#
#..#.....#
.##.......

Tile 1831:
##.##.##.#
#.........
.........#
##.......#
###.....##
..##..##..
##.....#.#
#....#...#
###.##..#.
#..#####..

Tile 1487:
#..#....##
.#..#....#
#....#....
#.........
#.#...#.##
#..##...##
...##..#..
.#...##...
.#........
.#...#..#.

Tile 1987:
###..#....
##..##...#
......#..#
.#.#...#.#
.....#.#..
....#..#..
....###..#
#...##....
###.....#.
...##.####

Tile 3083:
....##..#.
##..#.###.
#..#...##.
#.###.....
.........#
....#.....
.#........
.#........
#.........
#.#.#.##.#

Tile 1543:
...##..###
.........#
.......#.#
#..#..#.##
##....#.#.
....#..#..
#..#......
...#...#.#
##.##..#..
#.###..#..

Tile 1151:
#.#..#####
#.#..#...#
#..#......
....#...#.
..........
#...#.#..#
#..#.#...#
##....#..#
#.........
##.....###

Tile 1009:
##..#...##
#....#...#
.#...#....
#........#
.#..#..#..
.###.##.#.
#......#.#
##.#..##..
#....#.###
####...##.

Tile 3929:
......#.#.
#..#.##.##
....#.#.##
#.##..#...
###..#..#.
.##..###.#
.##......#
....#....#
........#.
.#...###..

Tile 1321:
#.##..#...
.##.....##
#.#..#....
...#.....#
###......#
#.#.#.##.#
##.......#
##......#.
.#...#....
.#..##..##

Tile 2017:
###.#..###
.#..###..#
#..#......
.........#
..#...##..
....#.##.#
...##.#..#
....#...##
#..#..##..
##.#.#.#..

Tile 1747:
....##.#..
#........#
.....#..#.
..#####...
######..#.
##..#.#...
.###..#..#
#.....#...
.##..#..##
..#####...

Tile 3089:
#....#.##.
#.....#..#
..........
#..#.#....
.......#..
#.....#...
........#.
##..#..##.
#.....#..#
#.#.#....#

Tile 3019:
.#..###.##
.#...#...#
#.#.......
###.......
#....#...#
#.##...#..
##........
.#.......#
.#.#......
.#..#...#.

Tile 3079:
...#.###..
#......#..
#.......##
#...#..###
#.......#.
......#.#.
#........#
.#.#...###
..#.#....#
...#...#.#

Tile 1663:
##.##..###
#.....##.#
......#.##
#........#
..#.#.....
....#..#.#
#.#.#..#.#
#.......#.
..#......#
#.#..#....

Tile 1823:
.###...###
#.#.#..##.
..........
.........#
###....#..
..........
##....#.##
#.......##
..#..#...#
......####

Tile 3823:
....#..#..
..#.#..#.#
###.#.##.#
..##....#.
#.........
#....#...#
#.......##
#.#...##..
..#....#..
..#....##.

Tile 1901:
#.#.#....#
..#....#.#
...#..#.#.
.#..#..###
....####..
......#...
#....#....
..#....#..
#......#..
######.#..

Tile 3347:
#.#.....#.
#..#..#...
#.#.......
#..#.#....
...#......
#.........
##.#.....#
#........#
#....#...#
#.#.##.###

Tile 1873:
..###.#.##
.#.#....#.
#........#
..#..#...#
##.....#..
#........#
#.........
.#........
#.#..#.#.#
.##.#...##

Tile 2053:
#.#.#.#..#
#...###..#
##.##.##.#
....##.#.#
#.###....#
#.....#..#
#..##.####
....#..#..
#.........
#..#.#..#.

Tile 2659:
.#....##.#
#.#......#
#..#......
.#.###.#.#
..........
#........#
.......#.#
....#....#
#........#
##..##.#..

Tile 2503:
.#..####.#
#.##......
..#....###
..#..#.###
...##...##
..#.....#.
..........
##.#......
#.#.......
#...#..#.#

Tile 3881:
##.###.###
#......#..
#...#....#
..#.#....#
#..#..#..#
#..#.....#
...#..##.#
#.#.......
#..##....#
...#.##...

Tile 1973:
..#.###.#.
#.##....##
#.......##
##......##
#.........
#.#..#....
.#....###.
..#.#..#..
......#..#
#..#.....#

Tile 3329:
.#.#.###.#
..#.#.....
.#.......#
#..#.##.##
#.##..####
..#.##..##
....#.....
#...#.#.#.
...#.#...#
.#...##..#

Tile 3331:
#......###
#......#.#
#.#.#.#..#
........#.
.##.####..
#..#..#..#
.#.......#
......#.##
......#.#.
.##...#.#.

Tile 1307:
##.#.#..#.
.........#
.#....##.#
#.........
#.........
#....#.#..
........##
......##..
..#.##...#
..##...##.

Tile 2543:
.#.#.##.##
#........#
..##......
#.........
##...#...#
.###..##.#
.##......#
.#........
.....#.#..
...######.

Tile 2003:
#.#..#.#.#
.....#....
#.#.#.....
####.#..##
..###....#
....#.#...
#.####...#
.##...#.##
#.#.#..#..
...#.....#

Tile 3301:
##....##.#
.....#...#
#........#
..........
###.##.#..
.....#...#
#.#......#
....##...#
#........#
.#.#...#.#

Tile 2297:
#..#.##..#
...#.#.##.
..###..#..
##..#.....
####..#..#
..#.#..#..
.....#...#
#...#.....
#.....#..#
##....#...

Tile 2311:
##.....#.#
##........
#........#
#...##....
#......#..
.........#
.........#
#..#.#....
.....#...#
###.#..##.

Tile 1361:
.#.##.#..#
#.#..#...#
#....###..
..###.#...
#..#.....#
#..#...##.
#.#.....#.
.......#.#
##.##.....
#.###.#..#

Tile 1481:
.####.#.##
..........
.........#
###.#.#...
##....##.#
..#...#.##
..##.#.#..
#.#.....##
.......#..
....###...

Tile 1153:
.##.##..##
###......#
#....##...
......#.#.
#....#....
.....##..#
.....#...#
#.........
#...#....#
##..#.#...

Tile 2153:
#.###.#..#
..#.##....
..##....#.
##...#...#
#...#.....
........#.
#..##...#.
..#.......
#...##.#..
#.#.#.#...

Tile 2377:
.##..##.#.
...##..#.#
#.#.#.....
#.##......
#.....#..#
#...#....#
...##....#
...###....
.#.##...##
.###.##...

Tile 3863:
.##.###.##
.......#.#
#........#
##.#.#...#
##...#...#
#...##....
#..#..#.##
.....#####
##.#..###.
....###...

Tile 1163:
##..######
#........#
.#.#...###
..#..#...#
##..#...##
#.#.......
#.#..#....
#..#.#....
###..#...#
.#####.###

Tile 2207:
.#..#.#.##
##.....#.#
#..#.....#
#..#....##
.........#
...#.....#
#...#..#..
..#.....##
.....#....
#.##.....#

Tile 1201:
#.##.##..#
#.#.......
#..#.....#
.###...#..
#.#......#
........##
.........#
.##....#.#
..##.#...#
.......###

Tile 1619:
#.....#.#.
...#.##..#
#.....#...
#...#.....
#..#...#.#
#..##.#...
.#...#.#..
#......##.
#.........
#.##...###

Tile 3389:
...#..##..
#........#
#...#.....
#.#....#.#
###....#.#
#.#....###
#..##..#.#
.##.#.#..#
#...###...
#...#....#

Tile 3359:
.###..##..
#........#
###...#.#.
........##
....#..#.#
.#.#......
#........#
.......#.#
.#.....#..
##.###....
""".strip().split(
    "\n\n"
)

inp = [parse_tile(x) for x in inp_o]

ex_inp_o = """
Tile 2311:
..##.#..#.
##..#.....
#...##..#.
####.#...#
##.##.###.
##...#.###
.#.#.#..##
..#....#..
###...#.#.
..###..###

Tile 1951:
#.##...##.
#.####...#
.....#..##
#...######
.##.#....#
.###.#####
###.##.##.
.###....#.
..#.#..#.#
#...##.#..

Tile 1171:
####...##.
#..##.#..#
##.#..#.#.
.###.####.
..###.####
.##....##.
.#...####.
#.##.####.
####..#...
.....##...

Tile 1427:
###.##.#..
.#..#.##..
.#.##.#..#
#.#.#.##.#
....#...##
...##..##.
...#.#####
.#.####.#.
..#..###.#
..##.#..#.

Tile 1489:
##.#.#....
..##...#..
.##..##...
..#...#...
#####...#.
#..#.#.#.#
...#.#.#..
##.#...##.
..##.##.##
###.##.#..

Tile 2473:
#....####.
#..#.##...
#.##..#...
######.#.#
.#...#.#.#
.#########
.###.#..#.
########.#
##...##.#.
..###.#.#.

Tile 2971:
..#.#....#
#...###...
#.#.###...
##.##..#..
.#####..##
.#..####.#
#..#.#..#.
..####.###
..#.#.###.
...#.#.#.#

Tile 2729:
...#.#.#.#
####.#....
..#.#.....
....#..#.#
.##..##.#.
.#.####...
####.#.#..
##.####...
##..#.##..
#.##...##.

Tile 3079:
#.#.#####.
.#..######
..#.......
######....
####.#..#.
.#...#.##.
#.#####.##
..#.###...
..#.......
..#.###...
""".strip().split(
    "\n\n"
)

ex_inp = [parse_tile(x) for x in ex_inp_o]

print(part1(inp))
print(part2(inp))
