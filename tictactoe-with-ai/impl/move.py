from .field import Field
from .general import SIZE, Position

ENTER_COORDINATES = "Enter the coordinates: "
ERRORS = dict(
    occupied="This cell is occupied! Choose another one!",
    not_numbers="You should enter numbers!",
    not_in_range="Coordinates should be from 1 to 3!"
)


def get_new_field(new_position: Position,
                  current_player_mark: str,
                  old_field: Field) -> Field:
    """Returns a new field after making the move to given coordinates"""

    old_field_str = old_field.get_field_str()
    pos = new_position.y * SIZE + new_position.x
    new_field_str = old_field_str[:pos] \
        + current_player_mark + old_field_str[pos + 1:]

    return Field(new_field_str)


def make_move(old_field: Field, current_player_mark: str) -> Field:
    """Ask for new coords and make a move if possible, retry otherwise"""

    try:
        return __try_move(old_field, current_player_mark)
    except (ValueError, TypeError):
        print(ERRORS["not_numbers"])
    except IndexError:
        print(ERRORS["not_in_range"])
    except AssertionError:
        print(ERRORS["occupied"])

    # retry after displaying error message
    return make_move(old_field, current_player_mark)


def __try_move(old_field: Field, current_player_mark: str) -> Field:
    """Ask for new coords and try to make a move"""

    position = Position(*[int(n) for n in input(ENTER_COORDINATES).split()])
    __check_nums_in_range(position)
    position = __transform_coords(position, old_field)

    return get_new_field(position, current_player_mark, old_field)


def __check_nums_in_range(position: Position):
    """Check X and Y are between 1 and size (inclusively)"""

    x_in_range = 0 < position.x <= SIZE
    y_in_range = 0 < position.y <= SIZE

    if not (x_in_range and y_in_range):
        raise IndexError


def __transform_coords(position: Position, old_field: Field) -> Position:
    """Converts from visible coordinates to array position"""

    new_x = position.x - 1
    new_y = SIZE - position.y
    if old_field.is_occupied(new_x, new_y):
        raise AssertionError

    return Position(new_x, new_y)
