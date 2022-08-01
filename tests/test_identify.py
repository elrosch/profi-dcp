import itertools
import pytest
import pnio_dcp
from socket import timeout


class TestDCPIdentify:

    def test_identify_all_devices(self, mock_return, instance_dcp):
        instance_dcp, socket = instance_dcp

        valid_responses = mock_return.identify_response('IDENTIFY_ALL', xid=instance_dcp._DCP__xid + 1)
        recv_return_value = itertools.chain(valid_responses, itertools.cycle([TimeoutError]))
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
        instance_dcp, socket = instance_dcp
        socket().recv.side_effect = timeout

        devices = instance_dcp.identify_all()

        assert len(devices) == 0

    def test_identify_device(self, mock_return, instance_dcp):
        instance_dcp, socket = instance_dcp
        for device_mac in mock_return.dst:
            mock_return.dst_custom = device_mac
            socket().recv.return_value = mock_return.identify_response('IDENTIFY', xid=instance_dcp._DCP__xid + 1)
            socket().recv.return_value.append(TimeoutError)
            socket().recv.side_effect = socket().recv.return_value

            identified = instance_dcp.identify(device_mac)
            assert isinstance(identified, pnio_dcp.Device)
            assert identified.name_of_station == mock_return.devices[device_mac].NameOfStation
            assert identified.MAC == mock_return.devices[device_mac].MAC
            assert identified.IP == mock_return.devices[device_mac].IP
            assert identified.netmask == mock_return.devices[device_mac].Netmask
            assert identified.gateway == mock_return.devices[device_mac].Gateway
            assert identified.family == mock_return.devices[device_mac].Family

    def test_identify_device_no_response_raises_timeout(self, mock_return, instance_dcp):
        instance_dcp, socket = instance_dcp
        socket().recv.side_effect = timeout
        device_mac = mock_return.dst[0]

        with pytest.raises(pnio_dcp.DcpTimeoutError):
            instance_dcp.identify(device_mac)
