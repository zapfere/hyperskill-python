import random
import string

# constants
title = "H A N G M A N"
menu_text = 'Type "play" to play the game, "exit" to quit: '
guessed_text = """You guessed the word!
You survived!"""
failed_text = "You are hanged!"
no_such_letter = "No such letter in the word"
error_already_tried = "You already typed this letter"
error_not_letter = "It is not an ASCII lowercase letter"
error_str_too_long = "You should input a single letter"
enter_letter = "Input a letter: "
num_tries = 8

word_list = ["python", "java", "kotlin", "javascript"]


class Game:

    def __init__(self, generated_word):
        self.word = generated_word
        self.letters = set(generated_word)
        self.attempted_letters = set()
        self.guessed_letters = set()
        self.remaining_attempts = num_tries
        self.not_guessed = True

    def try_letter(self, letter):
        if not_a_letter(letter) or self.already_tried(letter):
            return

        self.attempted_letters.add(letter)
        if letter in self.letters:
            self.guessed_letters.add(letter)
        else:
            self.remaining_attempts -= 1
            print(no_such_letter)

    def print_guessed(self):
        text = [
            letter if letter in self.guessed_letters else "-"
            for letter in self.word
        ]
        print(*text, sep="")

    def already_tried(self, letter):
        already_attempted = letter in self.attempted_letters

        if already_attempted:
            print(error_already_tried)

        return already_attempted

    def play_round(self):
        if self.remaining_attempts <= 0:
            raise AssertionError

        print()
        self.print_guessed()
        letter = input(enter_letter)
        self.try_letter(letter)

    def is_not_finished(self):
        if self.guessed_letters == self.letters:
            self.not_guessed = False

        return self.remaining_attempts > 0 and self.not_guessed

    def is_guessed(self):
        return not self.not_guessed


def not_a_letter(input_str):
    if len(input_str) != 1:
        print(error_str_too_long)
        return True

    if input_str not in string.ascii_lowercase:
        print(error_not_letter)
        return True

    return False


def play_game():
    secret_word = start_new_game()

    while secret_word.is_not_finished():
        secret_word.play_round()

    check_result(secret_word)


def start_new_game():
    random.seed()
    chosen_word = random.choice(word_list)
    return Game(chosen_word)


def check_result(word):
    if word.is_guessed():
        print()
        word.print_guessed()
        print(guessed_text)
    else:
        print(failed_text)


# main logic
print(title)
action = input(menu_text)
while action != "exit":
    if action == "play":
        play_game()
    print()
    action = input(menu_text)
