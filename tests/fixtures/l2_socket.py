import pytest
from pnio_dcp.l2socket import L2Socket

from pnio_dcp.l2socket.l2socket import L2PcapSocket
from util import get_ip, get_network_interface


@pytest.fixture(scope='function')
def l2_sockets():
    """
    Returns a function that opens the given number of L2-sockets on the first valid IPv4 address.
    All sockets are closed in teardown.
    """
    ip=get_ip()
    network_interface = get_network_interface(ip)
    sockets = []
    def open_sockets(n):
        for _ in range(n):
            sockets.append(L2Socket(ip=ip, interface=network_interface, protocol=None))
        return sockets
    yield open_sockets
    for socket in sockets:
        socket.close()

@pytest.fixture(scope='function')
def loopback_sockets():
    """
    Returns a function that opens the given number of L2PcapSockets on the loopback device.
    All sockets are closed in teardown.
    """
    ip=get_ip()
    sockets = []
    def open_sockets(n):
        for _ in range(n):
            socket = L2PcapSocket(ip)
            socket.close()
            socket.pcap.open(r"\Device\NPF_Loopback")
            sockets.append(socket)
        return sockets
    yield open_sockets
    for socket in sockets:
        socket.close()

