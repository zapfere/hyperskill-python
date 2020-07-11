from abc import ABCMeta

expression_error = "Invalid expression"
identifier_error = "Invalid identifier"
assignment_error = "Invalid assignment"
command_error = "Unknown command"
variable_error = "Unknown variable"


class CheckedError(Exception, metaclass=ABCMeta):
    pass


class CommandError(CheckedError):

    def __str__(self):

        return command_error


class IdentifierError(CheckedError):

    def __str__(self):

        return identifier_error


class AssignmentError(CheckedError):

    def __str__(self):

        return assignment_error


class ExpressionError(CheckedError):

    def __str__(self):

        return expression_error
