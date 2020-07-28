import sqlite3 as db
from sqlite3 import Connection
from typing import Optional
from .card import Card
from .exceptions import CardDoesntExistException


DB_NAME = "card.s3db"
CHECK_TABLE_QUERY = """select count(name) 
                         from sqlite_master 
                        where type='table' and name='card'"""
CREATE_TABLE_QUERY = """create table card(
                            id integer primary key autoincrement, 
                            number text not null unique, 
                            pin text not null, 
                            balance integer default 0
                        )"""
FIND_CARD_BY_NUMBER_QUERY = """select number, pin, balance 
                                 from card 
                                where number = ?"""
DELETE_CARD_BY_NUMBER_QUERY = """delete from card 
                                where number = ?"""
INSERT_CARD_QUERY = """insert into card (number, pin, balance) 
                                 values (?     , ?  , ?)"""
UPDATE_BALANCE_QUERY = """update card 
                             set balance = ? 
                           where number = ?"""

connection: Optional[Connection] = None


def startup():

    global connection
    connection = db.connect(DB_NAME)
    cur = connection.cursor()
    cur.execute(CHECK_TABLE_QUERY)
    if cur.fetchone()[0] == 0:
        cur.execute(CREATE_TABLE_QUERY)
        connection.commit()
    cur.close()


def shutdown():

    connection.close()


def create_account(account: Card):

    cur = connection.cursor()
    cur.execute(INSERT_CARD_QUERY, (account.get_card_num(),
                                    account.get_pin(),
                                    account.get_balance()))
    connection.commit()
    cur.close()


def update_balance(account: Card):

    cur = connection.cursor()
    cur.execute(UPDATE_BALANCE_QUERY, (account.get_balance(),
                                       account.get_card_num()))
    connection.commit()
    cur.close()


def fix_money_transfer(card_from: Card, card_to: Card):

    try:
        cur = connection.cursor()
        cur.execute(UPDATE_BALANCE_QUERY, (card_from.get_balance(),
                                           card_from.get_card_num()))
        cur.execute(UPDATE_BALANCE_QUERY, (card_to.get_balance(),
                                           card_to.get_card_num()))
        connection.commit()
        cur.close()
    except db.Error as err:
        connection.rollback()
        raise err


def get_account(number: str) -> Card:

    row = _get_account_row(number)
    if row is None:
        raise CardDoesntExistException
    return Card(row[0], row[1], row[2])


def _get_account_row(number: str) -> tuple:

    cur = connection.cursor()
    cur.execute(FIND_CARD_BY_NUMBER_QUERY, (number,))
    row = cur.fetchone()
    cur.close()
    return row


def delete_account(number: str):

    cur = connection.cursor()
    cur.execute(DELETE_CARD_BY_NUMBER_QUERY, (number,))
    connection.commit()
    cur.close()
