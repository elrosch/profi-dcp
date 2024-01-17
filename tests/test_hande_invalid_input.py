import random
import pytest
from unittest.mock import patch

import pnio_dcp


class TestInvalidInput:
    """
    Test the behavior for some invalid input.
    """

    @patch('pnio_dcp.pnio_dcp.psutil')
    def test_init_with_invalid_ip(self, psutil, mock_return):
        """
        Test the init of the dcp class with invalid ip addresses.
        """
        psutil.net_if_addrs.return_value = mock_return.testnetz

        invalid_ips = ["0.0.0.0",
                       "not an ip",
                       None,
                       5]

        for ip in invalid_ips:
            with pytest.raises(ValueError):
                pnio_dcp.DCP(ip)

    def test_provide_invalid_ip(self, mock_return, instance_dcp):
        """
        Test set_ip_address with invalid ip suits.
        """
        instance_dcp, socket = instance_dcp
        invalid_ip = [['260.0.270.31', '255.255.240.0', '10.0.0.1'],
                      ['10.0.0.30', '255..240.0', '10.0.0.1'],
                      ['10.0.0.30', '255.255.240.0', '10.0.1'],
                      ['10.0.0.30', '255.255.240.0', '-10.0.0.1']]
        test_device_mac = random.choice(mock_return.dst)
        mock_return.dst_custom = test_device_mac
        socket().recv.return_value = mock_return.identify_response('SET', xid=instance_dcp._DCP__xid + 1)
        socket().recv.return_value.append(TimeoutError)
        socket().recv.side_effect = socket().recv.return_value
        for ip_conf in invalid_ip:
            exception_occured = False
            try:
                ret_msg = instance_dcp.set_ip_address(test_device_mac, ip_conf)
            except BaseException:
                exception_occured = True
            assert exception_occured

    def test_provide_invalid_name(self, mock_return, instance_dcp):
        """
        Test set_name_of_station with invalid profinet names.
        """
        instance_dcp, socket = instance_dcp
        test_device_mac = random.choice(mock_return.dst)

        mock_return.dst_custom = test_device_mac
        socket().recv.return_value = mock_return.identify_response('SET', xid=instance_dcp._DCP__xid + 1)
        socket().recv.return_value.append(TimeoutError)
        socket().recv.side_effect = socket().recv.return_value

        names = ['name xx', 'na&/$%&me', '1name', 'name*:><', '.name']
        exception_occured = False
        for invalid_name in names:
            try:
                ret_msg = instance_dcp.set_name_of_station(test_device_mac, invalid_name)
            except BaseException:
                exception_occured = True
            assert exception_occured
