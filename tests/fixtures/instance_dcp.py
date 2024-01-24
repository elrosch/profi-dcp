import pytest
from profinet_dcp.profinet_dcp import DCP
import configparser
from unittest.mock import patch, MagicMock


@pytest.fixture(scope='function')
@patch('profinet_dcp.profinet_dcp.L2Socket')
@patch('profinet_dcp.profinet_dcp.psutil.net_if_addrs')
def instance_dcp(psutil_net_if_addrs, socket, mock_return):
    """
    Provides a dcp instance with a mocked socket and the mocked socket.
    """
    psutil_net_if_addrs.return_value = mock_return.testnetz

    config = configparser.ConfigParser()
    config.read('testconfig.ini')
    ip = config.get('BasicConfigurations', 'ip')
    assert ip, 'IP-Address is not set'
    dcp = DCP(ip)
    return dcp, socket
