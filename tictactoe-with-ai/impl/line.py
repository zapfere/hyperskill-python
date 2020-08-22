from typing import List

from .general import EMPTY, O, X, V_LINE, LineStatistics


class Line:

    def __init__(self, fields: List[str]):

        self._fields = fields
        self._stats = None

    def get_stats(self) -> LineStatistics:

        if self._stats is None:
            self._stats = _count_on_line(self._fields)

        return self._stats

    def get_field(self, index: int) -> str:

        return self._fields[index]

    def is_occupied(self, coord: int) -> bool:

        return self._fields[coord] != EMPTY

    def print(self):

        _print_line(self._fields)

    def __iter__(self):

        return iter(self._fields)


def _print_line(line: List[str]):
    """Prints array list of globally set size"""

    print(V_LINE, "", end="")
    print(end="", *line)
    print("", V_LINE)


def _count_on_line(line: List[str]) -> LineStatistics:
    """Iterates given line and counts players' moves"""

    xs = 0
    os = 0
    has_empty = False

    for pos in line:
        if pos == X:
            xs += 1
        elif pos == O:
            os += 1
        elif not has_empty:
            has_empty = True

    return LineStatistics(xs, os, has_empty)
