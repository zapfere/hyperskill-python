import socket
from sys import argv
from typing import List

from impl.guessers import BehavioralGuesser


LOGIN_FILE_NAME = "logins.txt"


class WrongArgumentsError(Exception):
    def __init__(self):
        super().__init__(
            "Expected 2 arguments: IP address, port number"
        )


def main():
    host, port = parse_args()
    passwords = load_login_list()
    with socket.socket() as client:
        client.connect((host, port))
        guesser = BehavioralGuesser(client, passwords)
        result = guesser.hack_password()
        print(result)


def load_login_list() -> List[str]:
    with open(LOGIN_FILE_NAME, "r") as file:
        return [line[:-1] for line in file]


def parse_args() -> (str, int, str):
    if len(argv) < 3:
        raise WrongArgumentsError()
    return argv[1], int(argv[2])


if __name__ == '__main__':
    main()
