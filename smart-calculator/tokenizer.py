from abc import ABCMeta
from string import ascii_letters, digits
from typing import List, Optional
from errors import ExpressionError
from general import Operator, UnaryOperator, operators, variables


class Plus(UnaryOperator):

    @staticmethod
    def compute(x1: int, x2: Optional[int] = None) -> int:

        if x2 is None:
            return x1

        return x1 + x2

    @staticmethod
    def get_priority() -> int:

        return 1

    def __repr__(self):

        return "+"


class Minus(UnaryOperator):

    @staticmethod
    def compute(x1: int, x2: Optional[int] = None) -> int:

        if x2 is None:
            return -x1

        return x1 - x2

    @staticmethod
    def get_priority() -> int:

        return 1

    def __repr__(self):

        return "-"


class Multiply(Operator):

    @staticmethod
    def compute(x1: int, x2: int) -> int:

        return x1 * x2

    @staticmethod
    def get_priority() -> int:

        return 2

    def __repr__(self):

        return "*"


class Divide(Operator):

    @staticmethod
    def compute(x1: int, x2: int) -> int:

        try:
            return x1 // x2
        except ZeroDivisionError:
            raise ExpressionError

    @staticmethod
    def get_priority() -> int:

        return 2

    def __repr__(self):

        return "/"


class Power(Operator):

    @staticmethod
    def compute(x1: int, x2: int) -> int:

        return x1 ** x2

    @staticmethod
    def get_priority() -> int:

        return 3

    def __repr__(self):

        return "^"


class TokenExtractor(metaclass=ABCMeta):

    def __init__(self, expression_str: str, start_pos: int):

        self._str = expression_str
        self._start_pos = start_pos
        self._max_pos = len(expression_str) - 1

    @staticmethod
    def allows_next() -> str:
        """Check what chars are allowed after that"""

        raise NotImplementedError

    @staticmethod
    def can_be_parsed(expression_str: str, pos: int) -> bool:
        """Check if given string position can be parsed by this extractor"""

        raise NotImplementedError

    def _extraction_finished(self, pos: int) -> bool:
        """Check if token is fully read"""

        raise NotImplementedError

    def extract(self) -> (object, int):
        """Extract token and return it with first position after it"""

        chars = []
        last_pos = self._start_pos

        for pos in range(self._start_pos, self._max_pos + 1):

            if self._extraction_finished(pos):
                break

            chars.append(self._str[pos])
            last_pos += 1

        return "".join(chars), last_pos


class OperandExtractor(TokenExtractor, metaclass=ABCMeta):

    @staticmethod
    def allows_next() -> str:

        return ")" + operators


class NumberExtractor(OperandExtractor):

    def __init__(self, expression_str: str, start_pos: int):

        super().__init__(expression_str, start_pos)

    @staticmethod
    def can_be_parsed(expression_str: str, pos: int) -> bool:

        return expression_str[pos] in digits

    def extract(self) -> (object, int):

        chars, pos = super().extract()
        return int(chars), pos

    def _extraction_finished(self, pos) -> bool:

        return not NumberExtractor.can_be_parsed(self._str, pos)


class VariableExtractor(OperandExtractor):

    def __init__(self, expression_str: str, start_pos: int):

        super().__init__(expression_str, start_pos)

    @staticmethod
    def can_be_parsed(expression_str: str, pos: int) -> bool:

        return expression_str[pos] in ascii_letters

    def extract(self) -> (int, int):

        name, pos = super().extract()
        # variable name extracted - get value
        value = variables[name]

        return value, pos

    def _extraction_finished(self, pos) -> bool:

        return not VariableExtractor.can_be_parsed(self._str, pos)


class OperatorExtractor(TokenExtractor, metaclass=ABCMeta):

    @staticmethod
    def allows_next() -> bool:

        return "(" + ascii_letters + digits


class PlusMinusExtractor(OperatorExtractor, metaclass=ABCMeta):

    def __init__(self, expression_str: str, start_pos: int, operation: str):

        super().__init__(expression_str, start_pos)
        self._op = operation
        forbidden = set(operators)
        forbidden.remove(operation)
        self._forbidden = forbidden

    def _extraction_finished(self, pos: int) -> bool:

        char = self._str[pos]

        if char in self._forbidden:
            raise ExpressionError

        return char != self._op


class PlusExtractor(PlusMinusExtractor):

    def __init__(self, expression_str: str, start_pos: int):

        super().__init__(expression_str, start_pos, "+")

    @staticmethod
    def can_be_parsed(expression_str: str, pos: int) -> bool:

        return expression_str[pos] == "+"

    def extract(self) -> (Plus, int):

        _, pos = super().extract()
        # any number of '+' is '+'
        return Plus(), pos


