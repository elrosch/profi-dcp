import pytest
from pnio_dcp import DcpTimeoutError


class TestDCPGetSet:
    """
    Test the get and set functions of the library.
    """

    def test_get_ip(self, instance_dcp, mock_return):
        """
        Test get_ip_address.
        """
        instance_dcp, socket = instance_dcp
        for device_mac in mock_return.dst:

            mock_return.dst_custom = device_mac
            socket().recv.return_value = mock_return.identify_response('GET_IP', xid=instance_dcp._DCP__xid + 1)
            socket().recv.return_value.append(TimeoutError)
            socket().recv.side_effect = socket().recv.return_value

            ip = instance_dcp.get_ip_address(device_mac)
            assert ip == mock_return.devices[device_mac].IP

    def test_get_ip_no_response(self, mock_return, instance_dcp):
        """
        Test device not responding to get ip address.
        """
        instance_dcp, socket = instance_dcp
        device_mac = mock_return.dst[0]
        mock_return.dst_custom = device_mac
        socket().recv.return_value = None

        with pytest.raises(DcpTimeoutError):
            instance_dcp.get_ip_address(device_mac)

    def test_get_name(self, mock_return, instance_dcp):
        """
        Test get_name_of_station.
        """
        instance_dcp, socket = instance_dcp
        for device_mac in mock_return.dst:

            mock_return.dst_custom = device_mac
            socket().recv.return_value = mock_return.identify_response('GET_NAME', xid=instance_dcp._DCP__xid + 1)
            socket().recv.return_value.append(TimeoutError)
            socket().recv.side_effect = socket().recv.return_value

            name = instance_dcp.get_name_of_station(device_mac)
            assert name == mock_return.devices[device_mac].NameOfStation

    def test_get_name_no_response_raises_timeout(self, mock_return, instance_dcp):
        """
        Test device not reponding to get name.
        """
        instance_dcp, socket = instance_dcp
        device_mac = mock_return.dst[0]
        mock_return.dst_custom = device_mac
        socket().recv.return_value = None

        with pytest.raises(DcpTimeoutError):
            instance_dcp.get_name_of_station(device_mac)

    @pytest.mark.parametrize("store_permanent", [None, True, False])
    def test_set_ip(self, mock_return, instance_dcp, store_permanent):
        """
        Test set_ip_address.
        """
        instance_dcp, socket = instance_dcp
        new_ip = ['10.0.0.31', '255.255.240.0', '10.0.0.1']
        for device_mac in mock_return.dst:

            mock_return.dst_custom = device_mac
            socket().recv.return_value = mock_return.identify_response('SET', xid=instance_dcp._DCP__xid + 1)
            socket().recv.return_value.append(TimeoutError)
            socket().recv.side_effect = socket().recv.return_value

            if store_permanent == None:
                ret_msg = instance_dcp.set_ip_address(device_mac, new_ip)
            else:
                ret_msg = instance_dcp.set_ip_address(device_mac, new_ip, store_permanent)

            assert ret_msg.code == int(mock_return.devices[device_mac].err_code)

    @pytest.mark.parametrize("store_permanent", [None, True, False])
    def test_set_ip_no_response_raises_timeout(self, mock_return, instance_dcp, store_permanent):
        """
        Test device not responding to set ip address.
        """
        instance_dcp, socket = instance_dcp
        device_mac = mock_return.dst[0]
        mock_return.dst_custom = device_mac
        socket().recv.return_value = None

        new_ip = ['127.0.0.1', '255.255.255.0', '0.0.0.0']
        with pytest.raises(DcpTimeoutError):
            if store_permanent == None:
                instance_dcp.set_ip_address(device_mac, new_ip)
            else:
                instance_dcp.set_ip_address(device_mac, new_ip, store_permanent)

    @pytest.mark.parametrize("store_permanent", [None, True, False])
    def test_set_name(self, mock_return, instance_dcp, store_permanent):
        """
        Test set_name_of_station.
        """
        instance_dcp, socket = instance_dcp
        for idx in range(len(mock_return.dst)):

            mock_return.dst_custom = mock_return.dst[idx]
            socket().recv.return_value = mock_return.identify_response('SET', xid=instance_dcp._DCP__xid + 1)
            socket().recv.return_value.append(TimeoutError)
            socket().recv.side_effect = socket().recv.return_value

            new_name = 'name-{}'.format(idx)
            if store_permanent == None:
                ret_msg = instance_dcp.set_name_of_station(mock_return.dst[idx], new_name)
            else:
                ret_msg = instance_dcp.set_name_of_station(mock_return.dst[idx], new_name, store_permanent)
                
            assert ret_msg.code == int(mock_return.devices[mock_return.dst[idx]].err_code)

    @pytest.mark.parametrize("store_permanent", [None, True, False])
    def test_set_name_no_response_raises_timeout(self, mock_return, instance_dcp, store_permanent):
        """
        Test device not responding to set name of station.
        """
        instance_dcp, socket = instance_dcp
        device_mac = mock_return.dst[0]
        mock_return.dst_custom = device_mac
        socket().recv.return_value = None

        new_name = 'test-name-of-station'
        with pytest.raises(DcpTimeoutError):
            if store_permanent == None:
                instance_dcp.set_name_of_station(device_mac, new_name)
            else:
                instance_dcp.set_name_of_station(device_mac, new_name, store_permanent)
