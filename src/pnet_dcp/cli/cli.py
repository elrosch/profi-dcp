"""CLI Tool that distributes subcommands"""
import argparse
import logging
from pnet_dcp.cli.set_ip import add_set_ip_parser
from pnet_dcp.utils.logging import Logging


def main():
    """Parses command line arguments and calls corresponding subcommand program."""
    # Bus agnostic options
    parser = argparse.ArgumentParser()

    parser.add_argument('-a', '--adapter-ip-address', default="192.168.0.1",
                        help='IP address of the network adapter to use (default: %(default)s).')

    # Bus specific options
    parser.add_argument('-v', '--verbose', action='store_true',
                        help='increase output verbosity')

    subparsers = parser.add_subparsers(dest='subcommand', required=True,
                                       title='subcommands',
                                       help="Subcommand that should be called")

    # Options for position
    add_set_ip_parser(subparsers)

    args = parser.parse_args()
    if args.verbose:
        Logging(logging.INFO)
    else:
        Logging(logging.WARNING)

    args.func(args)


if __name__ == "__main__":
    main()
