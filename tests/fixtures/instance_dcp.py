import pytest
import pnio_dcp
import configparser
from unittest.mock import patch, MagicMock


@pytest.fixture(scope='function')
@patch('pnio_dcp.pnio_dcp.L2Socket')
@patch('pnio_dcp.pnio_dcp.psutil.net_if_addrs')
def instance_dcp(psutil_net_if_addrs, socket, mock_return):

    psutil_net_if_addrs.return_value = mock_return.testnetz

    config = configparser.ConfigParser()
    config.read('testconfig.ini')
    ip = config.get('BasicConfigurations', 'ip')
    assert ip, 'IP-Address is not set'
    dcp = pnio_dcp.DCP(ip)
    return dcp, socket
