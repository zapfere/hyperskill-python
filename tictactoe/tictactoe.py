from field import Field
from general import o, x, size


# text labels
enter_cells = "Enter cells: "
enter_coords = "Enter the coordinates: "
errors = dict(
    occupied="This cell is occupied! Choose another one!",
    not_numbers="You should enter numbers!",
    not_in_range="Coordinates should be from 1 to 3!"
)
empty_field_str = "_" * size ** 2


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


def main():

    current_field = Field(empty_field_str)
    current_field.print()
    player_mark = x

    while current_field.moves_possible():
        current_field = make_move(current_field, player_mark)
        current_field.print()
        player_mark = switch_sides(player_mark)

    print(current_field.get_result())


if __name__ == '__main__':
    main()
