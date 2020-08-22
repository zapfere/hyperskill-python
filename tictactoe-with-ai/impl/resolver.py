from abc import ABC, abstractmethod
from typing import Callable

from .field import Field
from .general import O, SIZE, X, RatedPosition
from .move import get_new_field


class Resolver(ABC):

    def __init__(self, current_mark: str):

        self._current_mark = current_mark
        self._other_mark = _get_other_mark(current_mark)
        self._is_x = self._current_mark == X

    @abstractmethod
    def find_position(self, field: Field) -> RatedPosition:

        raise NotImplementedError


class NullResolver(Resolver):

    def find_position(self, field: Field) -> RatedPosition:

        return RatedPosition()


class SimpleResolver(Resolver):

    def find_position(self, field: Field) -> RatedPosition:

        result = _check_current_turn_win(field, self._current_mark, self._is_x)
        if result.position is not None:
            return result

        return _check_current_turn_win(field, self._other_mark, not self._is_x)


class MinimaxResolver(Resolver):

    def find_position(self, field: Field) -> RatedPosition:

        return self.__minimax(field, SIZE * SIZE, True)

    def __minimax(self,
                  field: Field,
                  depth: int,
                  my_turn: bool) -> RatedPosition:

        # check for terminal condition
        if depth == 0 or not field.moves_possible():
            return self.__choose_final_rating(field)

        # compute next turns' ratings
        start_rating = -1 if my_turn else 1
        return self.__choose_best_rating(field,
                                         start_rating,
                                         my_turn,
                                         _conditional_comparator(my_turn),
                                         depth)

    def __choose_final_rating(self, field: Field) -> RatedPosition:

        result = field.get_result(True)
        if result.x_wins:
            return RatedPosition(rating=1 if self._is_x else -1)
        if result.o_wins:
            return RatedPosition(rating=-1 if self._is_x else 1)
        return RatedPosition()

    def __choose_best_rating(self,
                             field: Field,
                             start_rating: int,
                             my_turn: bool,
                             comparator: Callable[[int, int], bool],
                             depth: int) -> RatedPosition:

        next_turn_mark = self._current_mark if my_turn else self._other_mark
        target_rating = -start_rating
        next_turn_depth = depth - 1
        not_my_turn = not my_turn
        result = RatedPosition(rating=start_rating)
        for position in field.get_empty_fields():
            next_field = get_new_field(position, next_turn_mark, field)
            next_rating = self.__minimax(next_field,
                                         next_turn_depth,
                                         not_my_turn).rating
            if comparator(next_rating, result.rating):
                result = RatedPosition(position, next_rating)
                if next_rating == target_rating:  # Alpha–beta pruning
                    return result

        return result


def _conditional_comparator(my_turn: bool) -> Callable[[int, int], bool]:
    """Return GT if my_turn else LT"""

    return lambda x, y: x > y if my_turn else x < y


def _get_other_mark(player_mark: str) -> str:
    """Get the mark opposite to given"""

    return X if player_mark == O else O


def _check_current_turn_win(field: Field,
                            player_mark: str,
                            is_x: bool) -> RatedPosition:
    """Check if given mark can win in this turn"""

    for position in field.get_empty_fields():
        new_field = get_new_field(position, player_mark, field)
        result = new_field.get_result(False)
        if (is_x and result.x_wins) or (not is_x and result.o_wins):
            return RatedPosition(position)

    return RatedPosition()
