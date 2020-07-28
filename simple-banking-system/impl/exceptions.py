from abc import ABCMeta


class UnknownActionException(Exception):

    def __init__(self, min_code: int, max_code: int):

        self.min_code = min_code
        self.max_code = max_code
        message = f"Unknown action code! " \
                  f"Enter a number from {min_code} to {max_code}"
        super().__init__(message)


class AuthenticationException(Exception):

    def __init__(self):

        super().__init__("Wrong card number or PIN!")


class MoneyTransferException(Exception, metaclass=ABCMeta):
    pass


class NotEnoughMoneyException(MoneyTransferException):

    def __init__(self):

        super().__init__("Not enough money!")


class SameAccountException(MoneyTransferException):

    def __init__(self):

        super().__init__("You can't transfer money to the same account!")


class WrongCardNumberException(MoneyTransferException):

    def __init__(self):

        super().__init__("Probably you made mistake in the card number. "
                         + "Please try again!")


class CardDoesntExistException(MoneyTransferException):

    def __init__(self):

        super().__init__("Such a card does not exist.")
