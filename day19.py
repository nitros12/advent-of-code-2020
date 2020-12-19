import regex

class CharRule:
    def __init__(self, n: int, c) -> None:
        self.n = n
        self.c = c

    def validate(self, c, rulemap):
        if not c:
            return False, 0
        return c[0] == self.c, 1

    def as_re(self, rulemap):
        return self.c

    def __repr__(self) -> str:
        return f"CharRule(n = {self.n}, c = {self.c})"

class RefRule:
    def __init__(self, n: int, rules) -> None:
        self.n = n
        self.rules = rules
        self.is_exported = False

    def validate_inner(self, c, rulemap, seq):
        tl = 0
        for rule in seq:
            ok, l = rulemap[rule].validate(c, rulemap)
            if not ok:
                return False, 0
            tl += l
            c = c[l:]
        return (True, tl)

    def validate(self, c, rulemap):
        for seq in self.rules:
            ok, l = self.validate_inner(c, rulemap, seq)
            if ok:
                return ok, l
        return False, 0

    def as_re_inner(self, rulemap, seq):
        return "".join(rulemap[i].as_re(rulemap) for i in seq)

    def as_re(self, rulemap):
        if self.is_exported:
            return f"(?&rule_{self.n})"
        self.is_exported = True
        return f"(?P<rule_{self.n}>" + "|".join(self.as_re_inner(rulemap, seq) for seq in self.rules) + ")"

    def __repr__(self) -> str:
        return f"RefRule(n = {self.n}, r = {self.rules})"

def parse_rule(line: str):
    n, r = [x.strip() for x in line.split(":")]
    n = int(n)

    if r[0] == "\"":
        return CharRule(n, r[1])

    pairs = [[int(y) for y in x.strip().split(" ")] for x in r.split("|")]
    return RefRule(n, pairs)

def part1(rules, inp):
    rulemap = {r.n: r for r in rules}
    rule_zero = rulemap[0]
    total = 0

    for line in inp:
        ok, l = rule_zero.validate(line, rulemap)
        print(ok, l, line)
        if ok and (l == len(line)):
            total += 1

    return total

def part2(rules, inp):
    rulemap = {r.n: r for r in rules}
    rulemap[8] = RefRule(8, [[42, 8], [42]])
    rulemap[11] = RefRule(11, [[42, 11, 31], [42, 31]])
    rule_zero = rulemap[0]

    r = "^" + rule_zero.as_re(rulemap) + "$"

    print(r)

    total = 0

    for line in inp:
        if regex.fullmatch(r, line):
            total += 1

    return total

ex_rules_o = """
0: 4 1 5
1: 2 3 | 3 2
2: 4 4 | 5 5
3: 4 5 | 5 4
4: "a"
5: "b"
""".strip().splitlines()

ex_inp = """
ababbb
bababa
abbbab
aaabbb
aaaabbb
""".strip().splitlines()

ex_rules = [parse_rule(r) for r in ex_rules_o]

