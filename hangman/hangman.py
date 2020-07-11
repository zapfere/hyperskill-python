import random
from game import Game

# constants
title = "H A N G M A N"
menu_text = 'Type "play" to play the game, "exit" to quit: '
guessed_text = """You guessed the word!
You survived!"""
failed_text = "You are hanged!"

word_list = ["python", "java", "kotlin", "javascript"]


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


def main():
    print(title)
    action = input(menu_text)
    while action != "exit":
        if action == "play":
            play_game()
        print()
        action = input(menu_text)


if __name__ == "__main__":
    main()
