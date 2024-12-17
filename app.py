from argparse import ArgumentParser

OPERATION_DICT = {"health": lambda: print("I'm healthy!")}
"""The dictionary of operations application supports."""

if __name__ == "__main__":
    parser = ArgumentParser()
    parser.add_argument(
        "operation",
        type=str,
        choices=OPERATION_DICT.keys(),
        help="The operation to run.",
    )
    args = parser.parse_args()
    OPERATION_DICT[args.operation]()
