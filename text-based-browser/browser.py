import os
import requests
import sys
from abc import ABCMeta
from collections import deque
from typing import Deque, Optional, Set

from bs4 import BeautifulSoup
from colorama import Fore, init

PARSER_NAME = "html.parser"
PROTOCOL = "https://"
TAGS = (
    "title", "p", "h1", "h2", "h3", "h4", "h5", "h6", "a", "ul", "ol", "li"
)

saved_pages_dir: str = "."
saved_pages: Set[str] = set()
current_url: Optional[str] = None
history: Deque[str] = deque()


class BrowserError(Exception, metaclass=ABCMeta):
    pass


class IncorrectUrlError(BrowserError):

    def __str__(self):
        return "Error: Incorrect URL"


class FailedRequestError(BrowserError):

    def __init__(self, status_code: int):
        super().__init__(
            "Failed to open URL, HTTP result code: " + str(status_code)
        )
        self._status_code = status_code


def create_dir_if_needed():
    args = sys.argv
    if len(args) > 1:
        global saved_pages_dir
        saved_pages_dir = args[1]
        try:
            os.makedirs(saved_pages_dir)
        except FileExistsError:
            # directory already exists, no action needed
            pass


def main():
    while True:
        get_next_command()


def get_next_command():
    command = input().strip()
    if command == "exit":
        exit(0)
    if command == "back":
        go_back()
        return
    try:
        url = navigate(command)
        update_history(url)
    except BrowserError as err:
        print(err)


def go_back():
    if len(history) > 0:
        url = history.pop()
        navigate(url)


def navigate(url: str) -> str:
    try:
        url = validate_url(url)
        open_url(url)
    except IncorrectUrlError:
        find_saved_page(url)

    return url


def update_history(url):
    global current_url

    if current_url is not None:
        history.append(current_url)

    current_url = url


def validate_url(url: str) -> str:
    if url.find(".") == -1:
        raise IncorrectUrlError
    return url if url.startswith(PROTOCOL) else PROTOCOL + url


def open_url(url: str):
    result = requests.get(url)

    if not result:
        raise FailedRequestError(result.status_code)

    page_content = extract_result_text(result.content)
    print(page_content)
    save_page(url, page_content)


def extract_result_text(content: bytes) -> str:
    parsed = BeautifulSoup(content, PARSER_NAME)
    lines = (Fore.BLUE + tag.text + Fore.RESET
             if tag.name == "a" else tag.text
             for tag in parsed.find_all(TAGS))
    return "\n".join(lines)


def save_page(url: str, page_content: str):
    # first remove protocol and top-level domain
    file_name = url.split("://")[-1].split(".")[-2]
    full_name = saved_pages_dir + os.sep + file_name
    with open(full_name, "w") as saved_page:
        saved_page.write(page_content)
    saved_pages.add(file_name)


def find_saved_page(url: str):
    if url in saved_pages:
        path_to_file = saved_pages_dir + os.sep + url
        with open(path_to_file, "r") as saved_page:
            for line in saved_page:
                print(line, end="")
            print()
    else:
        raise IncorrectUrlError


if __name__ == "__main__":
    create_dir_if_needed()
    init()
    main()
