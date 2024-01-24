"""CLI Tool to set IP address."""
from pnet_dcp.pnet_dcp import DCP
from pnet_dcp.utils.logging import Logging


def add_set_ip_parser(subparsers):
    """Adds arguments to a provided subparsers instance"""
    parser_set_ip = subparsers.add_parser('set-ip')
    parser_set_ip.set_defaults(func=set_ip_func)

    parser_set_ip.add_argument('-i', '--ip-address', default="192.168.0.2",
                               help='IP address to apply (default: %(default)s).')
    parser_set_ip.add_argument('-s', '--subnet-mask', default="255.255.255.0",
                               help='Subnetmask to apply (default: %(default)s).')
    parser_set_ip.add_argument('-g', '--gateway-address', default="192.168.0.1",
                               help='Gateway address to apply (default: %(default)s).')
    parser_set_ip.add_argument('-p', '--permanent', action='store_true',
                               help='Apply settings permanently.')
    parser_set_ip.add_argument('-m', '--mac', default=None,
                               help='MAC address of device that should be configured.'
                                    'If None, pick first without IP. (default: %(default)s).')


def log_device(device):
    Logging.logger.info(f"Device '{device.name_of_station}':")
    for key, value in device.__dict__.items():
        Logging.logger.info(f"\t{key}: {value}")


def set_ip_func(args):
    """Executes subcommand based on provided arguments"""
    dcp = DCP(args.adapter_ip_address)

    identified_devices = dcp.identify_all()
    Logging.logger.info(f"Found {len(identified_devices)} devices:")
    for dev in identified_devices:
        log_device(dev)

    device = identified_devices[0]
    if (args.mac):
        try:
            device = next(
                dev for dev in identified_devices if dev.MAC == args.mac)
        except StopIteration:
            Logging.logger.error(f"MAC {args.mac} not found")
            return

    Logging.logger.info(f"Set IP address for '{device.name_of_station}'")

    ip_conf = [args.ip_address, args.subnet_mask, args.gateway_address]
    response = dcp.set_ip_address(
        mac=device.MAC, ip_conf=ip_conf, store_permanent=args.permanent)
    if not response:
        Logging.logger.error(
            f"Set IP address failed: {response.get_message()}")
        return
    Logging.logger.info(f"Successfully applied {ip_conf}")
