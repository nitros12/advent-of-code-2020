from functools import wraps
from typing import Optional, Tuple, TypeVar, Callable, Coroutine, List, Any

NoneType = type(None)

class StringView:
    def __init__(self, s: str, idx: int = 0):
        self.s = s
        self.idx = idx
        self.end = len(s)

    def at_end(self):
        return self.idx == self.end

    def peek(self) -> Optional[str]:
        if self.at_end():
            return None
        return self.s[self.idx]

    def next(self) -> 'ParserResult[str]':
        if self.at_end():
            return (False, self, None)
        r = self.s[self.idx]
        sv = StringView(self.s, self.idx + 1)
        return (True, sv, r)


T = TypeVar('T')
ParserResult = Tuple[bool, StringView, Optional[T]]
ParserFunction = Callable[[StringView], ParserResult[T]]


def parser_generator(gen_fn: Callable[[], Coroutine[ParserResult[T], StringView, T]]) -> ParserFunction[T]:
    def inner(view: StringView) -> ParserResult[T]:
        orig_view = view
        it, val = gen_fn(), None

        try:
            while True:
                p = it.send(val)
                success, view, val = p(view)
                if not success:
                    return (False, orig_view, None)
        except StopIteration as e:
            return (True, view, e.value)
    return lambda: inner


def consume_whitespace() -> ParserFunction[NoneType]:
    def inner(view: StringView) -> ParserResult[NoneType]:
        orig_view = view
        while True:
            (success, next_view, char) = view.next()
            if not success:
                return (False, orig_view, None)
            if not char.isspace():
                return (True, view, None)
            view = next_view
    return inner


def consume_string(to_consume: str) -> ParserFunction[str]:
    def inner(view: StringView) -> ParserResult[str]:
        orig_view = view
        for wanted_char in to_consume:
            (success, view, actual_char) = view.next()
            if not success or wanted_char != actual_char:
                return (False, orig_view, None)
        return (True, view, to_consume)
    return inner


def read_integer() -> ParserFunction[int]:
    def inner(view: StringView) -> ParserResult[int]:
        so_far = []
        orig_view = view
        while True:
            (success, next_view, char) = view.next()
            if not success and not so_far:
                return (False, orig_view, None)
            if char is None or not char.isnumeric():
                if so_far:
                    return (True, view, int(''.join(so_far)))
                return (False, view, None)
            view = next_view
            so_far.append(char)
    return inner


def consume_any_string(*to_consume: str) -> ParserFunction[str]:
    return try_parsers(*map(consume_string, to_consume))


def try_parsers(*parsers: ParserFunction[T]) -> ParserFunction[T]:
    def inner(view: StringView) -> ParserResult[T]:
        orig_view = view
        for p in parsers:
            (success, view, val) = p(orig_view)
            if success:
                return (True, view, val)
        return (False, orig_view, None)
    return inner


def kleene(p: ParserFunction[T]) -> ParserFunction[List[T]]:
    def inner(view: StringView) -> ParserResult[List[T]]:
        result = []
        while True:
            (success, next_view, val) = p(view)
            if not success:
                return (True, view, result)
            view = next_view
            result.append(val)
    return inner


def optional(p: ParserFunction[T]) -> ParserFunction[Optional[T]]:
    def inner(view: StringView) -> ParserResult[Optional[T]]:
        (success, next_view, val) = p(view)
        if not success:
            return (True, view, None)
        return (True, next_view, val)
    return inner


def take_until(taker: ParserFunction[T], untiller: ParserFunction[Any]) -> ParserFunction[List[T]]:
    def inner(view: StringView) -> ParserResult[List[T]]:
        result = []
        while True:
            (success, _, _) = untiller(view)
            if success:
                return (True, view, result)
            (success, next_view, val) = taker(view)
            if not success:
                return (False, view, None)
            view = next_view
            result.append(val)
    return inner


def char_fits_predicate(predicate: Callable[[str], bool]) -> ParserFunction[str]:
    def inner(view: StringView) -> ParserResult[str]:
        orig_view = view
        (success, view, char) = view.next()
        if not success or not predicate(char):
            return (False, orig_view, None)
        return (True, view, char)
    return inner


def is_char(char: str) -> ParserFunction[str]:
    return char_fits_predicate(lambda c: c == char)


def is_whitespace() -> ParserFunction[str]:
    return char_fits_predicate(lambda c: c.isspace())


def any_char() -> ParserFunction[str]:
    def inner(view: StringView) -> ParserResult[str]:
        return view.next()
    return inner

def run_parser(parser: ParserFunction[T], inp: str) -> Optional[T]:
    (success, _, val) = parser()(StringView(inp))
    if success:
        return val
    return None
