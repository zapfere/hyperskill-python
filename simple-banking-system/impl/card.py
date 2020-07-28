from __future__ import annotations
from random import randint, seed
from typing import Optional
from .exceptions import NotEnoughMoneyException

CARD_NUM_PREFIX = "400000"
MIN_CARD_NUM = 0
MAX_CARD_NUM = 999999999
MIN_PIN = 0
MAX_PIN = 9999


class Card:

    def __init__(self, card_num: str, pin: str, balance: Optional[int] = 0):

        self._card_num = card_num
        self._pin = pin
        self._balance = balance

    @staticmethod
    def generate_card() -> Card:

        card_num_suffix = randint(MIN_CARD_NUM, MAX_CARD_NUM)
        card_num = CARD_NUM_PREFIX + f"{card_num_suffix:09d}"
        card_num += generate_luhn_key(card_num)
        pin = randint(MIN_PIN, MAX_PIN)
        pin_str = f"{pin:04d}"
        return Card(card_num, pin_str)

    def get_card_num(self) -> str:

        return self._card_num

    def get_pin(self) -> str:

        return self._pin

    def get_balance(self) -> int:

        return self._balance

    def add_income(self, amount: int):

        self._balance += amount

    def check_withdraw(self, amount: int):

        if self._balance < amount:
            raise NotEnoughMoneyException

    def withdraw(self, amount: int):

        self.check_withdraw(amount)
        self._balance -= amount


def generate_luhn_key(card_num: str) -> str:

    digits = (int(digit) for digit in card_num)
    step1 = (digit if i % 2 else 2 * digit for i, digit in enumerate(digits))
    step2 = (digit if digit <= 9 else digit - 9 for digit in step1)
    step3 = sum(step2) % 10
    result = 0 if step3 == 0 else 10 - step3
    return str(result)


seed()
