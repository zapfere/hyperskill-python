from general import empty, h_line, size
from line import Line


results = dict(
    in_progress="Game not finished",
    draw="Draw",
    x_wins="X wins",
    o_wins="O wins",
    fail="Impossible"
)


class Field:

    def __init__(self, field_str):
        self._field_str = field_str
        self._h_lines = None
        self._v_lines = None
        self._diagonals = None
        self._result = None

    def get_field_str(self):
        return self._field_str

    def get_h_lines(self):
        if self._h_lines is None:
            self._h_lines = parse_input(self._field_str)
        return self._h_lines

    def get_v_lines(self):
        if self._v_lines is None:
            self._v_lines = transpose(self.get_h_lines())
        return self._v_lines

    def get_diagonals(self):
        if self._diagonals is None:
            self._diagonals = diagonals(self.get_h_lines())
        return self._diagonals

    def is_occupied(self, coord_x, coord_y):
        return self.get_h_lines()[coord_y].is_occupied(coord_x)

    def print(self):
        print_field(self.get_h_lines())

    def get_result(self):
        if self._result is None:
            self._result = check_results(self)
        return self._result

    def moves_possible(self):
        return self.get_result() == results["in_progress"]


class PartialResult:

    def __init__(self):
        self._x_wins = False
        self._o_wins = False
        self._has_empties = None
        self._unfair_moves = None

    def x_wins(self):
        return self._x_wins

    def o_wins(self):
        return self._o_wins

    def has_empties(self):
        return self._has_empties

    def has_unfair_moves(self):
        return self._unfair_moves

    def set_unfair_moves(self, unfair):
        self._unfair_moves = unfair

    def both_win(self):
        return self._x_wins and self._o_wins

    def merge(self, x_wins, o_wins, has_empties):
        self._x_wins = x_wins or self._x_wins
        self._o_wins = o_wins or self._o_wins
        self._has_empties = has_empties or self._has_empties


def parse_input(moves):
    """Parses string to 2D array - expected length is size * size"""

    field = []
    start = 0

    for i in range(size):
        line_data = parse_line(moves.replace("_", empty), start)
        field.append(Line(line_data))
        start += size

    return field


def parse_line(moves, start):
    """Parses string from given start position up to size characters"""

    return [moves[start + j] for j in range(size)]


def transpose(field):
    """Transposes given square matrix"""

    return [Line([line.get_field(i) for line in field]) for i in range(size)]


def diagonals(field):
    """Gets matrix's diagonals"""

    result = [[], []]
    for i in range(size):
        result[0].append(field[i].get_field(i))
        result[1].append(field[i].get_field(-i - 1))

    return [Line(line_data) for line_data in result]


def print_field(field):
    """Prints internal state from 2D array"""

    print(h_line)

    for line in field:
        line.print()

    print(h_line)


def check_results(field):
    """Iterate all lines and checks total results"""

    result = PartialResult()
    line_sets = [
        field.get_h_lines(),
        field.get_v_lines(),
        field.get_diagonals()
    ]

    for line_set in line_sets:
        if result.has_unfair_moves() is None:
            unfair = unfair_total_moves(line_set)
            if unfair:
                return results["fail"]
            result.set_unfair_moves(unfair)

        check_partial_result(line_set, result)
        if result.both_win():
            return results["fail"]

    return interpret_result(result)


def check_partial_result(lines, partial_result):
    """Check if win condition is matched for a subset of lines"""

    x_wins = partial_result.x_wins()
    o_wins = partial_result.o_wins()
    has_empties = partial_result.has_empties()

    for line in lines:
        stats = line.get_stats()
        if (not x_wins) and stats.get_xs() == size:
            x_wins = True
        if (not o_wins) and stats.get_os() == size:
            o_wins = True
        if (not has_empties) and stats.has_empties():
            has_empties = True

    partial_result.merge(x_wins, o_wins, has_empties)


def unfair_total_moves(lines):
    """Checks if one player's made too many moves"""

    sum_x = 0
    sum_o = 0

    for line_res in lines:
        stats = line_res.get_stats()
        sum_x += stats.get_xs()
        sum_o += stats.get_os()

    return abs(sum_x - sum_o) > 1


def interpret_result(result):
    """Get the game's result after iterating through all lines"""

    if result.x_wins():
        return results["x_wins"]
    elif result.o_wins():
        return results["o_wins"]
    elif result.has_empties():
        return results["in_progress"]
    else:
        return results["draw"]
