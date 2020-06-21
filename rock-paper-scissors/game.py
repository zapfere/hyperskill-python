import random

# constants
default_options = ["rock", "paper", "scissors"]
result_text = dict(
    lose="Sorry, but computer chose {option}",
    draw="There is a draw ({option})",
    win="Well done. Computer chose {option} and failed"
)
exit_option = "!exit"
rating_option = "!rating"
file_name = "rating.txt"
name_request = "Enter your name: "
greeting_text = "Hello, {name}"
start_text = "Okay, let's start"
rating_text = "Your rating: {points}"
exit_text = "Bye!"
input_error = "Invalid input"
win_points = 100
draw_points = 50


def load_score(name):
    score = load_score_from_file()

    if name not in score:
        score[name] = 0

    return score


def load_score_from_file():
    score = {}
    file = open(file_name, "r", encoding="utf-8")

    for line in file:
        name, points = line.split()
        score[name] = int(points)

    file.close()
    return score


def get_game_options():
    options_str = input()

    if len(options_str) == 0:
        return default_options

    return options_str.split(sep=",")


def choose_action(user_option):
    if user_option == rating_option:
        print_rating()
    elif user_option in game_options:
        play_round(user_option)
    else:
        print(input_error)


def print_rating():
    points = all_score[user_name]
    print(rating_text.format(points=points))


def add_rating(points):
    all_score[user_name] += points


def play_round(user_option):
    computer_option = random.choice(game_options)
    result = check_result(user_option, computer_option)
    print_result(result, computer_option)


def check_result(user_option, computer_option):
    if user_option == computer_option:
        add_rating(draw_points)
        return "draw"

    if check_win(user_option, computer_option):
        add_rating(win_points)
        return "win"

    return "lose"


def check_win(user_option, computer_option):
    user_index = game_options.index(user_option)
    computer_index = game_options.index(computer_option)

    if user_index < computer_index:
        return computer_index - user_index > middle

    return user_index - computer_index <= middle


def print_result(result, computer_option):
    text = result_text[result].format(option=computer_option)
    print(text)


# main logic
random.seed()

user_name = input(name_request)
print(greeting_text.format(name=user_name))
all_score = load_score(user_name)
game_options = get_game_options()
middle = len(game_options) // 2
print(start_text)

option = input()

while option != exit_option:
    choose_action(option)
    option = input()

print(exit_text)
