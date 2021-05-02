import argparse
import os
import pickle
import pprint

from model import Model
from player import ComputerPlayer


def run_game(player1, player2):
    """
    Returns
    ---
    Boolean, True if player1 wins
    """

    # Gameplay
    while True:

        player1.turn(player2)

        if not player2.alive():
            return True
            # 'Player B loses'

        player2.turn(player1)

        if not player1.alive():
            return False
            # 'Player A loses'


def main(debug=False, warm_start=False, opponent=None, num_games=1000, overwrite=False):

    # Initialization
    attack_dict = None
    if warm_start and os.path.isfile("attack_dict.pickle"):
        attack_dict = pickle.load(open("attack_dict.pickle", "rb"))

    redistribution_dict = None
    if warm_start and os.path.isfile("redistribution_dict.pickle"):
        redistribution_dict = pickle.load(open("redistribution_dict.pickle", "rb"))

    model1 = Model(
        attack_dict=attack_dict, redistribution_dict=redistribution_dict, debug=debug
    )

    if opponent == "self":
        model2 = model1
    elif opponent == "naive":
        model2 = None
    elif opponent == "independent":
        attack_dict2 = None
        if warm_start and os.path.isfile("attack_dict2.pickle"):
            attack_dict2 = pickle.load(open("attack_dict2.pickle", "rb"))

        redistribution_dict2 = None
        if warm_start and os.path.isfile("redistribution_dict2.pickle"):
            redistribution_dict2 = pickle.load(
                open("redistribution_dict2.pickle", "rb")
            )

        model2 = Model(
            attack_dict=attack_dict2,
            redistribution_dict=redistribution_dict2,
            debug=debug,
        )
    else:
        raise NotImplementedError()

    # Iterative gameplay
    num_player1_wins = 0

    for i in range(num_games):
        player1 = ComputerPlayer(model=model1, name="A")
        player2 = ComputerPlayer(model=model2, name="B")

        player1_wins = run_game(player1, player2)
        if player1_wins:
            if debug:
                print(f"Player 2 loses game {i}")
            player1.model.update(player1.attacks, player1.redistributions, True)
            player2.model.update(player2.attacks, player2.redistributions, False)
            num_player1_wins += 1
        else:
            if debug:
                print(f"Player 1 loses game {i}")
            player1.model.update(player1.attacks, player1.redistributions, False)
            player2.model.update(player2.attacks, player2.redistributions, True)

        if debug:
            print(f"Player 1's attacks: {player1.attacks}")
            print(f"Player 2's attacks: {player2.attacks}")

    # Look at model(s) that evolved
    if debug:
        print("Attack dictionary")
        pprint.pprint(player1.model._attack_dict)
        if opponent == "independent":
            pprint.pprint(player2.model._attack_dict)
        print("Redistribution dictionary")
        pprint.pprint(player1.model._redistribution_dict)
        if opponent == "independent":
            pprint.pprint(player2.model._redistribution_dict)

    if overwrite:
        pickle.dump(player1.model._attack_dict, open("attack_dict.pickle", "wb"))
        pickle.dump(
            player1.model._redistribution_dict, open("redistribution_dict.pickle", "wb")
        )
        if opponent == "independent":
            pickle.dump(player2.model._attack_dict, open("attack_dict2.pickle", "wb"))
            pickle.dump(
                player2.model._redistribution_dict,
                open("redistribution_dict2.pickle", "wb"),
            )

    print(f"Player 1 wins {num_player1_wins} out of {num_games} games")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Train RL chopstick agent.")
    parser.add_argument(
        "--debug",
        action="store_true",
        help="print debug messages to stderr and sets num-games to 1",
        default=False,
    )
    parser.add_argument(
        "--warm-start",
        action="store_true",
        help="try to start with weights from disk, if available",
        default=False,
    )
    parser.add_argument(
        "--overwrite",
        action="store_true",
        help="write model weights back to disk",
        default=False,
    )
    parser.add_argument(
        "--opponent",
        choices=["self", "naive", "independent"],
        help="type of agent to play against",
        default="independent",
    )
    parser.add_argument(
        "--num-games",
        type=int,
        help="number of games for which to run training, set to 1 if debug is True",
        default=1000,
    )
    args = parser.parse_args()

    num_games = 1 if args.debug else args.num_games
    main(
        debug=args.debug,
        warm_start=args.warm_start,
        opponent=args.opponent,
        num_games=num_games,
        overwrite=args.overwrite,
    )