class MinusExtractor(PlusMinusExtractor):

    def __init__(self, expression_str: str, start_pos: int):

        super().__init__(expression_str, start_pos, "-")

    @staticmethod
    def can_be_parsed(expression_str: str, pos: int) -> bool:

        return expression_str[pos] == "-"

    def extract(self) -> (Operator, int):

        # even number of '-' is '+'
        token, pos = TokenExtractor.extract(self)
        return Minus() if len(token) % 2 else Plus(), pos


class SingleCharExtractor(TokenExtractor, metaclass=ABCMeta):

    def _extraction_finished(self, pos: int) -> bool:

        return self._start_pos != pos


class OtherOperatorsExtractor(OperatorExtractor, SingleCharExtractor):

    _allowed = "*/^"

    def __init__(self, expression_str: str, start_pos: int):

        super().__init__(expression_str, start_pos)

    @staticmethod
    def can_be_parsed(expression_str: str, pos: int) -> bool:

        return expression_str[pos] in OtherOperatorsExtractor._allowed

    @staticmethod
    def _wrap_operator(char: str) -> Operator:

        index = OtherOperatorsExtractor._allowed.find(char)

        if index == 0:
            return Multiply()
        if index == 1:
            return Divide()
        if index == 2:
            return Power()

        raise ExpressionError

    def extract(self) -> (Operator, int):

        pos = self._start_pos
        char = self._str[pos]

        return self._wrap_operator(char), pos + 1


class LeftBracketExtractor(SingleCharExtractor):

    @staticmethod
    def allows_next() -> str:

        return "(" + ascii_letters + digits

    @staticmethod
    def can_be_parsed(expression_str: str, pos: int) -> bool:

        return expression_str[pos] == "("


class RightBracketExtractor(SingleCharExtractor):

    @staticmethod
    def allows_next() -> str:

        return ")" + operators

    @staticmethod
    def can_be_parsed(expression_str: str, pos: int) -> bool:

        return expression_str[pos] == ")"


class Tokenizer:

    def __init__(self, expression_str: str):

        self._str = expression_str.replace(" ", "")
        self._last_char_idx = len(self._str) - 1
        self._pos = 0
        self._result = None

    def parse_tokens(self) -> List[object]:
        """Convert input string to sequence of tokens"""

        self._result = []
        self._validate_edges()

        pos = self._parse_next_token(0)
        while pos <= self._last_char_idx:
            pos = self._parse_next_token(pos)

        self._validate_result()

        return self._result

    def _validate_edges(self) -> None:
        """Preliminary validation of input string's edges"""

        not_first = "*/^)"
        not_last = "+-*/^("

        if self._str[0] in not_first \
                or self._str[self._last_char_idx] in not_last:
            raise ExpressionError

    def _parse_next_token(self, pos: int) -> int:
        """Extract next token from given position"""

        extractor = self._get_next_extractor(pos)
        token, next_pos = extractor.extract()
        self._result.append(token)
        self._validate_allowed(next_pos, extractor.allows_next())
        return next_pos

    def _get_next_extractor(self, pos: int) -> TokenExtractor:
        """Resolve token extractor for given position"""

        _str = self._str

        if NumberExtractor.can_be_parsed(_str, pos):
            return NumberExtractor(_str, pos)
        elif VariableExtractor.can_be_parsed(_str, pos):
            return VariableExtractor(_str, pos)
        elif PlusExtractor.can_be_parsed(_str, pos):
            return PlusExtractor(_str, pos)
        elif MinusExtractor.can_be_parsed(_str, pos):
            return MinusExtractor(_str, pos)
        elif OtherOperatorsExtractor.can_be_parsed(_str, pos):
            return OtherOperatorsExtractor(_str, pos)
        elif LeftBracketExtractor.can_be_parsed(_str, pos):
            return LeftBracketExtractor(_str, pos)
        elif RightBracketExtractor.can_be_parsed(_str, pos):
            return RightBracketExtractor(_str, pos)
        else:
            # no extractor is applicable here
            raise ExpressionError

    def _validate_allowed(self, pos: int, allowed: str) -> None:
        """Check that previous extractor allows char at given position"""

        if pos <= self._last_char_idx and self._str[pos] not in allowed:
            raise ExpressionError

    def _validate_result(self) -> None:
        """Validate token sequence"""

        self._validate_brackets()

        last_index = len(self._result) - 1
        middle_index = last_index // 2

        self._validate_edge(0, middle_index)
        self._validate_edge(last_index, middle_index)

    def _validate_brackets(self) -> None:
        """Validate that all brackets are paired"""

        lefts = 0
        rights = 0

        for token in self._result:
            if token == "(":
                lefts += 1
            elif token == ")":
                rights += 1

        if lefts != rights:
            raise ExpressionError

    def _validate_edge(self, index: int, middle: int) -> None:
        """Validate first and last token"""

        token = self._result[index]

        if token == "(" and index <= middle:
            self._validate_edge(index + 1, middle)
            return

        if token == ")" and index > middle:
            self._validate_edge(index - 1, middle)
            return

        if not isinstance(token, int):
            if index > middle or not isinstance(token, UnaryOperator):
                raise ExpressionError
