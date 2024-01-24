import pytest
from profinet_dcp.error import DcpTimeoutError


class TestLEDBlink:
    """
    Test the LED blink DCP-Request. When this request is sent, a device should blink or flash it's LED(s).
    """

    def test_blink(self, mock_return, instance_dcp):
        """
        Test behaviour if the device answers the request.
        """
        instance_dcp, socket = instance_dcp

        for device_mac in mock_return.dst:
            mock_return.dst_custom = device_mac
            socket().recv.return_value = mock_return.identify_response(
                'SET', xid=instance_dcp._DCP__xid + 1)
            socket().recv.return_value.append(TimeoutError)
            socket().recv.side_effect = socket().recv.return_value

            ret_msg = instance_dcp.blink(device_mac)
            assert ret_msg.code == int(
                mock_return.devices[device_mac].err_code)

    def test_blink_no_response_raises_timeout(self, mock_return, instance_dcp):
        """
        Test behaviour if the device does not answer the request.
        (A DcpTimeoutError is expected)
        """
        instance_dcp, socket = instance_dcp
        device_mac = mock_return.dst[0]
        mock_return.dst_custom = device_mac
        socket().recv.return_value = None

        with pytest.raises(DcpTimeoutError):
            instance_dcp.blink(device_mac)
