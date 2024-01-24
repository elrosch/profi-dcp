import pytest
from pnet_dcp.error import DcpTimeoutError
from pnet_dcp.dcp_constants import ResetFactoryModes


class TestDCPReset:
    """
    Test the reset_to_factory and factory_reset functions.
    """

    @pytest.mark.parametrize("reset_mode", [None, ResetFactoryModes.RESET_COMMUNICATION, ResetFactoryModes.RESET_ENGENEERING,
                                            ResetFactoryModes.RESET_ALL_DATA, ResetFactoryModes.RESET_DEVICE,
                                            ResetFactoryModes.RESET_AND_RESTORE])
    def test_reset_to_factory(self, mock_return, instance_dcp, reset_mode):
        """
        Test reset_to_factory with response from device.
        """
        instance_dcp, socket = instance_dcp
        for device_mac in mock_return.dst:
            mock_return.dst_custom = device_mac
            socket().recv.return_value = mock_return.identify_response(
                'RESET', xid=instance_dcp._DCP__xid + 1)
            socket().recv.return_value.append(TimeoutError)
            socket().recv.side_effect = socket().recv.return_value

            # Invoke reset to factory
            if reset_mode:
                ret_msg = instance_dcp.reset_to_factory(device_mac, reset_mode)
            else:
                ret_msg = instance_dcp.reset_to_factory(device_mac)

            # Test response code
            assert ret_msg.code == int(
                mock_return.devices[device_mac].err_code)

    @pytest.mark.parametrize("reset_mode", [None, ResetFactoryModes.RESET_COMMUNICATION, ResetFactoryModes.RESET_ENGENEERING,
                                            ResetFactoryModes.RESET_ALL_DATA, ResetFactoryModes.RESET_DEVICE,
                                            ResetFactoryModes.RESET_AND_RESTORE])
    def test_reset_to_factory_raises_timeout(self, mock_return, instance_dcp, reset_mode):
        """
        Test device not responding to reset_to_factory.
        """
        instance_dcp, socket = instance_dcp
        for device_mac in mock_return.dst:
            mock_return.dst_custom = device_mac
            socket().recv.return_value = None

            # Invoke reset to factory
            with pytest.raises(DcpTimeoutError):
                if reset_mode:
                    instance_dcp.reset_to_factory(device_mac, reset_mode)
                else:
                    instance_dcp.reset_to_factory(device_mac)

    def test_factory_reset(self, mock_return, instance_dcp):
        """
        Test factory_reset with response from device.
        """
        instance_dcp, socket = instance_dcp
        for device_mac in mock_return.dst:
            mock_return.dst_custom = device_mac
            socket().recv.return_value = mock_return.identify_response(
                'RESET', xid=instance_dcp._DCP__xid + 1)
            socket().recv.return_value.append(TimeoutError)
            socket().recv.side_effect = socket().recv.return_value

            # Invoke factory reset
            ret_msg = instance_dcp.factory_reset(device_mac)
            assert ret_msg.code == int(
                mock_return.devices[device_mac].err_code)

    def test_factory_reset_raises_timeout(self, mock_return, instance_dcp):
        """
        Test device not responding to factory_reset.
        """
        instance_dcp, socket = instance_dcp
        for device_mac in mock_return.dst:
            mock_return.dst_custom = device_mac
            socket().recv.return_value = None

            # Invoke factory reset
            with pytest.raises(DcpTimeoutError):
                instance_dcp.factory_reset(device_mac)
