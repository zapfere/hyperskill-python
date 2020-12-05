from abc import ABC
from enum import Enum
from typing import List

EMPTY_STR = ''
ANY_CHAR = '.'
STARTS_CHAR = '^'
ENDS_CHAR = '$'
ZERO_OR_ONE = '?'
ZERO_OR_MORE = '*'
ONE_OR_MORE = '+'
ESCAPE_CHAR = '\\'


class Matcher:
    def __init__(self, pattern: str):
        self.__filtered = pattern
        self.__start = False
        self.__end = False
        self.__result = None
        self.__prev_matched = False

        self.__check_is_possible()
        self.__process_bounds()
        self.__post_process_pattern()

    def match(self, src: str) -> bool:
        if self.__filtered == src:
            self.__result = True
        if self.__has_result():
            return self.__get_result()

        for pos, char in enumerate(src):
            self.__match_position(char, pos, src)
            if self.__has_result():
                return self.__get_result()

        return False

    def __match_position(self, char: str, pos: int, src: str):
        src_last_idx = len(src) - 1
        next_index = self.__index + 1
        if not self.__check_escape() \
                and self.__filtered_last >= next_index \
                and self.__filtered[next_index] in (
                ZERO_OR_ONE, ZERO_OR_MORE, ONE_OR_MORE):
            self.__match_repetition(next_index, pos, src)
        else:
            self.__match(char, pos == src_last_idx)

    def __check_escape(self) -> bool:
        return self.__get_pattern_char() == ESCAPE_CHAR \
               and (self.__index == 0
                    or self.__filtered[self.__index - 1] != ESCAPE_CHAR)

    def __match_repetition(self, next_index: int, pos: int, src: str) -> bool:
        if self.__check_escape():
            self.__index -= 1
            next_index -= 1
        tail_pattern = self.__filtered[next_index + 1:]
        if self.__end:
            if len(tail_pattern) == 0:
                # empty tail pattern for non-empty tail with tail match on
                return False
            tail_pattern += ENDS_CHAR
        checker = create_checker(self.__filtered[next_index],
                                 self.__get_pattern_char(),
                                 tail_pattern,
                                 src,
                                 pos)
        check_result = checker.check()
        while check_result == CheckResult.ONGOING:
            check_result = checker.check()
        self.__result = check_result == CheckResult.MATCHED

    def __get_pattern_char(self) -> str:
        return self.__filtered[self.__index]

    def __has_result(self) -> bool:
        return self.__result is not None

    def __get_result(self) -> bool:
        return self.__result

    def __check_is_possible(self):
        pattern = self.__filtered
        wrong_start_char = any(x not in (-1, 0)
                               for x in self.__find_unescaped(STARTS_CHAR))
        wrong_end_char = any(x not in (-1, len(pattern) - 1)
                             for x in self.__find_unescaped(ENDS_CHAR))
        if wrong_start_char or wrong_end_char \
                or pattern.startswith((ZERO_OR_ONE, ZERO_OR_MORE, ONE_OR_MORE)):
            self.__result = False

    def __find_unescaped(self, char: str) -> List[int]:
        result = list()
        pos = self.__add_unescaped_char(char, result, 0)
        if pos > -1:
            result.append(pos)
        last = len(self.__filtered) - 2
        while pos != -1 and pos < last:
            pos = self.__add_unescaped_char(char, result, pos + 1)
        return result

    def __add_unescaped_char(self, char: str,
                             result: List[int], start: int) -> int:
        pos = self.__filtered.find(char, start)
        if pos > 0 and self.__filtered[pos - 1] != ESCAPE_CHAR:
            result.append(pos)
        return pos

    def __process_bounds(self):
        if self.__filtered.startswith(STARTS_CHAR):
            self.__filtered = self.__filtered[1:]
            self.__start = True

        if self.__filtered.endswith(ENDS_CHAR) \
                and len(self.__filtered) > 1 \
                and self.__filtered[-2] != ESCAPE_CHAR:
            self.__filtered = self.__filtered[:-1]
            self.__end = True

    def __post_process_pattern(self):
        self.__index = 0
        self.__filtered_last = len(self.__filtered) - 1
        if self.__filtered_last == -1 and not (self.__start and self.__end):
            self.__result = True

    def __match(self, char: str, consumed: bool):
        if self.__check_finished():
            return
        if self.__check_escape():
            self.__index += 1

        pattern_char = self.__get_pattern_char()
        matched = pattern_char in (ANY_CHAR, char)

        self.__prev_matched = matched
        self.__check_bounds(consumed)
        if matched and not (self.__end and self.__pattern_consumed()):
            self.__index += 1
        else:
            self.__index = 0

    def __pattern_consumed(self) -> bool:
        return self.__index == self.__filtered_last

    def __check_finished(self) -> bool:
        return self.__index > self.__filtered_last

    def __check_bounds(self, src_consumed: bool):
        if self.__start and not self.__prev_matched:
            self.__result = False

        elif self.__pattern_consumed() and not self.__end:
            if src_consumed:
                self.__result = self.__prev_matched
            elif self.__prev_matched:
                self.__result = True

        elif self.__end and src_consumed:
            self.__result = self.__prev_matched


class CheckResult(Enum):
    ONGOING = 0
    MATCHED = 1
    FAILED = 2


class RepeatingChecker(ABC):
    def __init__(self, tail_pattern: str, char: str, src: str, pos: int):
        self._tail_matcher = Matcher(STARTS_CHAR + tail_pattern)
        self._char = char
        self._src = src
        self._pos = pos
        self._iteration = 0

    def check(self) -> CheckResult:
        if self._cant_continue():
            return CheckResult.FAILED
        current_pos = self._pos + self._iteration
        tail_matched = self._tail_matcher.match(self._src[current_pos:])
        if self._iteration == 0:
            self._iteration += 1
            return CheckResult.MATCHED if tail_matched else CheckResult.ONGOING
        pos_matched = self._pos_matched(current_pos - 1)
        self._iteration += 1
        if pos_matched and tail_matched:
            return CheckResult.MATCHED
        if pos_matched and not tail_matched:
            return CheckResult.ONGOING
        return CheckResult.FAILED

    def _pos_matched(self, current_pos: int) -> bool:
        return self._char in (ANY_CHAR, self._src[current_pos])

    def _cant_continue(self) -> bool:
        return self._pos + self._iteration >= len(self._src)


class ZeroOrOne(RepeatingChecker):
    def _cant_continue(self) -> bool:
        return self._iteration > 1 or super()._cant_continue()


class ZeroOrMore(RepeatingChecker):
    pass


class OneOrMore(RepeatingChecker):
    def check(self) -> CheckResult:
        if self._iteration == 0:
            self._iteration += 1
            if self._pos_matched(self._pos):
                return CheckResult.ONGOING
            return CheckResult.FAILED
        return super().check()


def create_checker(checker_type: str, pattern_char: str,
                   tail_pattern: str, src: str, pos: int) -> RepeatingChecker:
    if checker_type == ZERO_OR_ONE:
        return ZeroOrOne(tail_pattern, pattern_char, src, pos)
    if checker_type == ZERO_OR_MORE:
        return ZeroOrMore(tail_pattern, pattern_char, src, pos)
    if checker_type == ONE_OR_MORE:
        return OneOrMore(tail_pattern, pattern_char, src, pos)
    raise AttributeError(f'Unknown checker type: {checker_type}')


def main():
    pattern, string = input().split('|')
    result = Matcher(pattern).match(string)
    print(result)


if __name__ == '__main__':
    main()
