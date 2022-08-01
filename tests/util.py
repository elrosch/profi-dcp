
import psutil
import logging
import socket

from pnio_dcp.l2socket.pcap_wrapper import PcapWrapper


def pcap_available():
    """
    Checks, if Pcap is available. The check is done by trying to load the Pcap-DLL.
    Will return False, if the OS is not Windows or if Pcap is not installed on this machine.
    :return: True, if Pcap is available
    :rtype: boolean
    """
    try:
        PcapWrapper()
        return True
    except (OSError, KeyError):
        return False


def get_ip(address_family=socket.AF_INET):
    """
    Get the first valid IP address of the given address family (that is not a loop-back address).
    :param address_family: The address family, e.g. socket.AF_INET for IPv4 oder socket.AF_INET6 for IPv6.
    :type address_family: int
    :return: The first valid IP address found by psutil.
    :rtype: string
    """
    localhost = ['127.0.0.1', '::1']
    addrs = psutil.net_if_addrs()
    for iface_name, config in addrs.items():
        for address in config:
            if address.family == address_family and address.address not in localhost:
                logging.info(f"Using ip {address.address} for socket tests.")
                return address.address
    logging.warning("Could not find valid ip address with psutil.net_if_addrs()")


def get_network_interface(ip):
        """
        Get the name of the network interface corresponding to the given IP address by iterating over
        all available network interfaces and comparing the IP addresses.
        If no interface with the given IP address is found, a ValueError is raised.
        :param ip: The IP address to select the network interface with.
        :type ip: string
        :return: Interface name
        :rtype: string
        """
        for network_interface, addresses in psutil.net_if_addrs().items():
            addresses_by_family = {}
            for address in addresses:
                addresses_by_family.setdefault(address.family, []).append(address)

            # try to match either ipv4 or ipv6 address, ipv6 addresses may have additional suffix
            ipv4_match = any(address.address == ip for address in addresses_by_family.get(socket.AF_INET, []))
            ipv6_match = any(address.address.startswith(ip) for address in addresses_by_family.get(socket.AF_INET6, []))

            if ipv4_match or ipv6_match:
                if not addresses_by_family.get(psutil.AF_LINK, False):
                    logging.warning(f"Found network interface matching the ip {ip} but no corresponding mac address "
                                   f"with AF_LINK = {psutil.AF_LINK}")
                    continue
                return network_interface
        logging.debug(f"Could not find a network interface for ip {ip} in {psutil.net_if_addrs()}")
        raise ValueError(f"Could not find a network interface for ip {ip}.")
