"""
Copyright (c) 2020 Codewerk GmbH, Karlsruhe.
All Rights Reserved.
License: MIT License see LICENSE.md in the pnio_dcp root directory.
"""
import binascii
import logging
import socket


logger = logging.getLogger("pnio_dcp")


def mac_address_to_bytes(mac_address):
    """
    Converts the mac address from ':'-separated strings to bytes by encoding each part as binary and concatenating them.
    :param mac_address: The mac address given as ':'-separated strings.
    :type mac_address: string
    :return: The mac address encoded as bytes.
    :rtype: bytes
    """
    return b''.join(binascii.unhexlify(num) for num in mac_address.split(':'))


def mac_address_to_string(mac_address):
    """
    Converts the mac address from bytes to ':'-separated strings by decoding each byte to a 2-digit lower-case string
    and concatenating them separated by ':'.
    :param mac_address: The mac address encoded as bytes.
    :type mac_address: bytes
    :return: The mac address as ':'-separated lower-case strings.
    :rtype: string
    """
    return ':'.join(format(num, '02x') for num in mac_address)


def ip_address_to_string(ip_address):
    """
    Converts the ip address from bytes to string using socket.inet_ntoa.
    :param ip_address: The ip address encoded as bytes.
    :type ip_address: bytes
    :return: The ip address as string.
    :rtype: string
    """
    return socket.inet_ntoa(ip_address)


def ip_address_to_bytes(ip_address):
    """
    Converts the IP address from '.'-separated string to bytes using socket.inet_aton.
    :param ip_address: The IP address given as '.'-separated strings.
    :type ip_address: string
    :return: The IP address encoded as bytes.
    :rtype: bytes
    """
    # Validation: an ip address should consist of exactly 4 octets, each an integer between 0 and 255.
    octets = list(ip_address.split('.'))
    if len(octets) != 4:
        raise ValueError('Provided IP-address of invalid length')
    if not all(octet.isdigit() for octet in octets):
        raise TypeError('Provided invalid IP-octet (non-integer)')
    if not all(0 <= int(octet) <= 255 for octet in octets):
        raise ValueError('Provided value exceeds the allowed range of IP octets (0-255)')

    return socket.inet_aton(ip_address)
