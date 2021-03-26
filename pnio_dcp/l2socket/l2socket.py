"""
Copyright (c) 2021 Codewerk GmbH, Karlsruhe.
All Rights Reserved.
License: MIT License see LICENSE.md in the pnio_dcp root directory.
"""
from pnio_dcp.l2socket.pcap_wrapper import PcapWrapper


class L2PcapSocket:
    """
    An L2 socket based on a wrapper around the Pcap (WinPcap/Npcap) DLL.
    """

    def __init__(self, ip, interface=None, filter=None):
        """
        Open a socket on the network interface with the given IP and using the given BPF filter.
        :param ip: The IP address to open the socket on.
        :type ip: string
        :param interface: unused
        :type interface: Any
        :param filter: The BPF filter used to filter incoming packets directly within pcap (offers better performance
        than receiving all packets and only filtering in python).
        :type filter: string
        """
        self.pcap = PcapWrapper()
        pcap_device_name = self.pcap.get_device_name_from_ip(ip)
        self.pcap.open(pcap_device_name)
        if filter:
            self.pcap.set_bpf_filter(filter)

    def recv(self):
        """
        Receive the next packet from pcap.
        :return: The next raw packet (or None if no packet has been received e.g. due to a timeout).
        :rtype: Optional(bytes)
        """
        # Receive the next packet from pcap
        return self.pcap.get_next_packet()

    def send(self, data):
        """
        Send the given data as raw packet via pcap.
        :param data: The data to send.
        :type data: Any, will be converted to bytes
        """
        self.pcap.send(bytes(data))

    def close(self):
        """Close the connection."""
        self.pcap.close()
