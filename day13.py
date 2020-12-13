def part1(inp_t, inp):
    min = 99999999
    min_v = 999999999
    for i in inp:
        x = i - (inp_t % i)
        if x < min:
            min_v = i
            min = x
    return min_v * min

def part2(inp):
    import z3

    inps = [(i, x) for i, x in enumerate(inp) if x != "x"]

    ts = z3.Int("t")

    cs = [ts > 0]

    for a, n in inps:
        cs.append(((ts + a) % n) == 0)

    print(cs)
    z3.solve(*cs)

from functools import reduce

def egcd(a, b):
    if a == 0:
        return (b, 0, 1)
    else:
        g, x, y = egcd(b % a, a)
        return (g, y - (b // a) * x, x)

def modinv(b, n):
    g, x, _ = egcd(b, n)
    if g == 1:
        return x % n

def chinese_remainder(n, a):
    sum = 0
    prod = reduce(lambda a, b: a*b, n)

    for n_i, a_i in zip(n, a):
        p = prod // n_i
        sum += a_i * modinv(p, n_i) * p
    return sum % prod

def part2_notbad(inp):
    m = max(i for i, x in enumerate(inp) if x != "x")
    inps = [(m - i, x) for i, x in enumerate(inp) if x != "x"]
    a, n = list(zip(*inps))


    print(n, a)

    return chinese_remainder(n, a) - m

inp_id = 1001612
inp_o = """
19,x,x,x,x,x,x,x,x,41,x,x,x,37,x,x,x,x,x,821,x,x,x,x,x,x,x,x,x,x,x,x,13,x,x,x,17,x,x,x,x,x,x,x,x,x,x,x,29,x,463,x,x,x,x,x,x,x,x,x,x,x,x,x,x,x,x,x,x,x,x,x,x,23
""".strip().split(",")

inp = [int(i) for i in inp_o if i != "x"]
inp_2 = [int(i) if i != "x" else i for i in inp_o]


ex_inp_id = 939
ex_inp_o = """
7,13,x,x,59,x,31,19
""".strip().split(",")

ex_inp = [int(i) for i in ex_inp_o if i != "x"]
ex_inp_2 = [int(i) if i != "x" else i for i in ex_inp_o]
