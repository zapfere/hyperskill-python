from string import ascii_letters
from typing import List
from errors import AssignmentError, CheckedError, CommandError, IdentifierError
from errors import expression_error, variable_error
from general import variables
from solver import Parser, Solver
from tokenizer import Tokenizer

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


def process_chosen_option(option: str) -> None:
    """Try to recognize and evaluate command or expression, handle errors"""

    try:
        choose_action(option)
    except CheckedError as e:
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


def main():
    chosen_option = input()

    while chosen_option != exit_option:
        process_chosen_option(chosen_option)
        chosen_option = input()

    print(exit_text)


if __name__ == "__main__":
    main()