rules_o = """
16: 95 7 | 53 12
41: 12 13 | 7 107
12: "a"
56: 17 12 | 129 7
102: 12 5 | 7 53
30: 105 7 | 26 12
66: 7 5 | 12 119
14: 27 7 | 109 12
62: 95 7 | 43 12
21: 12 12
23: 12 112 | 7 38
108: 7 43 | 12 21
80: 7 21 | 12 91
72: 7 41 | 12 89
117: 35 12 | 37 7
83: 7 91 | 12 5
13: 94 12 | 95 7
18: 7 62 | 12 87
24: 21 12 | 19 7
35: 7 81 | 12 113
8: 42
20: 12 27 | 7 1
120: 12 29 | 7 97
110: 107 7 | 102 12
7: "b"
32: 7 92 | 12 83
116: 12 40 | 7 98
86: 65 94
75: 12 118 | 7 119
46: 7 103 | 12 80
49: 109 7 | 57 12
95: 12 12 | 7 7
128: 7 19 | 12 5
19: 12 65 | 7 7
94: 7 12 | 12 7
99: 38 12 | 21 7
130: 7 6 | 12 116
76: 7 118 | 12 94
85: 7 67 | 12 126
104: 12 19 | 7 38
22: 44 7 | 24 12
79: 66 7 | 24 12
114: 70 7 | 115 12
27: 5 12 | 118 7
4: 7 91 | 12 21
105: 106 7 | 58 12
70: 18 7 | 2 12
33: 7 112 | 12 38
71: 53 12 | 93 7
87: 53 7 | 119 12
28: 7 64 | 12 16
63: 7 13 | 12 33
9: 57 7 | 36 12
34: 7 74 | 12 59
60: 7 108 | 12 86
67: 123 12 | 72 7
37: 52 12 | 71 7
112: 7 12
44: 12 5 | 7 118
26: 121 7 | 63 12
50: 127 12 | 48 7
15: 93 12 | 119 7
68: 112 12
78: 7 77 | 12 36
59: 49 12 | 22 7
109: 5 12 | 95 7
17: 38 12 | 119 7
54: 7 68 | 12 25
92: 119 12 | 94 7
123: 78 7 | 20 12
65: 7 | 12
129: 21 7 | 21 12
90: 12 112 | 7 95
98: 7 93 | 12 118
47: 12 93 | 7 21
2: 47 12 | 103 7
115: 125 7 | 56 12
25: 43 7 | 38 12
121: 7 23 | 12 99
36: 12 95 | 7 91
1: 7 118 | 12 91
113: 53 12 | 119 7
42: 12 85 | 7 50
6: 90 12 | 88 7
111: 5 12 | 5 7
69: 12 117 | 7 55
5: 12 7
106: 12 101 | 7 75
118: 7 65 | 12 7
77: 7 112 | 12 43
101: 53 7 | 38 12
31: 7 84 | 12 45
107: 53 7 | 118 12
119: 12 7 | 12 12
97: 119 7 | 112 12
57: 12 119 | 7 38
96: 7 98 | 12 4
100: 96 7 | 120 12
84: 12 114 | 7 30
64: 112 12 | 94 7
0: 8 11
52: 43 12 | 118 7
74: 12 28 | 7 79
58: 12 10 | 7 15
122: 12 104 | 7 29
127: 130 12 | 100 7
103: 21 7
81: 7 118 | 12 93
51: 122 12 | 9 7
10: 118 7 | 119 12
53: 12 7 | 7 7
89: 12 128 | 7 80
82: 12 32 | 7 60
124: 111 12 | 108 7
73: 19 7 | 5 12
3: 7 98 | 12 102
29: 38 12 | 5 7
126: 12 39 | 7 51
43: 7 12 | 7 7
125: 73 7 | 76 12
93: 65 65
11: 42 31
45: 12 69 | 7 34
39: 54 12 | 46 7
91: 65 12 | 12 7
61: 7 124 | 12 3
88: 91 7 | 19 12
38: 7 12 | 12 12
48: 61 12 | 82 7
55: 110 12 | 14 7
40: 112 12 | 43 7
""".strip().splitlines()

