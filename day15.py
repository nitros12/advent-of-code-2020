from collections import defaultdict


def part1(nums, n):
    ls = defaultdict(lambda: (0, 0))

    last_spoken = 0

    for i, x in enumerate(nums):
        ls[x] = (0, i + 1)
        last_spoken = x

    for i in range(len(nums), n):
        (turn_n2, turn_n1) = ls[last_spoken]

        if turn_n2 == 0:
            last_spoken = 0
        else:
            last_spoken = turn_n1 - turn_n2

        (_, lt) = ls[last_spoken]

        ls[last_spoken] = (lt, i + 1)

    return last_spoken


inp_o = """
0,14,1,3,7,9
""".strip()

inp = [int(i) for i in inp_o.split(",")]

ex_inp_o = """
0,3,6
""".strip()

ex_inp = [int(i) for i in ex_inp_o.split(",")]
