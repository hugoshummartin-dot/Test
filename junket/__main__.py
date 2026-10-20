"""Play the Junket cocktail in the terminal: python -m junket [--seed N] [--save FILE]"""

import argparse
import json

from .cocktail import Cocktail, DURATION, APPROACH_COST, TALK_COST, HELP

INTRO = f"""\
PROJECT JUNKET — the cocktail
You're a student who has talked their way into a junket. {DURATION} minutes of drinks,
a hundred strangers, and somewhere among them the handful who could change your year.
Most are clueless or useless. Walking up to someone takes {APPROACH_COST} minutes; each
step of a conversation takes {TALK_COST}. Choose wisely.
"""


def main(argv=None):
    parser = argparse.ArgumentParser(prog="junket", description="Attend a junket and collect contacts.")
    parser.add_argument("--seed", type=int, help="random seed, for a reproducible room")
    parser.add_argument("--save", metavar="FILE", help="write your agenda and address book to a JSON file at the end")
    args = parser.parse_args(argv)

    game = Cocktail(seed=args.seed)
    print(INTRO)
    print(HELP)
    print()
    print(game.room())
    while not game.over:
        try:
            line = input(f"\n{game.status_line()} > ")
        except (EOFError, KeyboardInterrupt):
            print()
            break
        out = game.do(line)
        if out:
            print(out)

    print(game.debrief())
    if args.save:
        with open(args.save, "w") as f:
            json.dump(game.to_dict(), f, indent=2)
        print(f"\nSaved your agenda and address book to {args.save}.")


if __name__ == "__main__":
    main()
