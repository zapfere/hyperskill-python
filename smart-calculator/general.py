from abc import ABCMeta
from typing import Optional


variables = {}
operators = "+-*/^"


class Token:

    @staticmethod
    def allows_next():
        """Check what chars are allowed after that"""

        raise NotImplementedError


class Operator(metaclass=ABCMeta):

    @staticmethod
    def compute(x1: int, x2: int) -> int:
        """Perform encapsulated operation"""

        raise NotImplementedError

    @staticmethod
    def get_priority() -> int:
        """Get operator priority"""

        raise NotImplementedError


class UnaryOperator(Operator, metaclass=ABCMeta):

    @staticmethod
    def compute(x1: int, x2: Optional[int] = None) -> int:

        raise NotImplementedError
