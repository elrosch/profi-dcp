

class TestDCPReset:

    def test_reset(self, mock_return, instance_dcp):
        instance_dcp, socket = instance_dcp
        for device_mac in mock_return.dst:
            before_family = mock_return.devices[device_mac].Family

            mock_return.dst_custom = device_mac
            socket().recv.return_value = mock_return.identify_response('RESET', xid=instance_dcp._DCP__xid + 1)
            socket().recv.return_value.append(TimeoutError)
            socket().recv.side_effect = socket().recv.return_value

            ret_msg = instance_dcp.reset_to_factory(device_mac)
            assert ret_msg.code == int(mock_return.devices[device_mac].err_code)
