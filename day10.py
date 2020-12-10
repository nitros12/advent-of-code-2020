from collections import defaultdict, deque
from typing import List
import functools


def part1(adaptors: List[int]):
    adaptors.sort()
    diffs = []

    diffs.append(adaptors[0])

    for a, b in zip(adaptors, adaptors[1:]):
        diffs.append(b - a)

    diffs.append(3)

    is_1 = sum(1 for i in diffs if i == 1)
    is_3 = sum(1 for i in diffs if i == 3)

    return is_1 * is_3


@functools.cache
def try_path(current: int, adaptors, idx: int) -> int:
    if idx == len(adaptors):
        return 1

    adaptor = adaptors[idx]

    if (adaptor - current) > 3:
        return 0

    by_taking = try_path(adaptor, adaptors, idx + 1)
    return by_taking + try_path(current, adaptors, idx + 1)

def part2(adaptors: List[int]):
    adaptors.sort()

    return try_path(0, tuple(adaptors), 0)

import numpy as np

def part2np(adaptors: List[int]):
    adaptors.append(0)
    adaptors.append(max(adaptors) + 3)
    adaptors.sort()

    reverse_indexes = {e: i for i, e in enumerate(adaptors)}

    matrix = np.zeros((len(adaptors), len(adaptors)))

    for i, e in enumerate(adaptors):
        for r in range(1, 4):
            if e + r in adaptors:
                matrix[i, reverse_indexes[e + r]] = 1

    total = 0

    m = matrix
    n = len(adaptors) - 1

    for i in range(len(adaptors)):
        total += m[0, n]
        m = m @ matrix

    return total


inp = """
95
43
114
118
2
124
120
127
140
21
66
103
102
132
136
93
59
131
32
9
20
141
94
109
143
142
65
73
27
83
133
104
60
110
89
29
78
49
76
16
34
17
105
98
15
106
4
57
1
67
71
14
92
39
68
125
113
115
26
33
61
45
46
11
99
7
25
130
42
3
10
54
44
139
50
8
58
86
64
77
35
79
72
36
80
126
28
123
119
51
22
""".strip().splitlines()

inp = [int(i) for i in inp]

tinp = """
16
10
15
5
1
11
7
19
6
12
4
""".strip().splitlines()

tinp = [int(i) for i in tinp]

tinp2 = """
28
33
18
42
31
14
46
20
48
47
24
23
49
45
19
38
39
11
1
32
25
35
8
17
7
9
4
2
34
10
3
""".strip().splitlines()

tinp2 = [int(i) for i in tinp2]
