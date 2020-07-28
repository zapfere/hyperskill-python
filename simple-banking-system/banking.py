import sqlite3
from typing import Optional, Tuple
from impl.card import Card, generate_luhn_key
from impl.exceptions import MoneyTransferException, UnknownActionException, \
    AuthenticationException, CardDoesntExistException, \
    SameAccountException, WrongCardNumberException
from impl import db

BYE = "Bye!"
CREATED_MESSAGE = "Your card has been created"
CREATED_CARD_NUM = "Your card number:"
CREATED_PIN = "Your card PIN:"
CARD_NUM_PROMPT = "Enter your card number:"
PIN_PROMPT = "Enter your PIN:"
LOGIN_MESSAGE = "You have successfully logged in!"
LOGOUT_MESSAGE = "You have successfully logged out!"
ADD_INCOME_PROMPT = "Enter income:"
ADD_INCOME_MESSAGE = "Income was added!"
TRANSFER_TO_PROMPT = "Transfer\nEnter card number:"
TRANSFER_AMOUNT_PROMPT = "Enter how much money you want to transfer:"
TRANSFER_MESSAGE = "Success!"
CLOSE_ACCOUNT_MESSAGE = "The account has been closed!"
BALANCE_MESSAGE = "Balance:"
MAIN_MENU = """
1. Create an account
2. Log into account
0. Exit
"""
ACCOUNT_MENU = """
1. Balance
2. Add income
3. Do transfer
4. Close account
5. Log out
0. Exit
"""

active_card: Optional[Card] = None


def main():

    while True:
        try:
            print(MAIN_MENU)
            choose_main_menu_action()
        except UnknownActionException as err:
            print(err)


def choose_main_menu_action():

    action = input().strip()
    if action == "0":
        quit_program()
    if action == "1":
        create_account()
    elif action == "2":
        log_into_account()
    else:
        raise UnknownActionException(0, 2)


def quit_program():

    print(BYE)
    db.shutdown()
    exit(0)


def create_account():

    card = Card.generate_card()
    db.create_account(card)
    print(CREATED_MESSAGE)
    print(CREATED_CARD_NUM)
    print(card.get_card_num())
    print(CREATED_PIN)
    print(card.get_pin())


def log_into_account():

    try:
        card_num, pin = ask_for_card_data()
        card = search_for_card(card_num)
        check_pin(card, pin)
        print(LOGIN_MESSAGE)
        card_menu()
    except AuthenticationException as err:
        print(err)


def ask_for_card_data() -> Tuple[str, str]:

    print(CARD_NUM_PROMPT)
    card_num = input().strip()
    print(PIN_PROMPT)
    pin = input().strip()
    return card_num, pin


def search_for_card(card_num: str) -> Card:

    try:
        return db.get_account(card_num)
    except CardDoesntExistException:
        raise AuthenticationException


def check_pin(card: Card, pin: str):

    if card.get_pin() != pin:
        raise AuthenticationException
    global active_card
    active_card = card


def card_menu():

    action_code = None
    while action_code not in ("4", "5"):
        try:
            print(ACCOUNT_MENU)
            action_code = choose_card_menu_action()
        except UnknownActionException as err:
            print(err)


def choose_card_menu_action() -> str:

    action_code = input().strip()
    if action_code == "0":
        quit_program()
    if action_code == "1":
        print_balance()
    elif action_code == "2":
        add_income()
    elif action_code == "3":
        do_transfer()
    elif action_code == "4":
        close_account()
    elif action_code == "5":
        logout(LOGOUT_MESSAGE)
    else:
        raise UnknownActionException(0, 5)
    return action_code


def print_balance():

    print(BALANCE_MESSAGE, active_card.get_balance())


def add_income():

    try:
        print(ADD_INCOME_PROMPT)
        amount = int(input().strip())
        active_card.add_income(amount)
        db.update_balance(active_card)
        print(ADD_INCOME_MESSAGE)
    except (ValueError, sqlite3.Error) as err:
        print(err)


def do_transfer():

    try:
        print(TRANSFER_TO_PROMPT)
        card_num_to = input().strip()
        validate_target_card_num(card_num_to)
        card_to = db.get_account(card_num_to)
        print(TRANSFER_AMOUNT_PROMPT)
        amount = int(input().strip())
        perform_transfer(amount, card_to)
        print(TRANSFER_MESSAGE)
    except MoneyTransferException as err:
        print(err)


def perform_transfer(amount, card_to):

    active_card.withdraw(amount)
    card_to.add_income(amount)
    try:
        db.fix_money_transfer(active_card, card_to)
    except sqlite3.Error as err:
        active_card.add_income(amount)
        print(err)


def validate_target_card_num(card_num_to: str):

    if card_num_to == active_card.get_card_num():
        raise SameAccountException
    expected_key = generate_luhn_key(card_num_to[:-1])
    if card_num_to[-1] != expected_key:
        raise WrongCardNumberException


def close_account():

    try:
        db.delete_account(active_card.get_card_num())
        logout(CLOSE_ACCOUNT_MESSAGE)
    except sqlite3.Error as err:
        print(err)


def logout(message: str):

    global active_card
    active_card = None
    print(message)


if __name__ == "__main__":

    db.startup()
    main()
