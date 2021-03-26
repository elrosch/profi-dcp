import pytest
from mock_return import MockReturn


class TestDCPReset:
    mock = MockReturn()

    def test_reset(self, instance_dcp):
        instance_dcp, socket = instance_dcp
        for device_mac in self.mock.dst:
            before_family = self.mock.devices[device_mac].Family

            self.mock.dst_custom = device_mac
            socket().recv.return_value = self.mock.identify_response('RESET', xid=instance_dcp._DCP__xid + 1)
            socket().recv.return_value.append(TimeoutError)
            socket().recv.side_effect = socket().recv.return_value

            ret_msg = instance_dcp.reset_to_factory(device_mac)
            assert ret_msg.code == int(self.mock.devices[device_mac].err_code)
