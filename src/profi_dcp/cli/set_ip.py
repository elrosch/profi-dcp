"""CLI Tool to set IP address."""

from profi_dcp.profi_dcp import DCP
from profi_dcp.utils.logging import Logging


def add_set_ip_parser(subparsers):
    """Adds arguments to a provided subparsers instance"""
    parser_set_ip = subparsers.add_parser("set-ip")
    parser_set_ip.set_defaults(func=set_ip_func)

    parser_set_ip.add_argument(
        "-i",
        "--ip-address",
        default="192.168.0.2",
        help="IP address to apply (default: %(default)s).",
    )
    parser_set_ip.add_argument(
        "-s",
        "--subnet-mask",
        default="255.255.255.0",
        help="Subnetmask to apply (default: %(default)s).",
    )
    parser_set_ip.add_argument(
        "-g",
        "--gateway-address",
        default="192.168.0.1",
        help="Gateway address to apply (default: %(default)s).",
    )
    parser_set_ip.add_argument(
        "-p", "--permanent", action="store_true", help="Apply settings permanently."
    )
    parser_set_ip.add_argument(
        "-m",
        "--mac",
        default=None,
        help="MAC address of device that should be configured."
        "If None, pick first or first unconfigured from list (depending on -u value). (default: %(default)s).",
    )
    parser_set_ip.add_argument(
        "-u", "--only-unconfigured", action="store_true", help="Only set IP for first unconfigured device in list."
    )


def set_ip_func(args):
    """Executes subcommand based on provided arguments"""
    dcp = DCP(args.ip_address)

    identified_devices = dcp.identify_all()
    if not identified_devices:
        Logging.logger.error(f"No devices found")
        return

    if args.mac:
        try:
            device = next(
                dev for dev in identified_devices if dev.MAC == args.mac)
            device.to_log()
        except StopIteration:
            Logging.logger.error(f"MAC {args.mac} not found")
            return
    else:
        Logging.logger.info(f"Found {len(identified_devices)} devices:")
        for dev in identified_devices:
            dev.to_log()
        device = identified_devices[0]
        if args.only_unconfigured:
            try:
                device = next(
                    dev for dev in identified_devices if dev.IP == "0.0.0.0")
                device.to_log()
            except StopIteration:
                Logging.logger.error(f"No unconfigured device found")
                return

    Logging.logger.info(f"Set ip address for '{device.name_of_station}'")

    ip_conf = [args.ip_address, args.subnet_mask, args.gateway_address]
    response = dcp.set_ip_address(
        mac=device.MAC, ip_conf=ip_conf, store_permanent=args.permanent
    )
    if not response:
        Logging.logger.error(
            f"Setting of ip address failed: {response.get_message()}")
        return
    Logging.logger.info(f"Successfully applied {ip_conf}")
