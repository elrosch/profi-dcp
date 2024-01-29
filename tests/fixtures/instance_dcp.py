import pytest
from profi_dcp.profi_dcp import DCP
import configparser
from unittest.mock import patch, MagicMock


@pytest.fixture(scope='function')
@patch('profi_dcp.profi_dcp.L2Socket')
@patch('profi_dcp.profi_dcp.psutil.net_if_addrs')
@patch('profi_dcp.profi_dcp.psutil.net_if_stats')
def instance_dcp(psutil_net_if_stats, psutil_net_if_addrs, socket, mock_return):
    """
    Provides a dcp instance with a mocked socket and the mocked socket.
    """
    psutil_net_if_addrs.return_value = mock_return.testnet_addrs
    psutil_net_if_stats.return_value = mock_return.testnet_stats

    config = configparser.ConfigParser()
    config.read('tests/testconfig.ini')
    ip = config.get('BasicConfigurations', 'ip')
    assert ip, 'IP-Address is not set'
    dcp = DCP(ip)
    dcp.default_timeout = 0.5
    dcp.identify_all_timeout = 0.5
    return dcp, socket
