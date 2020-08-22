from dataclasses import dataclass
from typing import Optional

SIZE = 3
X = "X"
O = "O"
EMPTY = " "
H_LINE = "-" * (2 * SIZE + 3)
V_LINE = "|"


@dataclass
class Position:
    x: int
    y: int


@dataclass
class RatedPosition:
    position: Optional[Position] = None
    rating: int = 0


@dataclass
class LineStatistics:
    x_count: int
    o_count: int
    has_empties: bool


@dataclass
class PartialResult:
    x_wins: Optional[bool]
    o_wins: Optional[bool]
    has_empties: Optional[bool]
    impossible: bool = False
