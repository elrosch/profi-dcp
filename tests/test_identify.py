import itertools
import pytest
from pnet_dcp.pnet_dcp import DcpTimeoutError, Device
from socket import timeout


class TestDCPIdentify:
    """
    Test the identify and identify_all functions of the lib.
    """

    def test_identify_all_devices(self, mock_return, instance_dcp):
        """
        Test identify_all with respone from device.
        """
        instance_dcp, socket = instance_dcp

        valid_responses = mock_return.identify_response(
            'IDENTIFY_ALL', xid=instance_dcp._DCP__xid + 1)
        recv_return_value = itertools.chain(
            valid_responses, itertools.cycle([None]))
        socket().recv.return_value = recv_return_value
        socket().recv.side_effect = socket().recv.return_value

        devices = instance_dcp.identify_all()
        macs_identified = []
        assert devices
        for device in devices:
            macs_identified.append(device.MAC)

            assert device.name_of_station == mock_return.devices[device.MAC].NameOfStation
            assert device.MAC == mock_return.devices[device.MAC].MAC
            assert device.IP == mock_return.devices[device.MAC].IP
            assert device.netmask == mock_return.devices[device.MAC].Netmask
            assert device.gateway == mock_return.devices[device.MAC].Gateway
            assert device.family == mock_return.devices[device.MAC].Family

        assert macs_identified == mock_return.dst

    def test_identify_all_devices_no_responses_returns_empty_list(self, instance_dcp):
        """
        Test no devices responding to identify_all.
        """
        instance_dcp, socket = instance_dcp
        socket().recv.return_value = None

        devices = instance_dcp.identify_all()

        assert len(devices) == 0

    def test_identify_device(self, mock_return, instance_dcp):
        """
        Test identify with response from device.
        """
        instance_dcp, socket = instance_dcp
        for device_mac in mock_return.dst:
            mock_return.dst_custom = device_mac
            socket().recv.return_value = mock_return.identify_response(
                'IDENTIFY', xid=instance_dcp._DCP__xid + 1)
            socket().recv.return_value.append(TimeoutError)
            socket().recv.side_effect = socket().recv.return_value

            identified = instance_dcp.identify(device_mac)
            assert isinstance(identified, Device)
            assert identified.name_of_station == mock_return.devices[device_mac].NameOfStation
            assert identified.MAC == mock_return.devices[device_mac].MAC
            assert identified.IP == mock_return.devices[device_mac].IP
            assert identified.netmask == mock_return.devices[device_mac].Netmask
            assert identified.gateway == mock_return.devices[device_mac].Gateway
            assert identified.family == mock_return.devices[device_mac].Family

    def test_identify_device_no_response_raises_timeout(self, mock_return, instance_dcp):
        """
        Test no response from device to identify
        """
        instance_dcp, socket = instance_dcp
        socket().recv.return_value = None
        device_mac = mock_return.dst[0]

        with pytest.raises(DcpTimeoutError):
            instance_dcp.identify(device_mac)
