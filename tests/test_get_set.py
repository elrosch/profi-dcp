import pytest
from socket import timeout
from mock_return import MockReturn
from pnio_dcp import DcpTimeoutError


class TestDCPGetSet:
    mock = MockReturn()

    def test_get_ip(self, instance_dcp):
        instance_dcp, socket = instance_dcp
        for device_mac in self.mock.dst:

            self.mock.dst_custom = device_mac
            socket().recv.return_value = self.mock.identify_response('GET_IP', xid=instance_dcp._DCP__xid + 1)
            socket().recv.return_value.append(TimeoutError)
            socket().recv.side_effect = socket().recv.return_value

            ip = instance_dcp.get_ip_address(device_mac)
            assert ip == self.mock.devices[device_mac].IP

    def test_get_ip_no_response(self, instance_dcp):
        instance_dcp, socket = instance_dcp
        device_mac = self.mock.dst[0]
        self.mock.dst_custom = device_mac
        socket().recv.side_effect = timeout

        with pytest.raises(DcpTimeoutError):
            instance_dcp.get_ip_address(device_mac)

    def test_get_name(self, instance_dcp):
        instance_dcp, socket = instance_dcp
        for device_mac in self.mock.dst:

            self.mock.dst_custom = device_mac
            socket().recv.return_value = self.mock.identify_response('GET_NAME', xid=instance_dcp._DCP__xid + 1)
            socket().recv.return_value.append(TimeoutError)
            socket().recv.side_effect = socket().recv.return_value

            name = instance_dcp.get_name_of_station(device_mac)
            assert name == self.mock.devices[device_mac].NameOfStation

    def test_get_name_no_response_raises_timeout(self, instance_dcp):
        instance_dcp, socket = instance_dcp
        device_mac = self.mock.dst[0]
        self.mock.dst_custom = device_mac
        socket().recv.side_effect = timeout

        with pytest.raises(DcpTimeoutError):
            instance_dcp.get_name_of_station(device_mac)

    def test_set_ip(self, instance_dcp):
        instance_dcp, socket = instance_dcp
        new_ip = ['10.0.0.31', '255.255.240.0', '10.0.0.1']
        for device_mac in self.mock.dst:

            self.mock.dst_custom = device_mac
            socket().recv.return_value = self.mock.identify_response('SET', xid=instance_dcp._DCP__xid + 1)
            socket().recv.return_value.append(TimeoutError)
            socket().recv.side_effect = socket().recv.return_value

            ret_msg = instance_dcp.set_ip_address(device_mac, new_ip)
            assert ret_msg.code == int(self.mock.devices[device_mac].err_code)

    def test_set_ip_no_response_raises_timeout(self, instance_dcp):
        instance_dcp, socket = instance_dcp
        device_mac = self.mock.dst[0]
        self.mock.dst_custom = device_mac
        socket().recv.side_effect = timeout

        with pytest.raises(DcpTimeoutError):
            instance_dcp.set_ip_address(device_mac, ['127.0.0.1', '255.255.255.0', '0.0.0.0'])

    def test_set_name(self, instance_dcp):
        instance_dcp, socket = instance_dcp
        for idx in range(len(self.mock.dst)):

            self.mock.dst_custom = self.mock.dst[idx]
            socket().recv.return_value = self.mock.identify_response('SET', xid=instance_dcp._DCP__xid + 1)
            socket().recv.return_value.append(TimeoutError)
            socket().recv.side_effect = socket().recv.return_value

            new_name = 'name-{}'.format(idx)
            ret_msg = instance_dcp.set_name_of_station(self.mock.dst[idx], new_name)
            assert ret_msg.code == int(self.mock.devices[self.mock.dst[idx]].err_code)

    def test_set_name_no_response_raises_timeout(self, instance_dcp):
        instance_dcp, socket = instance_dcp
        device_mac = self.mock.dst[0]
        self.mock.dst_custom = device_mac
        socket().recv.side_effect = timeout

        with pytest.raises(DcpTimeoutError):
            instance_dcp.set_name_of_station(device_mac, 'test-name-of-station')
