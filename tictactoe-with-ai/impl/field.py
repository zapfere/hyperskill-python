from typing import List

from .general import EMPTY, H_LINE, SIZE, Position, PartialResult
from .line import Line

results = dict(
    in_progress="Game not finished",
    draw="Draw",
    x_wins="X wins",
    o_wins="O wins",
    fail="Impossible"
)


class Field:

    def __init__(self, field_str: str):

        self._field_str = field_str
        self._h_lines = None
        self._v_lines = None
        self._diagonals = None
        self._result = None

    def get_field_str(self) -> str:

        return self._field_str

    def get_h_lines(self) -> List[Line]:

        if self._h_lines is None:
            self._h_lines = _parse_input(self._field_str)

        return self._h_lines

    def get_v_lines(self) -> List[Line]:

        if self._v_lines is None:
            self._v_lines = _transpose(self.get_h_lines())

        return self._v_lines

    def get_diagonals(self) -> List[Line]:

        if self._diagonals is None:
            self._diagonals = _diagonals(self.get_h_lines())

        return self._diagonals

    def is_occupied(self, coord_x: int, coord_y: int) -> bool:

        return self.get_h_lines()[coord_y].is_occupied(coord_x)

    def print(self):

        _print_field(self.get_h_lines())

    def print_result(self):

        result = self.get_result(True)
        print(_interpret_result(result))

    def get_result(self, check_for_impossible: bool) -> PartialResult:

        if self._result is None:
            self._result = _check_results(self, check_for_impossible)

        return self._result

    def moves_possible(self) -> bool:

        result = self.get_result(True)
        return result.has_empties and not result.impossible \
            and not result.x_wins and not result.o_wins

    def get_empty_fields(self) -> List[Position]:

        result = []

        for y, line in enumerate(self.get_h_lines()):
            for x in range(SIZE):
                if not line.is_occupied(x):
                    result.append(Position(x, y))

        return result


def _parse_input(moves: str) -> List[Line]:
    """Parses string to 2D array - expected length is size * size"""

    h_lines = []
    start = 0

    for i in range(SIZE):
        line_data = __parse_line(moves.replace("_", EMPTY), start)
        h_lines.append(Line(line_data))
        start += SIZE

    return h_lines


def __parse_line(moves: str, start: int) -> List[str]:
    """Parses string from given start position up to size characters"""

    return [moves[start + j] for j in range(SIZE)]


def _transpose(h_lines: List[Line]) -> List[Line]:
    """Transposes given square matrix"""

    return [Line([line.get_field(i) for line in h_lines]) for i in range(SIZE)]


def _diagonals(h_lines: List[Line]) -> List[Line]:
    """Gets matrix's diagonals"""

    result = [[], []]
    for i in range(SIZE):
        result[0].append(h_lines[i].get_field(i))
        result[1].append(h_lines[i].get_field(-i - 1))

    return [Line(line_data) for line_data in result]


def _print_field(h_lines: List[Line]):
    """Prints internal state from 2D array"""

    print(H_LINE)

    for line in h_lines:
        line.print()

    print(H_LINE)


def _check_results(field: Field, check_for_possible: bool) -> PartialResult:
    """Iterate all lines and checks total results"""

    result = PartialResult(None, None, None)
    line_sets = [
        field.get_h_lines(),
        field.get_v_lines(),
        field.get_diagonals()
    ]

    if check_for_possible:
        unfair = __unfair_total_moves(field.get_h_lines())
        if unfair:
            result.impossible = True
            return result

    for line_set in line_sets:
        __check_partial_result(line_set, result)
        if check_for_possible and result.x_wins and result.o_wins:
            result.impossible = True
            return result

    return result


def _interpret_result(result: PartialResult) -> str:
    """Get the game's result after iterating through all lines"""

    if result.x_wins:
        return results["x_wins"]
    elif result.o_wins:
        return results["o_wins"]
    elif result.has_empties:
        return results["in_progress"]
    else:
        return results["draw"]


def __check_partial_result(lines: List[Line], partial_result: PartialResult):
    """Check if win condition is matched for a subset of lines"""

    x_wins = partial_result.x_wins
    o_wins = partial_result.o_wins
    has_empties = partial_result.has_empties

    for line in lines:
        stats = line.get_stats()
        if (not x_wins) and stats.x_count == SIZE:
            x_wins = True
        if (not o_wins) and stats.o_count == SIZE:
            o_wins = True
        if (not has_empties) and stats.has_empties:
            has_empties = True

    __merge_partial_result(partial_result, x_wins, o_wins, has_empties)


def __merge_partial_result(existing_result: PartialResult,
                           x_wins: bool,
                           o_wins: bool,
                           has_empties: bool):
    """Update existing partial result with new data"""

    existing_result.x_wins = x_wins or existing_result.x_wins
    existing_result.o_wins = o_wins or existing_result.o_wins
    existing_result.has_empties = has_empties or existing_result.has_empties


def __unfair_total_moves(lines: List[Line]) -> bool:
    """Checks if one player's made too many moves"""

    sum_x = 0
    sum_o = 0

    for line_res in lines:
        stats = line_res.get_stats()
        sum_x += stats.x_count
        sum_o += stats.o_count

    return abs(sum_x - sum_o) > 1
