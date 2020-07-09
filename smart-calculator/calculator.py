from abc import ABCMeta
from collections import deque
from string import ascii_letters, digits
from typing import List, Optional, Type

# constants
help_option = "/help"
help_text = """The program calculates the result of given expression.
Expression consist of some numbers separated by '+', '-', '*', '/', '^' signs.
Expression can be grouped by matching pairs of brackets: '(' and ')'.
Each sign represents corresponding arithmetic operation.
Signs '+' and '-' can be repeated multiple times in a row.
Expression should start and end with a number or variable.
Variables can be assigned via 'name=value' notation.
Variable name should consist of latin letters only.
Variable value should be a number or previously set variable's name.
Enter '/exit' to exit from program."""
exit_option = "/exit"
exit_text = "Bye!"
expression_error = "Invalid expression"
identifier_error = "Invalid identifier"
assignment_error = "Invalid assignment"
command_error = "Unknown command"
variable_error = "Unknown variable"
variables = {}
operators = "+-*/^"


class CommandError(Exception):

    def __str__(self):
        return command_error


class IdentifierError(Exception):

    def __str__(self):

        return identifier_error


class AssignmentError(Exception):

    def __str__(self):

        return assignment_error


class ExpressionError(Exception):

    def __str__(self):

        return expression_error


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

    def extract(self) -> (Type[Operator], int):

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


def process_chosen_option(option: str) -> None:
    """Try to recognize and evaluate command or expression, handle errors"""

    try:
        choose_action(option)
    except (CommandError, IdentifierError, AssignmentError, ExpressionError) \
            as e:
        print(e)
    except KeyError:
        print(variable_error)
    except ValueError:
        print(expression_error)


def choose_action(option: str) -> None:
    """Parse given option to perform a command or evaluate an expression"""

    if len(option) == 0:
        return

    if option.startswith("/"):
        process_command(option)
    elif "=" in option:
        process_assignment(option)
    else:
        process_expression(option)


def process_command(option: str) -> None:
    """Perform given command if it's recognized"""

    if option == help_option:
        print(help_text)
        return

    raise CommandError


def process_assignment(option: str) -> None:
    """Perform variable assignment if possible"""

    parsed_str = [s.strip() for s in option.split("=")]
    validate_variable_name(parsed_str[0])
    assign_value(parsed_str)


def validate_variable_name(name: str) -> None:
    """Check if variable name is valid"""

    for char in name:
        if char not in ascii_letters:
            raise IdentifierError


def assign_value(parsed_str: List[str]) -> None:
    """Resolve given token to a number and assign it to given variable name"""

    if len(parsed_str) != 2 or len(parsed_str[1]) == 0:
        raise AssignmentError
    try:
        variables[parsed_str[0]] = resolve_value(parsed_str[1])
    except (ValueError, IdentifierError):
        raise AssignmentError


def resolve_value(token: str) -> int:
    """Try to resolve given token between number or known variable name"""

    try:
        return int(token)
    except ValueError:
        validate_variable_name(token)
        return variables[token]


def process_expression(expression_str: str) -> None:
    """Parse and evaluate an expression"""

    tokens = Tokenizer(expression_str).parse_tokens()
    parsed = Parser(tokens).parse()
    result = Solver(parsed).solve()

    print(result)


# main
chosen_option = input()

while chosen_option != exit_option:
    process_chosen_option(chosen_option)
    chosen_option = input()

print(exit_text)
