import logging
import pytest
import threading
import time
import socket as sock
from pnet_dcp.pnet_dcp import DCP
from pnet_dcp.dcp_constants import ETHER_TYPE, FrameID, Option, ServiceID, ServiceType
from pnet_dcp.protocol import DCPBlockRequest, DCPPacket, EthernetPacket
from util import get_ip, pcap_available


def create_request(src_mac, dst_mac, service_id, options, xid):
    """
    Build the raw packet for a dcp request. This function is implemented
    here so as not to rely on the implementation in the dcp-lib.
    """
    option, suboption = options
    block = DCPBlockRequest(option, suboption, payload=bytes())

    # Create DCP frame
    service_type = ServiceType.REQUEST
    dcp_packet = DCPPacket(FrameID.GET_SET, service_id,
                           service_type, xid, payload=block)

    # Create ethernet frame
    ethernet_packet = bytes(EthernetPacket(
        dst_mac, src_mac, ETHER_TYPE, payload=dcp_packet))

    # Shorten response to cut off dcp set details like ip config
    ethernet_packet = ethernet_packet[:24] if len(
        ethernet_packet) > 24 else ethernet_packet

    return ethernet_packet


def thread_spam(socket, timeout, wait_time, data):
    """
    Send lot's of packets to the pcab buffer.
    """
    packet_number = 0
    timed_out = time.time() + timeout
    while time.time() < timed_out:
        for _ in range(10):
            # Use direct call to dll-Function to avoid delay due to buffer emptying
            # implemented in socket.pcap.send(...) respectively PcapWrapper.send(...)
            socket.pcap.win_pcap.pcap_sendpacket(
                socket.pcap.pcap, data, len(data))
            packet_number += 1
        time.sleep(wait_time)
    logging.info(
        f"Spam thread send {packet_number} packets ({(packet_number*len(data)):,} Bytes) in {timeout}s")


def thread_answer(socket, timeout, data, expected_packet):
    """
    Simulate a device by reading from the socket and answering with data
    after the expacted_packet has been received.
    """
    # Start receive loop with timeout
    timed_out = time.time() + timeout
    while time.time() < timed_out:
        try:
            received_packet = socket.recv()
        except sock.timeout:
            continue

        if received_packet:
            if len(received_packet) < len(expected_packet):
                continue
            if received_packet[:len(expected_packet)] == expected_packet:
                # Expected packet has been received, send anwer and return
                socket.send(data)
                return
    logging.error("Answer thread did not send an answer!")


@pytest.mark.skipif(not pcap_available(), reason="Could not find Pcap")
class TestHeavyNetwork:
    """
    Test the behavior in conditions with a lot of network traffic when
    using pcap.
    """
    host_mac = '02:00:00:00:00:05'
    device_mac = '02:00:00:00:00:02'
    device_spam_mac = '02:00:00:00:00:01'

    xid = 0xabcdabcd

    @pytest.mark.parametrize('n', range(4))
    def test_buffer_full_get_name(self, n, mock_return, loopback_sockets):
        """
        Fill the pcap buffer with packets and check if get_name_of_station
        still works.
        """
        # Get 2 sockets on the loopback adapter
        loopback_socket_1, loopback_socket_2 = loopback_sockets(2)

        # Init DCP on loopback adapder
        dcp = DCP(get_ip())
        dcp._DCP__socket.close()
        dcp._DCP__socket.pcap.open(r"\Device\NPF_Loopback")
        dcp.src_mac = self.host_mac

        # Change xid to match xids used in this test
        dcp._DCP__xid = self.xid

        # Create responses
        response_spam, response_answer, response_request = self.get_responses(
            mock_return, 'GET_NAME', self.xid+1)

        # Init threads
        t_spam = threading.Thread(target=thread_spam, args=(
            loopback_socket_1, 30.5, 0.005, response_spam))
        t_answer = threading.Thread(target=thread_answer, args=(
            loopback_socket_2, 40, response_answer, response_request))

        # Start the spam-dcp-thread and the answer-thread
        t_spam.start()
        t_answer.start()

        # Wait 30s (receive-buffer should be full by than)
        time.sleep(30)

        # Make DCP-request to get name
        name = dcp.get_name_of_station(self.device_mac)
        assert name == mock_return.devices[self.device_mac].NameOfStation

        # Join threads
        t_spam.join()
        t_answer.join()

    @pytest.mark.parametrize('n', range(4))
    def test_buffer_full_set_ip(self, n, mock_return, loopback_sockets):
        """
        Fill the pcap buffer with packets and check if set_ip_address
        still works.
        """
        # Get 2 sockets on the loopback adapter
        loopback_socket_1, loopback_socket_2 = loopback_sockets(2)

        # Init DCP on loopback adapder
        dcp = DCP(get_ip())
        dcp._DCP__socket.close()
        dcp._DCP__socket.pcap.open(r"\Device\NPF_Loopback")
        dcp.src_mac = self.host_mac

        # Change xid to match xids used in this test
        dcp._DCP__xid = self.xid

        # Create responses
        response_spam, response_answer, response_request = self.get_responses(
            mock_return, 'GET_IP', self.xid+1)

        # Init threads
        t_spam = threading.Thread(target=thread_spam, args=(
            loopback_socket_1, 30.5, 0.005, response_spam))
        t_answer = threading.Thread(target=thread_answer, args=(
            loopback_socket_2, 40, response_answer, response_request))

        # Start the spam-dcp-thread and the answer-thread
        t_spam.start()
        t_answer.start()

        # Wait 30s (receive-buffer should be full by than)
        time.sleep(30)

        # Make DCP-request to change the IP
        result = dcp.set_ip_address(
            self.device_mac, ("10.0.1.42", "255.255.240.0", "0.0.0.0"))
        assert result, f"Setting of IP address was not successfull, received {result}"

        # Join threads
        t_spam.join()
        t_answer.join()

    def get_responses(self, mock_return, request, xid):
        """
        Create a dcp device response for get_name_of_station or get_ip_address.
        """
        mock_return.src = self.host_mac
        mock_return.dst_custom = self.device_spam_mac
        response_spam = mock_return.identify_response(
            'IDENTIFY', xid=0xffff)[0]
        mock_return.dst_custom = self.device_mac

        if request == 'GET_NAME':
            response_answer = mock_return.identify_response('GET_NAME', xid=xid)[
                0]
            # Get request that will be send by dcp to trigger our response
            response_request = create_request(
                self.host_mac, self.device_mac, ServiceID.GET, Option.NAME_OF_STATION, self.xid+1)
        elif request == 'GET_IP':
            response_answer = mock_return.identify_response('SET', xid=xid)[0]
            # Get request that will be send by dcp to trigger our response
            response_request = create_request(
                self.host_mac, self.device_mac, ServiceID.SET, Option.IP_ADDRESS, self.xid+1)
        else:
            raise NotImplementedError(
                f"request must be one of 'GET_NAME', 'GET_IP'")

        return response_spam, response_answer, response_request
