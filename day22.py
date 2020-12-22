from typing import List, Optional, Tuple
from collections import deque
import copy


class Deck:
    def __init__(self, number: int, cards: List[int]) -> None:
        self.number = number
        self.cards = deque(cards)

    def hascards(self) -> bool:
        return bool(self.cards)

    def draw(self) -> int:
        return self.cards.popleft()

    def win(self, won_cards: List[int]):
        self.cards.extend(won_cards)

    def score(self) -> int:
        mult = len(self.cards)
        out = 0

        for c in self.cards:
            out += mult * c
            mult -= 1

        return out

def part1(players: List[Deck]):
    players = copy.deepcopy(players)
    players_map = {p.number: p for p in players}

    while True:
        cards_in_game = [(p.number, p.draw()) for p in players if p.hascards()]
        winner = max(cards_in_game, key=lambda e: e[1])

        winning_card = [b for a, b in cards_in_game if a == winner[0]]
        other_cards = [b for a, b in cards_in_game if a != winner[0]]

        players_map[winner[0]].win(winning_card + other_cards)

        if sum(p.hascards() for p in players) == 1:
            for p in players:
                if p.hascards():
                    return p.score()

def part2(players: List[Deck]) -> Tuple[int, int]:
    players = copy.deepcopy(players)
    players_map = {p.number: p for p in players}

    previous_rounds = set()

    while True:
        state = tuple(tuple(p.cards) for p in players)
        if state in previous_rounds:
            return 1, players_map[1].score()
        previous_rounds.add(state)

        cards_in_game = [(p.number, p.draw()) for p in players]
        previous_rounds.add(set(c) for _, c in cards_in_game)


        win_by_rec = True

        for pn, c in cards_in_game:
            if c > len(players_map[pn].cards):
                win_by_rec = False
                break

        if win_by_rec:
            new_players = [Deck(pn, list(players_map[pn].cards)[:c]) for pn, c in cards_in_game]
            winner, _ = part2(new_players)
        else:
            winner, _ = max(cards_in_game, key=lambda e: e[1])

        winning_card = [b for a, b in cards_in_game if a == winner]
        other_cards = [b for a, b in cards_in_game if a != winner]

        players_map[winner].win(winning_card + other_cards)

        if sum(p.hascards() for p in players) == 1:
            for p in players:
                if p.hascards():
                    return p.number, p.score()

def parse_deck(inp: str):
    first, *rest = inp.splitlines()
    number = int(first[len("Player "):].strip(": "))
    return Deck(number, [int(i) for i in rest])


inp_o = """
Player 1:
27
29
30
44
50
5
33
47
34
38
36
4
2
18
24
16
32
21
17
9
3
22
41
31
23

Player 2:
25
1
15
46
6
13
20
12
10
14
19
37
40
26
43
11
48
45
49
28
35
7
42
39
8
""".strip().split("\n\n")

inp = [parse_deck(x) for x in inp_o]


ex_inp_o = """
Player 1:
9
2
6
3
1

Player 2:
5
8
4
7
10
""".strip().split("\n\n")

ex_inp = [parse_deck(x) for x in ex_inp_o]
