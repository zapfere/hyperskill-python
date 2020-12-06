from abc import ABCMeta
from dataclasses import dataclass
from sys import argv
from typing import IO, List, Optional

from bs4 import BeautifulSoup
from requests import HTTPError, Response, get

BASE_URL = 'https://context.reverso.net/translation'
REQUEST_HEADERS = {'User-Agent': 'Mozilla/5.0'}
LANGUAGES = [
    'arabic',
    'german',
    'english',
    'spanish',
    'french',
    'hebrew',
    'japanese',
    'dutch',
    'polish',
    'portuguese',
    'romanian',
    'russian',
    'turkish'
]
ANSWERS_LIMIT = 5
ALL_LANGUAGES = 'all'


@dataclass
class Query:
    from_language: str
    to_language: str
    word: str


@dataclass(eq=False)
class Result:
    to_language: str
    translations: List[str]
    examples: List[str]


class ApplicationError(Exception, metaclass=ABCMeta):
    pass


class ArgumentError(ApplicationError):
    def __init__(self, argument: str):
        self.argument = argument

    def __str__(self) -> str:
        return "Sorry, the program doesn't support " + self.argument


class TransferError(ApplicationError):
    def __str__(self) -> str:
        return 'Something wrong with your internet connection'


class TranslationError(ApplicationError):
    def __init__(self, word: str):
        self.word = word

    def __str__(self) -> str:
        return 'Sorry, unable to find ' + self.word


class ParseError(ApplicationError):
    def __init__(self, language: str):
        self.language = language

    def __str__(self) -> str:
        return 'Error parsing response for language ' + self.language


def parse_arguments() -> Query:
    if (len(argv)) < 4:
        print('Usage: translator.py [source_language] '
              '[target_language|all] [word_to_translate]')
        exit(1)

    from_language = get_language(argv[1], False)
    to_language = get_language(argv[2], True)
    word = argv[3].lower().strip()
    return Query(from_language, to_language, word)


def get_language(argument: str, all_permitted: bool) -> str:
    language = argument.lower().strip()
    if language in LANGUAGES or (all_permitted and language == ALL_LANGUAGES):
        return language

    raise ArgumentError(language)


def translate_all(input_data: Query) -> List[Result]:
    results = list()
    if input_data.to_language == ALL_LANGUAGES:
        for to_language in LANGUAGES:
            if to_language == input_data.from_language:
                continue
            input_data.to_language = to_language
            results.append(translate(input_data))
    else:
        results.append(translate(input_data))

    return results


def translate(input_data: Query) -> Result:
    response = perform_request(input_data)
    return parse_response(input_data.to_language, response)


def perform_request(input_data: Query) -> Response:
    url = f'{BASE_URL}/{input_data.from_language}-{input_data.to_language}' \
          f'/{input_data.word}'

    try:
        response = get(url, headers=REQUEST_HEADERS)
        check_response(input_data, response)
        return response
    except TranslationError as err:
        raise err
    except Exception:
        raise TransferError


def check_response(input_data: Query, response: Response):
    if not response.ok:
        if response.status_code == 404:
            raise TranslationError(input_data.word)

        raise HTTPError(
            f'Server responded with status code {response.status_code}'
        )


def parse_response(language: str, response: Response) -> Result:
    try:
        html = BeautifulSoup(response.text, 'html.parser')
        translations = extract_text(
            html, 'translations-content', 'translation', ANSWERS_LIMIT)
        examples = extract_text(
            html, 'examples-content', 'text', ANSWERS_LIMIT * 2)
        return Result(language, translations, examples)
    except Exception:
        raise ParseError(language)


def extract_text(parsed: BeautifulSoup,
                 part_id: str,
                 target_class: str,
                 limit: int) -> List[str]:
    part = parsed.find(id=part_id)
    found = part.find_all(class_=target_class)[:limit]
    return [tag.text.strip() for tag in found]


def print_results(word: str, results: List[Result]):
    with open(f'{word}.txt', 'w', encoding='UTF-8') as out_file:
        for result in results:
            print_result(result, out_file)
            print_result(result, None)


def print_result(result: Result, out_file: Optional[IO]):
    to_language = result.to_language.capitalize()
    print(f'{to_language} Translations:', file=out_file)
    for word in result.translations:
        print(word, file=out_file)
    print(f'\n{to_language} Examples:', file=out_file)
    for i in range(len(result.examples) // 2):
        print(result.examples[i * 2], file=out_file)
        print(result.examples[i * 2 + 1], file=out_file)
        print(file=out_file)
    print(file=out_file)


def main():
    try:
        input_data = parse_arguments()
        results = translate_all(input_data)
        print_results(input_data.word, results)
    except ApplicationError as error:
        print(error)


if __name__ == '__main__':
    main()
