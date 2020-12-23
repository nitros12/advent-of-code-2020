from typing import List
from collections import deque

def part1(inp: List[int]):
    cups = deque(inp)
    min_cup = min(cups)
    max_cup = max(cups)
    knowncups = set(inp)

    for _ in range(100):
        current, a, b, c = cups.popleft(), cups.popleft(), cups.popleft(), cups.popleft()
        cups.append(current)

        target = current - 1
        while target not in knowncups or (target == a) or (target == b) or (target == c):
            target -= 1
            if target < min_cup:
                target = max_cup

        idx = cups.index(target) + 1
        cups.insert(idx, c)
        cups.insert(idx, b)
        cups.insert(idx, a)
    idx = cups.index(1)
    lcups = list(cups)
    return "".join(map(str, lcups[idx + 1:] + lcups[:idx]))

def part2(inp: List[int]):
    min_cup = min(inp)
    max_cup = max(inp)
    cups = inp + list(range(max_cup + 1, 1000000 + 1))
    map = {a: b for a, b in zip(cups, cups[1:])}
    map[cups[-1]] = cups[0]
    current = cups[0]

    for i in range(10000000):
        if i % 10000 == 0:
            print("tick ", i)
        a = map[current]
        b = map[a]
        c = map[b]
        after = map[c]

        #
        #  current -> a -> b -> c -> after
        #

        target = current - 1
        while (target < min_cup) or (target == a) or (target == b) or (target == c):
            target -= 1
            if target < min_cup:
                target = 1000000

        map[c] = map[target]

        #
        # target -> x -> ...
        # current -> a -> b -> c -> x -> ...
        # after -> ...
        #

        map[current] = after

        #
        # target -> x -> ...
        # current -> after -> ...
        # a -> b -> c -> x -> ...
        #

        map[target] = a

        #
        # target -> a -> b -> c -> x -> ...
        # current -> after ->
        #

        current = after

    a = map[1]
    b = map[a]
    return a * b

ex_inp = [int(i) for i in "389125467"]
print(part1(ex_inp))
inp = [int(i) for i in "326519478"]
print(part2(inp))
