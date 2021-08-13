import time
import pytest
import psutil
import logging
import socket

from pnio_dcp.l2socket.l2socket import L2PcapSocket
from pnio_dcp.l2socket.pcap_wrapper import PcapWrapper
from pnio_dcp.l2socket.pcap_wrapper import WinPcap
from mock_return import MockReturn


@pytest.fixture(scope='function')
def l2_socket():
    """Open a L2PcapSocket on the first valid IPv4 address. Close the socket afterwards."""
    ip = TestPcapSocket.get_ip()
    l2_socket = L2PcapSocket(ip)
    yield l2_socket
    l2_socket.close()


def pcap_available():
    try:
        PcapWrapper()
        return True
    except (OSError, KeyError):
        return False


@pytest.mark.skipif(not pcap_available(), reason="Could not find Pcap")
class TestPcapSocket:
    """Test the custom Pcap-based L2-Socket"""

    timeout = 10

    @staticmethod
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

    def test_load_dll_twice(self):
        """
        Test loading the pcap DLL twice.
        Expected results: no errors.
        """
        # load DLL for the first time
        win_pcap1 = WinPcap()
        # set class variable to None so the DLL will be loaded a second time
        WinPcap._WinPcap__pcap_dll = None
        # load DLL a second time
        win_pcap2 = WinPcap()

    def test_open_close_ipv4(self):
        """
        Test opening and closing the Pcap-based socket with an IPv4 address.
        Expected results: no errors.
        """
        ip = TestPcapSocket.get_ip()

        l2_socket = L2PcapSocket(ip)
        l2_socket.close()

    def test_open_close_ipv6(self):
        """
        Test opening and closing the Pcap-based socket with an IPv6 address.
        Expected results: no errors.
        """
        ip = TestPcapSocket.get_ip(socket.AF_INET6)
        print(ip)

        l2_socket = L2PcapSocket(ip)
        l2_socket.close()

    def test_send(self, l2_socket):
        """
        Test sending some dummy data from the socket.
        Expected results: no errors.
        """
        data = bytes([0] * 64)
        l2_socket.send(data)

    def test_recv(self, l2_socket):
        """
        Test receiving some dummy data from the socket.
        Expected results: no errors.
        """
        l2_socket.recv()

    def test_send_recv(self, l2_socket):
        """
        Test sending and receiving some dummy data from the socket.
        Expected results: the socket receives the sent data before the timeout.
        """
        data = bytes([0] * 64)
        l2_socket.send(data)

        start = time.time()
        packet_count = 0
        received_sent_data = False

        while time.time() < start + self.timeout:
            received = l2_socket.recv()
            if received is not None:
                packet_count += 1
            if received == data:
                received_sent_data = True
                break
        end = time.time()

        logging.info(f"Sent data {'received' if received_sent_data else 'not received'} after {packet_count} packets "
                     f"and {end - start} s")
        assert received_sent_data

    def test_filter(self):
        """
        Test the BPF filter by sending and receiving two packets: one that fits the filter and one that does not.
        Expected results: the socket receives the packet which passes the filter while not receiving the other packet
        before the timeout.
        """
        mock_return = MockReturn()
        mock_return.dst_custom = mock_return.dst[0]

        ip = TestPcapSocket.get_ip()
        filter = f"ether host {mock_return.src} and ether proto {mock_return.eth_type}"
        valid_data = mock_return.identify_response('IDENTIFY')[0]
        invalid_data = bytes([0] * 64)

        l2_socket = L2PcapSocket(ip, filter)
        l2_socket.send(valid_data)

        end = time.time() + self.timeout
        received_valid_data = False

        while time.time() < end:
            received = l2_socket.recv()
            assert received != invalid_data
            if received == valid_data:
                received_valid_data = True

        assert received_valid_data

        l2_socket.close()
