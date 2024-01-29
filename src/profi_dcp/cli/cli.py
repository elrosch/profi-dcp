"""CLI Tool that distributes subcommands"""
import argparse
import logging
from profi_dcp.cli.set_ip import add_set_ip_parser
from profi_dcp.utils.logging import Logging


def main():
    """Parses command line arguments and calls corresponding subcommand program."""
    # Bus agnostic options
    parser = argparse.ArgumentParser()

    # Bus specific options
    parser.add_argument(
        "-v", "--verbose", action="store_true", help="increase output verbosity"
    )

    subparsers = parser.add_subparsers(
        dest="subcommand",
        required=True,
        title="subcommands",
        help="Subcommand that should be called",
    )

    # Options for position
    add_set_ip_parser(subparsers)

    args = parser.parse_args()
    if args.verbose:
        Logging(logging.DEBUG)
    else:
        Logging(logging.WARNING)

    args.func(args)


if __name__ == "__main__":
    main()