inp = """
abbbabaabbabaaabbbaabbbabaaabbabbabbbbbb
bbbbbabbababaabbbbaababbbbbaaabbaabaaaabaaabbbbabaabbbbbaabbabaa
bababbbababbabbbabbbabaa
abbabaaaaababbaaabaabbab
baababaaabbabbbbaaaabbbababaababaabbbabaaaabbbbb
abaababbabbaaaaaabbbabababaaaaab
aababbaaaababaaaaaabbbaa
bbbbababaaaababaababaaaa
babaaabaabaabaabaabbbbbb
bbbaaabbbababbabbbbbaaab
ababababaaaaaabbabaaabbb
aabbababbabaabbaabaababbbaabaabbbabbababaaabaababbbbaabbbaaaaabb
babbabbaabbabaaaabbabbbaaaabbbab
aabbababbbaaabbbbabbaabb
abbabbbaabaabaabaabbbbba
babaababbaabbbabababaabaaaabbaaababbabbaabbaaabbbbaaabba
baabbababbbabbaaaabbaaaabbbbaaaa
baabbabbbbaaabaaabababaabbabaaabaababbabbaaabaab
bbaaababaabbabbaababbbab
abbaaaaabbabbabaaabbabaa
baaaaabaaabaabbbabaababa
aaaaaaaaabaabaabbbaaabbbbabbabbbababbaabbbbaabaabbaaaabbaaababbbbbabaaba
bbbaaabaaabbbaaabbbabbaaaaaaaabbbbbbabbb
abaaabbbbbaaaaaabbbaabaa
abababbaababaababbbabbab
baaaaababbbbbbbbabaaabbb
aabbaabaaabbaababbbabaab
bbababababbbbbaaabbaaabbbbbbaaaa
aaaaaaaaabaaabaababbbababaaababbbbbaabaa
aabbbabbbbaabbbaabaabaaabbaababbaabbabaababbbabb
aaaabaababbaaabbbabbbabb
babbababbbbaabbaaabaabbbbabbbbabbaaabaabbabaaaab
babbaaaaababbbaababbaabb
abbbbaabbbbbbbbababbaaaaabbaabbbbbbabaaa
abaabaaaaaaabaabaaaabbbb
bababbbbaaababbbabbababb
ababbababbaababababbbbabaabbbaaaababbbbaaaabaaba
babaabaabbabaaabbbababab
babbabbabbaaaababbabbbbb
bbababaabababbbbbabbbabb
abaaaaabbabaabababaaaabaabaabbaabaaaababaababbaabababbbabaaaabbbabaaababaabbbaab
babaabbabbbabbaabbaaabba
abbabababababaaabbbaaababaababbbbbabbbaaabaaababaababaab
aaabaabbabbaaabbababbaab
baaaababaabbaaabbaabbbab
baabbababaabaaaaababbbaabbaaababbbababaaabbbbabb
bbababbabaabaabbbbaabababababbaaabbaaaaaaabbbbbb
bbbaaababaabaabbaaabbbba
bbabbaabbbababbabaaabbba
abaabbbbaabbabbabbabaaabaababaab
bbaabbbabbbbbabbabaababbaaabbbaa
abaabbaaaabbabababbbbbaaaabaaabbabaabbabbbaaaaab
babaabaabbbaabbabbabbaabbaabababbaaabaaa
bbababbbbbbabbbaaaaaababaabababbbbaaaaaa
aaaabbbbabbabbaaabbaaaba
aabbababbbbabbaaabababaabbabbbbabbbbaaba
abbbbaaabbbaaabaabaaabab
babaaaaabaabbaabbbbbbaababbaaaab
aaabaabbbabbababbaabbabbbbbababbabbababb
aaaabaaaaabbabababababbb
abbabaaabababbaaaaaaabaa
aabaaabbbabbabbaabbbbaabbabaabbbababaaaa
bbabbabbabaababbbababbbbaabbabababaaaabaababaaaaabbbaaababaaaaaa
ababaabbbababbabbababbabbaaabbbb
abaabbbababbbaabbababaaaabbbababbabbaaabaaababaa
bbbbbaaaababaababaaaaaaa
babbbaababbabaaabbaabbbababbbbaabbaabaaa
babbabbaabbbbabaaaababba
ababaabababbaaabbabaaaab
abaabbaabbbbbaaaabbabbaa
bababbbaabbabbbbaaaaabaa
abbabbbabbbaaabbaabaaabbbbbbbbbbaaaaabbaabaaabba
bbbaaaaabaabbbabaaaabbbbbbbaabab
bbaabbbaabbababaaabaabaa
aabbbabbbbbbababaabaabbbaaabaaaa
baabbababbbabbaabbaabbbb
abaaaababaaaababaaabaaaa
bbabbbbabaabaaaabaaababb
baabbbaaabababaabababbbaababaababbabbbbb
abbbababbaabbabbbabaabbb
abbabababababbbbaabbabbaabbaaaba
bbabbaabbbabbbbabbaaabba
babaaababaaaababaaabbbbb
baabababaaaaababaababbba
baabbbaabaaaabbabaaaaabbabababaaaababbbbaaabbaababaaaaaabababbbbbbbbabbaaabaaaba
baabababbabbabaabbababbaaaabbababbaabaaa
abaaaabbbabbaaabababbbab
baaaaababababbbababbbbbb
babbbbaabababbabaaababba
ababaabbbabbabbaababbabb
aabbaabbbbbbbabbbabbbbabbbbaabbaabbababb
bbbaaaaabaababbbabbabaabbbabbbaabbbaabbabaaabaabaaaabbbb
bbbaabbaaaaaaabbabbbabbbabbbabbaaaabbbbb
aabaaaabbabaabbaaabaaaaaabbbabababbbbabb
babbabaabababaaabbbbbbbbbaabbabbbbabbbaaaaaabbaa
babbabaababaabababbbbabb
aabbababbbbbbbbabaabbbababbabaabbabbbbba
abbbbaaabaababbbaabbabaa
baabbbabbbbbbabbababbbba
bbababaababbbaabbbbbabaa
aababbaaaababbabbbaabaab
abbbbaabbaaaabbaabaababbbaaaaabb
babbbababbbaababaaabaabbbabbabbababbabaa
abababbaabababaaaaaabbbb
bbaababaaaabaabbbbabbbab
bbbbababbbbbabbabbbaaababaaaaabb
babbbaaabaaaaabababbbaababbbbaababbbbaabbbbbaaaabbaaaabbabbbbabb
abababbabbbaaaaababbaaabbbaaabbbaabbbbaa
ababbababbabbbaaabbaaaba
bbaabbaaababaaabaababbaababbbbabbbbbaaaaabbbabba
aaaabbbababbabbbbbaabbaabaabbaabbbabaaba
abaabbaaabababbaabbbabaaababaaaa
aaabaabbaabaabbbaaabbbaabbaabaaabbbaaabbbbaaaabb
bbabbabbabbbbaabababbbbb
babaaabaaaaabaabbabababa
abbabaabbbabbababaabbbbb
bbbaabbaabbbbaabaabbbaaabababbaabbbabbaaaababbbb
aababbabaabaabbabbabbbbabaabbbbb
aaaabaaabbbaaabaaaabaaaa
babbbaaababaabbbbabaaaab
abbbabbbbabababbbbbbababababaaabbaaaaaabbbbbbaabbbabaabb
ababbabaaababbaababaababaabbaaba
babaabaaabaabaabaabbabbb
babbbbaaabbaababbaabbaabbbbbbbbbbabbaabababaaaaabbbabaaabbaabaab
aabaaaabaaaabbbbaabaaabbbaabaaabababbbbbbbbaaabbbbabbaabbabbbaba
aabaaaabbbaabababbaabbaaabaaabbbbaaabbab
bbabbabaabbababaabaababa
abaaabaaabaaaaabbaaaaaaabbbabaabbbbbaaba
bbbbababababbababbaabababaababbbaababaaabbabaabbbbaabaaabbaabbbbbbabbbbb
baaabbaabbbabbabaabababaabaababaaaabbabb
babbbbaabbbabbbaaaabbaaabbbaaaab
abbbbabaabbabbbabbbaabbb
aaaababababbabbbabbaabbbbabaaaabbaaabbababaaabbaaababbbb
abbbbbabaababaaaaaabababbaaabaab
aabababaaaababaabaaabbaaababbaaa
aabbbaabbabaababbbabbabbbbbbbaaabbbbbbbaabaaabbb
abaabbbabbabbbbaaaaaabaa
bbabababbbaabaaaaaababababbbbbbaabbbaaabbbabbaabbaababab
aaaabbbabaabbabbabaaabbb
baabaaaaaabaabbabbbaabbbbaaaaaaaabaababa
aaaabaababbbbabababbaaaaaabababa
bbbbabaabababbaaaaaaababbaaabaaaaaaabbab
bbbaaababaaaababbabbbbabbbaabaab
aabbbabbabbaaabbbbabaaaabbbbaaab
abaaabbbaaabaaaabaaababbbbbaaabaabbbbbbbaaaaaabbbabaabbaabababaa
aaaabaaababbabbbabbababaabbbbbbbaaabaaaaaabbbbab
abbbbababbbbabaababaabaabbaaaaaa
aabaaabbaaaaabababbaaaba
baaaabbbbaabbbabbabaabbabbbbaaaa
baabbbabbaabbbaababbaaaabbbabbaaabbaaabaaaabaaba
bbbaaaabbabaababbbaabbbbaabaabbababaaabbbabbabbaabbabaabbbabaaab
aabbaaaabababbbabbbbaaba
abaabbbaabbbabbbabaaaabaabbaaabaababbabb
aaaaaabbababababaaaabaaaaaabbbbb
aabbaaaaaaaababaaaaabaaabaababaaaababaab
baabbbaabbbaaabbaaabbaab
aaaaaaababbaaaaabbababbbaaaaabbaaaaababb
aaaabaababaabaaaaabbbaaaabababbaaaaabaabbbbabaaa
abbbbbababaabbbabababbaabababbbabbbbaabaabaabbab
bbaaabbbababbabababbaaabaaaabbaaaaaababb
aaaaaaaabbabaaababbabbbaabbaaaaaaaabbbaabbbbabbb
babbabbaaabaaaaaabbbbaaabbabbbbbaabababa
baabbbabaababbaaaaabbabb
bbabaaabaaaaaaabbbabbbbaaababaab
aaaaaaaababbaaaabbaaabba
aabbabbabbbaaaaabbbaabbaaaaaabaaaaabbbab
babaabaaabaabbaaabbbbaaabbbaaabaabbabaaaaabbabaabbbababa
bbabbbbaaabaaaaaaaaabababbbbbbbbbbbaaabbaababbbaabbbaaaaabbbabba
baababbbbabbabbabababbabbbbbbbabbabaabbb
ababbaabbababbbaaabbaaabaabbaaababbabbab
aabaabbbaabaaabbabbbbbabaaabbbbb
aababaaababbaaabbaaabbaa
aaabbaaabbbaaabbababaaaa
bbbabbaabaabbabbaabaabbbaababbabbbabbbab
aababbabaaabbaaabbaaaaba
aabbbaaabbbbbbbabaaaabbbbaabaaabaaabbbbb
bbbaabbaabbbabbbbabbabbbabbaaaaababaabbb
abbaababbabbbaabbababbbaaaaaaabbababbaaa
aababbaaabbbbaaabababaabababbaabbaabbbbb
babbabbabbabbbaaabbbababbbaabbbaaababbaaaababbbaaaababaa
babbbbabbabababbbbbaabbabaabbababababbbabbbbababaaabababaabaabab
bbbbbaababbbbabbbaabbaaaaabbabaaabbababb
abaaaabaaabbabbaaaabbabb
bbaabbaabbbabbaaaaaaaaaabbbbaaba
abbbbabbaaabaaaaabbbbabaaabbbababbaaaaaabbaaaaaabbaaabba
bbbbbbbabababaabbbbaaabaabbbaaabbaabaaba
bababaaababbbbababaaabbb
babbabbbbabaaabbaabbabbababbbaabaaabbbabbabaaaaa
ababaababaabaaaaaabbbaabbabbaaba
bbabbabbabaabbbbabbaaabbaaaabbaaabababbb
abaaaabababbabaabbaaabbbaabaaabbbbabbaabbbbbbaba
bbbbaaababaaabaabbbbaaba
aaaaaabbaaaabaaaaaababab
bbabbababbababbbaabbbbab
bababbbbbaabbbababaaaabbabbabbaa
bbbaaaaabbaaabbbbabababa
abaabbbaabbbbaaabbbaaaaababbbabbaaabaaaa
ababaabaaabbababbaabbaab
bbbbaaabbaaaaaabbbaaaaaa
bbbaaabbbbaaabaaaabbbaabbbbaaaab
baabbabbbababaaabababbabaabaaabbaaaababbbbabbbbbbbbaabbb
abbabaabababbabaabaabbaa
aaabaabbbaaaaabababaaaba
bbaabbbaaaaabbbaaabaaababaabbbbaaaaababb
bababaaaabbbbaaabbaaaaab
abbabbbbbbaabbaaabbbaabb
babbabaaababababaabaabbabbbaabab
aaaaaaaaaaaabbbabbbabbab
abbabbbaabbabaababaaabbb
bbaabababaababaabbbbabbaaaababbb
abbaababbabaaababbbabbbaabbbbaababaaabbbabbbabbaabaaababbaaabbbbbabbbbba
abbbbbabbababbbbbbaabbab
aabaabbabaabaabbbbaaabba
abbabbbbabbbbbbbababbabb
abbbbaababaabaaaaaaaaaabbabbaaba
aaaaaaabbabaabaabaaaababbbabbababaaabbaa
aabaaaaaabaaaabababbbbbb
aaaabbbaaabbaaabaabaaababbabaabb
bbabbabababbbaabbbabaaba
abbbabbbaabaabbbabaababbbaaaabbaabaabaabbaaabababaaaaabbbbbaabaa
bbabaaabbbbabbaaaabaaaabaabbbbaa
abbbbbbbabbabbbbbbaabaaa
bbbbabaaaabbababababaaaa
babbbbaaaabaaabaabaabbaabbabaaaabbababaaaabbaabbaabbbaba
bbabbbaaabbbababaaabbaba
bbbbaabaaababababbaabaab
bbbabbbabbabbabbabaaaababaaabbab
baaaababbaaaabbbbbbbababaaabaabbaaaaabaa
baaaaababbbbbabbbbbababa
bbabaaaabbabbabababaaabbaaabaabbbaabbbba
bbbabbaaaabbabbabbbbaaaa
abaabbaabbaababbaaabbaaabbbbaaaa
babaabbaaaaaababbaabbabaaaaabaaabaabbaababbaaababaabbaaa
ababaaabbababbaababaabaaaaaaabaabaabbbba
babbbaabaababaaaaabaaabbbbabbbbb
babbaaaabababbbabbbaabbb
abaabbaabbaababaabbabbab
abaabaaabbabbabbbbaaabbbaabbbaaaaaaaabaa
aabbbabaababaabaaaabbabb
abaabaabbbbbbaaabbaababaaabaaaabbababbaaababbabb
abbaabaababaaababbaabbbb
abbbabaabbabaaabababbbbb
aababbbbaabaabbababbabaabaababaabbabaabb
bbabaaabababbaabbabaabaababbabbabbbbbabaabaaababbbbaaaab
aaaabbbabbbabbaaababbbaabbbabbab
abaabbbbbbaabbbbaabbaabbaabaabaaaaabaaabbabbaaaabaabbbbabbaabbab
babbabbbbababaabaaabbaaaaabbabaaabaaabbb
baabbabaaaaabaaabbbaabaa
bababbbbbbbbababbbabbaaa
aabbbaaabbbaabbaaabbbbba
aababbabaaaaabababaaabbb
babbbbabbaaaaabaababbaaa
bababbaababbabbaaaabaabbbbabbbaaaabbbbbaabbaabbabaababba
baabbabbabbaabaababbababbbababbbbabbabbaaababbbaaababbbb
bbbbabaabbabbabbababaaababbbbbaaaabbbaabbbbbbbaa
aabbababbbbbbaabaabbabaababbaabababaaaabbaaaaaab
aabaaabbbababbabbabaabbb
bababbbaabababaabbabbbab
abbabaaaaaabaaaabaaaabaabaaabbbb
abababbabaaaaabaaaabbaab
aaaabbbababaaabaaabaabbaaabbababaaaaabaa
babbbbaaabbabbbbababbbaababaababbbbaaababbabbaaaababbbbbaaababab
baabababbaababbbaabbbabbbbabaabb
aabbabababbaaabbbabbbbabbabaabababbaaaaaaaababbb
aabaaabababaabbabaabbaab
abbbbaababbbababaaabbaba
babaabbaabbaaabbbaaababa
ababbaabbbaabbbaabbbbbbb
bbbbbabbbabbbaaabbaababbabbbaabbbaabbaaa
bbaabbaaaabbabbabbabbaabbbaaabaabbbaabbbbbaaaabbabbbbabb
aabbaabbabbabbbbaaaaabababbbbabbbbbabbab
aabbbaabbbbaaabbbaaaababaaaabbbaaabbbbab
ababbaabbabbbabaaabaababbbbbbaab
bbbbbbbaaabbabbabaabaaba
aabaaabaabbbababbabbaaaabbaabaabaaaabbaa
bbbbbbaaaaabaaabaabbbaabbabbabbabbaabbabaababbba
abaabbbaabaabaaabbaaabaabababbaaabaaabab
abbabaaaaabaaaababbbbaaabbbaaaaaabbbabaabbbaabaa
abaabbbabaaaabbbabbbbaaabbbaaaab
aabaababbaabaaaabbababbbbbabbbbbbbbbabbbabbbabbbaaaaabababbaabbb
aababbaababbaaabaaabaaab
aabbaaababaababbabbbababbaaaaabaaaaaabbababaaaab
abbbabaabbbabbaabbbbbbbbabaabbbbabbbabbbabbbbaaaaabbbbbabaaaaaabbaaabbbabbbbaaba
ababbabaabbaababbaaaabbabaaababaabbaabbabaaababaabbbbbba
baabaabbbbbbbbbbaabababbbaaabbaaaaababaabbabaaab
babbbaababbbbbaaaabaabbbbaabbabbbbbaaabababaabaaaabbabaa
abaabaaaaaababbabbaaabbbbababbabbababababbbaabbaaaababbabaaaabbaaaaabbabaabbaabbbbaabbabbbaabbbb
abababaabababbbbabaaaababbababaaabbbbbbaabbbaaaa
babbbaabaaabaabbbabaabbb
abbabaaaaabbaaabbbaaabbbbbbbaaab
aabbbaababaaaabbaaaababbabaababaabbbbbababaabbbabbbaabaa
aaaabaaaabaabaaaaaabaaab
aaabbaaaaabaaaaabbaaaaaa
bababaaabbbaaaaaabaabbbbaabaaaababbbbabbaabbabbb
abaabbaaabbbbbabbbaaababbbabbbabaaaaaaba
aabaaabbbaabbbabbaaababb
abbabaaabbbaaabbbabbbabb
aaaabababbababbaaababbaabbbabbbb
baaaaababbbbbbbabbbaabbb
baaaaabaabbabaaabbabaaabbabaabaa
abaaaabaabbabaaaabbbaabb
abaabbaabaaaabbababaaabaaaaabbab
babbbaaaabababbaaabbbaababababbb
abbabbbaabbbbababaabaabbbbaaababbbbaababbaaabbaa
aabaabbbaabbaaababaabbababbbabbbbbbbbabbbbbaababaaaaabababbbbabbbbabbbabbaaabaaabaaababa
babbabaabaabbabbbbaabbbabbbbbbab
abbbbaababaaaababababbbbbabbabbbaaabbaaabbbabaab
bbbaaaaaabbabaabababbbaaaaabaabbbaaaaabb
bbbabbaabababbabaabaabbabbaaaaab
abbbabaabbbaaababbaabbab
babbaaababbbbbabbbbabbab
bbaabbbabbbbbbbabbababaabbbaaabbabbaaabaababbbbb
bbbbbbabaabaaaabaaabbbba
babbaaababaaaabbaababbabbbaababbbbaabbbbbabbaaba
aaaababaaaaabaaabbaabbaababaaabaaabbaaaaaabbbaaaaaaaabbbbbbababaabaaabbb
abbaababaabbaaaabababaaababbabbaaabaaaabaaababbaaabbbbba
abababbaaabbaaaaabaabaabbbbbabbaaaababba
bbbbbbbaabababbaaaabaaaa
babbbabbbaababbaaababbbaaababbbbbabaaaabaaaaaabaaabaaabbabababbbbbbaaabbaababaaababbaababbbbbaaa
aaabaabbbbababbbaaaaaabbaaabbbaabbbaabab
abbaaaaaaabababaaaababab
bbabbbaaaaaaaaaabaaaabbbbaaaababbbbbbaab
bbabbbbaabbbbaaabbababaabbbbababbbabaaabaaaaabbbabaaababbbbabbbb
bbababbabbbabbbabbbababb
aaaaaaabbabbbbaaababbbab
baababaabababbbaababbbaaabaababa
ababbaabaaaaababababaabaabbbbaabbabbbbabaaabbababaaaaabbabbbaaabababbbba
bbbaabbabababbabbaabbbba
aabaabbaaaaabaaaaabaaaaaaabbbaababbababaabaaaaab
abbbabaabaabababbbababab
babaababbabbbbababbbbaaabababbabbbbbabaaaaabaababbbbabbb
abaabaaaaababbaaaaaababb
abbabaabaaabaabbbbababab
aaaabaabbaabbbaaaabbabbaaaabbabb
bababbbbabaababbaabbbbbb
babbaaaabbababbbaababbbb
bbbbbbbbabaabaabbbaaaaba
babaabbabababbbbaaabbaab
aabbabbaababbbaabbaaaabb
babbaaababbbbbaabbbabbbababaaaab
babbbbabbababbabbbaabbab
bbbaaaaabababaaababbbbba
abbababaabbaaabbaababbba
baaaababaabaaabaabbaabaabbabaabb
babbaaabbababaaababaabababababbababbbbaabbaabaaaabbbaabb
babaaabbaabaaabbaabbbabbabbbbbba
aabbabbabaabaaaabbbaabab
bababaaaaabbbaaaabbbabaabbbbbbabbaaabbab
abbaabaaaabbaaabbabbbbbaabbabbbabaabbaba
abbbbaabbaabaabbbaaaabbaaaabababbaaabbaaaaababbabaaababb
abbbbaabaaaaaaaaabababaababaaabbabaaabababbabbaa
aaaabaaaabbbbaaaabaabbab
baababbbbbbabbbabbbbaaaa
bbaabbbabaaaababbababbabaaabbaaaabaaabba
aababaaababaabaaaabaabbbbabbbbbb
bbabbbbabbabaaaaabaabbbabababbaaabaaaaababbaaaab
babbaaaaaabaabbabbbbbabbaaaaaaaabbababababaababa
bbbabbbaabbbbaababbaaabbababbaabaabbababbbabbabaaabbaabababaaaab
abbaababbbbaaabbbabbbbba
ababaaabbbabbaabbabaaabbaaabbbba
bababbabaabbaaaaababaabbbabbabbbbbabbbaaaabababababbbabaaaabbbbaababbaaa
aababaaababababbabaaabba
bbaababbabbabaababbbbaababbabaaaabaaaabbaaabbabbabbbaabaaabababbaabbbbbb
abbbabbbaabbaababbababbbbaabbabbbababaaaabababaababbaaaabaabbaaabbabbbbaababbbbb
""".strip().splitlines()

rules = [parse_rule(r) for r in rules_o]
