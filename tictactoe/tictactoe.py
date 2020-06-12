# text labels
enter_cells = "Enter cells: "
enter_coords = "Enter the coordinates: "
# constants
size = 3
x = "X"
o = "O"
_ = " "
h_line = "-" * (2 * size + 3)
v_line = "|"
empty_field_str = "_" * size ** 2
results = dict(
    in_progress="Game not finished",
    draw="Draw",
    x_wins="X wins",
    o_wins="O wins",
    fail="Impossible"
)
errors = dict(
    occupied="This cell is occupied! Choose another one!",
    not_numbers="You should enter numbers!",
    not_in_range="Coordinates should be from 1 to 3!"
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


class Line:

    def __init__(self, fields):
        self._fields = fields
        self._stats = None

    def get_stats(self):
        if self._stats is None:
            self._stats = count_on_line(self._fields)
        return self._stats

    def get_field(self, index):
        return self._fields[index]

    def is_occupied(self, coord):
        return self._fields[coord] != _

    def print(self):
        print_line(self._fields)


class LineStatistics:

    def __init__(self, x_count, o_count, has_empty_fields):
        self._x_count = x_count
        self._o_count = o_count
        self._has_empty_fields = has_empty_fields

    def get_xs(self):
        return self._x_count

    def get_os(self):
        return self._o_count

    def has_empties(self):
        return self._has_empty_fields


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


def print_field(field):
    """Prints internal state from 2D array"""

    print(h_line)

    for line in field:
        line.print()

    print(h_line)


def print_line(line):
    """Prints array list of globally set size"""

    print(v_line, "", end="")
    print(end="", *line)
    print("", v_line)


def parse_input(moves):
    """Parses string to 2D array - expected length is size * size"""

    field = []
    start = 0

    for i in range(size):
        line_data = parse_line(moves.replace("_", _), start)
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


def count_on_line(line):
    """Iterates given line and counts players' moves"""

    xs = 0
    os = 0
    has_empty = False

    for pos in line:
        if pos == x:
            xs += 1
        elif pos == o:
            os += 1
        elif not has_empty:
            has_empty = True

    return LineStatistics(xs, os, has_empty)


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


def make_move(old_field, current_player_mark):
    """Ask for new coords and make a move if possible, retry otherwise"""

    try:
        return try_move(old_field, current_player_mark)
    except ValueError:
        print(errors["not_numbers"])
    except IndexError:
        print(errors["not_in_range"])
    except AssertionError:
        print(errors["occupied"])
    # retry after displaying error message
    return make_move(old_field, current_player_mark)


def try_move(old_field, current_player_mark):
    """Ask for new coords and try to make a move"""

    coord_x, coord_y = [int(n) for n in input(enter_coords).split()]
    check_nums_in_range(coord_x, coord_y)
    coord_x, coord_y = transform_coords(coord_x, coord_y, old_field)

    return get_new_field(coord_x, coord_y, current_player_mark, old_field)


def transform_coords(coord_x, coord_y, old_field):
    """Converts from visible coordinates to array position"""

    new_x = coord_x - 1
    new_y = size - coord_y
    if old_field.is_occupied(new_x, new_y):
        raise AssertionError

    return new_x, new_y


def coords_invalid(message, current_player_mark, old_field):
    """Print error message and retry"""

    print(message)
    return make_move(old_field, current_player_mark)


def check_nums_in_range(coord_x, coord_y):
    """Check X and Y are between 1 and size (inclusively)"""

    x_in_range = 0 < coord_x <= size
    y_in_range = 0 < coord_y <= size

    if not (x_in_range and y_in_range):
        raise IndexError


def get_new_field(coord_x, coord_y, current_player_mark, old_field):
    """Returns a new field after making the move"""

    old_field_str = old_field.get_field_str()
    pos = coord_y * size + coord_x
    new_field_str = old_field_str[:pos] \
                    + current_player_mark \
                    + old_field_str[pos + 1:]

    return Field(new_field_str)


def switch_sides(current_player_mark):
    """Change player from X to O and vice versa"""

    if current_player_mark == x:
        return o
    return x


# main logic
current_field = Field(empty_field_str)
current_field.print()
player_mark = x

while current_field.moves_possible():
    current_field = make_move(current_field, player_mark)
    current_field.print()
    player_mark = switch_sides(player_mark)

print(current_field.get_result())
