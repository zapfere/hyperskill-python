from impl.field import Field
from impl.general import O, SIZE, X
from impl.player import Player, UnknownPlayerTypeError, create_player

GREETING = """Tic-Tac-Toe

Possible commands:
    start [player1] [player2] - play game with two chosen players
    exit - exit game
You can choose players from 'user' (for human player) or one of:
'easy', 'medium', 'hard' (for computer player).
"""
COMMAND_PROMPT = "Input command: "
EMPTY_FIELD_STR = "_" * SIZE ** 2


class BadCommandError(Exception):
    pass


def main():
    """Main loop"""

    print(GREETING)
    while True:
        try:
            command = input(COMMAND_PROMPT)
            if command == "exit":
                exit(0)
            players = parse_start_command(command)
            play_game(players)
        except (BadCommandError, UnknownPlayerTypeError):
            print("Bad parameters!")


def parse_start_command(command: str) -> (Player, Player):
    """Parse command and create two players"""

    tokens = command.split()
    if len(tokens) < 3 or tokens[0] != "start":
        raise BadCommandError
    return create_player(X, tokens[1]), create_player(O, tokens[2])


def play_game(players: (Player, Player)):
    """Play one game between given players"""

    current_field = Field(EMPTY_FIELD_STR)
    current_field.print()
    current_player = players[0]

    while current_field.moves_possible():
        current_field = current_player.make_move(current_field)
        current_field.print()
        current_player = switch_sides(current_player, players)

    current_field.print_result()


def switch_sides(current_player: Player, players: (Player, Player)) -> Player:
    """Change player from first to second and vice versa"""

    if current_player == players[0]:
        return players[1]
    return players[0]


if __name__ == "__main__":
    main()
