from collections import deque
from typing import List
from general import Operator, UnaryOperator
from errors import ExpressionError


class Parser:

    def __init__(self, tokens: List[object]):

        self._tokens = tokens
        self._operators = None
        self._result = None

    def parse(self) -> List[object]:
        """Parses sequence of tokens into reverse polish notation"""

        self._result = []
        self._operators = deque()

        for token in self._tokens:
            self._process_token(token)

        while len(self._operators) > 0:
            self._result.append(self._operators.pop())

        return self._result

    def _process_token(self, token: object) -> None:
        """Processes token using helper stack for operator reordering"""

        if isinstance(token, int):
            self._result.append(token)
        elif isinstance(token, Operator):
            self._process_operator(token)
        elif token == "(":
            self._operators.append(token)
        elif token == ")":
            self._process_right_bracket()
        else:
            raise ExpressionError

    def _process_operator(self, token: Operator) -> None:
        """Deals with operator basing on its priority"""

        if len(self._operators) == 0 or self._operators[-1] == "(":
            self._operators.append(token)
        else:
            operator = self._operators[-1]
            my_priority = token.get_priority()
            if my_priority > operator.get_priority():
                self._operators.append(token)
            else:
                self._push_operators(my_priority, token)

    def _push_operators(self, my_priority: int, token: Operator) -> None:
        """Push operators with priority higher than 'my_priority' to result"""

        self._result.append(self._operators.pop())

        while len(self._operators) > 0:

            operator = self._operators[-1]

            if operator == "(" or operator.get_priority() < my_priority:
                break

            self._result.append(self._operators.pop())

        self._operators.append(token)

    def _process_right_bracket(self) -> None:
        """Flushes operators from sub-expression to result"""

        while len(self._operators) > 0:
            operator = self._operators.pop()

            if operator == "(":
                break

            self._result.append(operator)


class Solver:

    def __init__(self, expression: List[object]):

        self._expr = expression
        self._buffer = None
        self._result = None

    def solve(self) -> int:
        """Solve expression given in reverse polish notation"""

        self._buffer = deque()

        for token in self._expr:
            if isinstance(token, int):
                self._buffer.append(token)
            elif isinstance(token, Operator):
                self._perform_calculation(token)

        self._result = self._buffer.pop()
        if len(self._buffer) == 0 and isinstance(self._result, int):
            return self._result

        raise ExpressionError

    def _perform_calculation(self, operator: Operator) -> None:
        """Perform calculation with one or two operands"""

        x = self._buffer.pop()
        if len(self._buffer) > 0:
            value = operator.compute(self._buffer.pop(), x)
            self._buffer.append(value)
        else:
            self._try_unary_operation(operator, x)

    def _try_unary_operation(self, operator: Operator, x: int) -> None:
        """Try unary operation if applicable, fail otherwise"""

        if isinstance(operator, UnaryOperator):
            value = operator.compute(x)
            self._buffer.append(value)
        else:
            raise ExpressionError
