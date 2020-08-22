from abc import ABC, abstractmethod
from random import choice, seed

from .field import Field
from .general import SIZE, Position
from .move import get_new_field, make_move
from .resolver import MinimaxResolver, NullResolver, Resolver, SimpleResolver

COMPUTER_MOVE_PREFIX = "Making move level"


class UnknownPlayerTypeError(Exception):
    pass


class Player(ABC):

    def __init__(self, player_mark: str):

        self._mark = player_mark

    @abstractmethod
    def make_move(self, current_state: Field) -> Field:

        raise NotImplementedError


class Computer(Player):

    __max_pos = SIZE - 1

    def __init__(self, player_mark: str):

        super().__init__(player_mark)
        seed()

    @abstractmethod
    def _get_difficulty_level(self) -> str:

        raise NotImplementedError

    @abstractmethod
    def _get_resolver(self) -> Resolver:

        raise NotImplementedError

    @staticmethod
    def _get_random_position(current_state: Field) -> Position:

        possible_moves = current_state.get_empty_fields()
        return choice(possible_moves)

    def make_move(self, current_state: Field) -> Field:

        print(COMPUTER_MOVE_PREFIX, self._get_difficulty_level())
        position = self._get_next_position(current_state)
        return get_new_field(position, self._mark, current_state)

    def _get_next_position(self, current_state: Field) -> Position:

        resolver = self._get_resolver()
        resolved = resolver.find_position(current_state)
        if resolved.position is not None:
            return resolved.position

        return self._get_random_position(current_state)


class EasyComputer(Computer):

    def __init__(self, player_mark: str):

        super().__init__(player_mark)
        self._resolver = NullResolver(self._mark)

    def _get_resolver(self) -> Resolver:

        return self._resolver

    def _get_difficulty_level(self) -> str:

        return '"easy"'


class MediumComputer(Computer):

    def __init__(self, player_mark: str):

        super().__init__(player_mark)
        self._resolver = SimpleResolver(self._mark)

    def _get_resolver(self) -> Resolver:

        return self._resolver

    def _get_difficulty_level(self) -> str:

        return '"medium"'


class HardComputer(Computer):

    def __init__(self, player_mark: str):

        super().__init__(player_mark)
        self._resolver = MinimaxResolver(self._mark)

    def _get_resolver(self) -> Resolver:

        return self._resolver

    def _get_difficulty_level(self) -> str:

        return '"hard"'


class User(Player):

    def make_move(self, current_state: Field) -> Field:

        return make_move(current_state, self._mark)


def create_player(player_mark: str, player_type: str) -> Player:
    """Create a player with given mark based on given type"""

    if player_type == "user":
        return User(player_mark)
    if player_type == "easy":
        return EasyComputer(player_mark)
    if player_type == "medium":
        return MediumComputer(player_mark)
    if player_type == "hard":
        return HardComputer(player_mark)

    raise UnknownPlayerTypeError
