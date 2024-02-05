"""CLI Tool to identify devices."""

from profi_dcp.profi_dcp import DCP
from profi_dcp.utils.logging import Logging


def add_identify_parser(subparsers):
    """Adds arguments to a provided subparsers instance"""
    parser_identify = subparsers.add_parser("identify")
    parser_identify.set_defaults(func=identify_func)

    parser_identify.add_argument(
        "-i",
        "--ip-address",
        default="192.168.0.1",
        help="IP address of the network interface to use (default: %(default)s).",
    )

    parser_identify.add_argument(
        "-m",
        "--mac",
        default=None,
        help="MAC address of device that should be identified (default: %(default)s).",
    )


def identify_func(args):
    """Executes subcommand based on provided arguments"""
    dcp = DCP(args.ip_address)

    identified_devices = dcp.identify_all()
    if not identified_devices:
        Logging.logger.error(f"No devices found")
        return

    if args.mac:
        try:
            device = next(dev for dev in identified_devices if dev.MAC == args.mac)
            device.to_log()
        except StopIteration:
            Logging.logger.error(f"MAC {args.mac} not found")
            return
    else:
        Logging.logger.info(f"Found {len(identified_devices)} devices:")
        for dev in identified_devices:
            dev.to_log()
