from general import empty, o, x, v_line


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
        return self._fields[coord] != empty

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


def print_line(line):
    """Prints array list of globally set size"""

    print(v_line, "", end="")
    print(end="", *line)
    print("", v_line)


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
