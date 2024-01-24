import threading
import time
import pytest
import logging
import socket

from pnet_dcp.l2socket.l2socket import L2PcapSocket
from pnet_dcp.l2socket.pcap_wrapper import WinPcap
from util import pcap_available, get_ip


@pytest.mark.skipif(not pcap_available(), reason="Could not find Pcap")
class TestPcapSocket:
    """Test the custom Pcap-based L2-Socket"""

    timeout = 10

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
        ip = get_ip()

        l2_socket = L2PcapSocket(ip)
        l2_socket.close()

    def test_open_close_ipv6(self):
        """
        Test opening and closing the Pcap-based socket with an IPv6 address.
        Expected results: no errors.
        """
        ip = get_ip(socket.AF_INET6)

        l2_socket = L2PcapSocket(ip)
        l2_socket.close()

    def test_open_invalid_ip(self):
        """
        Test opening the Pcap-based socket with an invalid ip address.
        Expected results: L2PcapSocket raises a ValueError.
        """
        invalid_ip = '192.0.2.0'
        with pytest.raises(ValueError):
            l2_socket = L2PcapSocket(invalid_ip)

    def test_filter(self, mock_return):
        """
        Test the BPF filter by sending and receiving two packets: one that fits the filter and one that does not.
        Expected results: the socket receives the packet which passes the filter while not receiving the other packet
        before the timeout.
        """
        mock_return.dst_custom = mock_return.dst[0]

        ip = get_ip()
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


class TestL2Socket:
    """Test L2-Socket functions on Windows and Linux."""

    timeout = 10

    def test_send(self, l2_sockets):
        """
        Test sending some dummy data from the socket.
        Expected results: no errors.
        """
        l2_socket = l2_sockets(1)[0]
        data = bytes([0] * 64)
        l2_socket.send(data)

    def test_recv(self, l2_sockets):
        """
        Test receiving some dummy data from the socket.
        Expected results: no errors.
        """
        l2_socket = l2_sockets(1)[0]
        l2_socket.recv()

    def test_send_recv(self, l2_sockets):
        """
        Test sending and receiving some dummy data from the socket.
        Expected results: the socket receives the sent data before the timeout.
        """
        # Get 2 sockets on the loopback adapter
        l2_socket_1, l2_socket_2 = l2_sockets(2)

        data = bytes([0] * 64)

        def send_data():
            time.sleep(1)
            l2_socket_1.send(data)

        t_send = threading.Thread(target=send_data, args=())
        t_send.start()

        start = time.time()
        packet_count = 0
        received_sent_data = False

        while time.time() < start + self.timeout:
            received = l2_socket_2.recv()
            if received is not None:
                packet_count += 1
            if received == data:
                received_sent_data = True
                break
        end = time.time()

        t_send.join()

        logging.info(f"Sent data {'received' if received_sent_data else 'not received'} after {packet_count} packets "
                     f"and {end - start}s")
        assert received_sent_data
