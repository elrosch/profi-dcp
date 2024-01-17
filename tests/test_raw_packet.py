import itertools
import pytest
from pnio_dcp import ResetFactoryModes
from protocol_constants import MULTICAST_PN_ADDRESS, DCPHeader, ServiceId, ServiceType, ResponseDelay, Option, SubOption, BlockQualifier, SignalValue


class TestRawPacket:
    """
    Test if raw packets are build correctly.
    """

    def test_raw_packet_identify_all(self, mock_return, instance_dcp):
        """
        Check packet for identify all is build correctly.
        """
        instance_dcp, socket = instance_dcp
        # Setup mock for call to identify all
        valid_responses = mock_return.identify_response('IDENTIFY_ALL', xid=instance_dcp._DCP__xid + 1)
        recv_return_value = itertools.chain(valid_responses, itertools.cycle([None]))
        socket().recv.return_value = recv_return_value
        socket().recv.side_effect = socket().recv.return_value

        # Invoke identify all
        instance_dcp.identify_all()

        # Check the packet was built correctly
        raw_packet = socket().send.call_args.args[0]
        assert raw_packet[0:6] == MULTICAST_PN_ADDRESS, "Destination MAC wrong"
        assert raw_packet[6:12] == mock_return.mac_address_to_bytes(mock_return.src), "Source MAC wrong"
        assert raw_packet[12:14] == DCPHeader.ETHERNET_TYPE, "Ethernet type wrong"
        assert raw_packet[14:16] == DCPHeader.FRAME_ID_IDENTIFY, "FrameID wrong"
        assert raw_packet[16:17] == ServiceId.IDENTIFY, "ServiceID wrong"
        assert raw_packet[17:18] == ServiceType.REQUEST, "ServiceType wrong"
        assert int.from_bytes(raw_packet[18:22], 'big') == instance_dcp._DCP__xid, "Xid wrong"
        assert raw_packet[22:24] == ResponseDelay.IDENTIFY, "Response delay wrong"
        assert raw_packet[24:26] == b'\x00\x04', "Length wrong"
        assert raw_packet[26:27] == Option.ALL_SELECTOR_OPTION, "Option wrong"
        assert raw_packet[27:28] == SubOption.ALL_SELECTOR, "Suboption wrong"
        assert raw_packet[28:30] == b'\x00\x00', "DCPBlockLength wrong"

        assert len(raw_packet) == 30, "Length wrong"

    def test_raw_packet_identify(self, mock_return, instance_dcp):
        """
        Check packet for identify.
        """
        instance_dcp, socket = instance_dcp
        for device_mac in mock_return.dst:
            # Setup mock for call to identify
            mock_return.dst_custom = device_mac
            socket().recv.return_value = mock_return.identify_response('IDENTIFY', xid=instance_dcp._DCP__xid + 1)
            socket().recv.return_value.append(TimeoutError)
            socket().recv.side_effect = socket().recv.return_value

            # Invoke identify
            instance_dcp.identify(device_mac)

            # Check the packet was built correctly
            raw_packet = socket().send.call_args.args[0]
            assert raw_packet[0:6] == mock_return.mac_address_to_bytes(device_mac), "Destination MAC wrong"
            assert raw_packet[6:12] == mock_return.mac_address_to_bytes(mock_return.src), "Source MAC wrong"
            assert raw_packet[12:14] == DCPHeader.ETHERNET_TYPE, "Ethernet type wrong"
            assert raw_packet[14:16] == DCPHeader.FRAME_ID_IDENTIFY, "FrameID wrong"
            assert raw_packet[16:17] == ServiceId.IDENTIFY, "ServiceID wrong"
            assert raw_packet[17:18] == ServiceType.REQUEST, "ServiceType wrong"
            assert int.from_bytes(raw_packet[18:22], 'big') == instance_dcp._DCP__xid, "Xid wrong"
            assert raw_packet[22:24] == ResponseDelay.IDENTIFY, "Response delay wrong"
            assert raw_packet[24:26] == b'\x00\x04', "Length wrong"
            assert raw_packet[26:27] == Option.ALL_SELECTOR_OPTION, "Option wrong"
            assert raw_packet[27:28] == SubOption.ALL_SELECTOR, "Suboption wrong"
            assert raw_packet[28:30] == b'\x00\x00', "DCPBlockLength wrong"

            assert len(raw_packet) == 30, "Length wrong"

    @pytest.mark.parametrize("store_permanent", [None, True, False])
    def test_raw_packet_set_ip(self, mock_return, instance_dcp, store_permanent):
        """
        Check packet for set ip address is build correctly.
        """
        instance_dcp, socket = instance_dcp
        new_ip = ['10.0.0.31', '255.255.240.0', '10.0.0.1']

        for device_mac in mock_return.dst:
            # Setup mock for call to set ip address
            mock_return.dst_custom = device_mac
            socket().recv.return_value = mock_return.identify_response('SET', xid=instance_dcp._DCP__xid + 1)
            socket().recv.return_value.append(TimeoutError)
            socket().recv.side_effect = socket().recv.return_value

            # Invoke set ip address
            if store_permanent == None:
                instance_dcp.set_ip_address(device_mac, new_ip)
            else:
                instance_dcp.set_ip_address(device_mac, new_ip, store_permanent)                

            # Check the packet was built correctly
            raw_packet = socket().send.call_args.args[0]
            assert raw_packet[0:6] == mock_return.mac_address_to_bytes(device_mac), "Destination MAC wrong"
            assert raw_packet[6:12] == mock_return.mac_address_to_bytes(mock_return.src), "Source MAC wrong"
            assert raw_packet[12:14] == DCPHeader.ETHERNET_TYPE, "Ethernet type wrong"
            assert raw_packet[14:16] == DCPHeader.FRAME_ID_GET_SET, "FrameID wrong"
            assert raw_packet[16:17] == ServiceId.SET, "ServiceID wrong"
            assert raw_packet[17:18] == ServiceType.REQUEST, "ServiceType wrong"
            assert int.from_bytes(raw_packet[18:22], 'big') == instance_dcp._DCP__xid, "Xid wrong"
            assert raw_packet[22:24] == ResponseDelay.GET_SET, "Padding wrong"
            assert raw_packet[24:26] == b'\x00\x12', "Length wrong"
            assert raw_packet[26:27] == Option.IP_OPTION, "Option wrong"
            assert raw_packet[27:28] == SubOption.IP_PARAMETER, "Suboption wrong"
            assert raw_packet[28:30] == b'\x00\x0e', "DCPBlockLength wrong"
            if store_permanent == None:
                assert raw_packet[30:32] == BlockQualifier.PERMANENT, "Block Qualifyer wrong (Must be store permanent)"
            elif store_permanent:
                assert raw_packet[30:32] == BlockQualifier.PERMANENT, "Block Qualifyer wrong (Must be store permanent)"
            else:
                assert raw_packet[30:32] == BlockQualifier.TEMPORARY, "Block Qualifyer wrong (Must be store temporary)"

            assert raw_packet[32:44] == mock_return.ip_to_hex(new_ip), "IPSuite value wrong"

            assert len(raw_packet) == 44, "Length wrong"
    
    @pytest.mark.parametrize("store_permanent", [None, True, False])        
    def test_raw_packet_set_name(self, mock_return, instance_dcp, store_permanent):
        """
        Check packet for set name of station is build correctly.
        """
        instance_dcp, socket = instance_dcp
        for idx in range(len(mock_return.dst)):
            # Setup mock for call to set name of station 
            mock_return.dst_custom = mock_return.dst[idx]
            socket().recv.return_value = mock_return.identify_response('SET', xid=instance_dcp._DCP__xid + 1)
            socket().recv.return_value.append(TimeoutError)
            socket().recv.side_effect = socket().recv.return_value

            # Generate new name and convert to bytes
            new_name = f"{mock_return.devices[mock_return.dst[idx]].NameOfStation}-{idx}"
            new_name_bytes = bytes(new_name, encoding='ascii')
            if len(new_name_bytes) % 2 == 1:
                new_name_bytes += bytes(1)

            # Invoke set name of station
            if store_permanent == None:
                instance_dcp.set_name_of_station(mock_return.dst[idx], new_name)
            else:
                instance_dcp.set_name_of_station(mock_return.dst[idx], new_name, store_permanent)

            # Check the packet was built correctly
            raw_packet = socket().send.call_args.args[0]
            assert raw_packet[0:6] == mock_return.mac_address_to_bytes(mock_return.dst[idx]), "Destination MAC wrong"
            assert raw_packet[6:12] == mock_return.mac_address_to_bytes(mock_return.src), "Source MAC wrong"
            assert raw_packet[12:14] == DCPHeader.ETHERNET_TYPE, "Ethernet type wrong"
            assert raw_packet[14:16] == DCPHeader.FRAME_ID_GET_SET, "FrameID wrong"
            assert raw_packet[16:17] == ServiceId.SET, "ServiceID wrong"
            assert raw_packet[17:18] == ServiceType.REQUEST, "ServiceType wrong"
            assert int.from_bytes(raw_packet[18:22], 'big') == instance_dcp._DCP__xid, "Xid wrong"
            assert raw_packet[22:24] == ResponseDelay.GET_SET, "Padding wrong"
            assert int.from_bytes(raw_packet[24:26], 'big') == len(new_name_bytes)+6, "Length wrong" #length with U16 alingment padding
            assert raw_packet[26:27] == Option.DEVICE_PROPERTIES_OPTION, "Option wrong"
            assert raw_packet[27:28] == SubOption.NAME_OF_STATION, "Suboption wrong"
            assert int.from_bytes(raw_packet[28:30], 'big') == len(new_name)+2, "DCPBlockLength wrong"  #length without U16 alingment padding
            if store_permanent == None:
                assert raw_packet[30:32] == BlockQualifier.PERMANENT, "Block Qualifyer wrong (Must be store permanent)"
            elif store_permanent:
                assert raw_packet[30:32] == BlockQualifier.PERMANENT, "Block Qualifyer wrong (Must be store permanent)"
            else:
                assert raw_packet[30:32] == BlockQualifier.TEMPORARY, "Block Qualifyer wrong (Must be store temporary)"
            assert raw_packet[32:] == new_name_bytes, "Device name wrong"

            assert len(raw_packet) == 32+len(new_name_bytes), "Length wrong"

    def test_raw_packet_get_ip(self, mock_return, instance_dcp):
        """
        Check packet for get ip address is build correctly.
        """
        instance_dcp, socket = instance_dcp
        for device_mac in mock_return.dst:
            # Setup mock for call to get ip address
            mock_return.dst_custom = device_mac
            socket().recv.return_value = mock_return.identify_response('GET_IP', xid=instance_dcp._DCP__xid + 1)
            socket().recv.return_value.append(TimeoutError)
            socket().recv.side_effect = socket().recv.return_value

            # Invoke get ip address
            instance_dcp.get_ip_address(device_mac)

            # Check the packet was built correctly
            raw_packet = socket().send.call_args.args[0]
            assert raw_packet[0:6] == mock_return.mac_address_to_bytes(device_mac), "Destination MAC wrong"
            assert raw_packet[6:12] == mock_return.mac_address_to_bytes(mock_return.src), "Source MAC wrong"
            assert raw_packet[12:14] == DCPHeader.ETHERNET_TYPE, "Ethernet type wrong"
            assert raw_packet[14:16] == DCPHeader.FRAME_ID_GET_SET, "FrameID wrong"
            assert raw_packet[16:17] == ServiceId.GET, "ServiceID wrong"
            assert raw_packet[17:18] == ServiceType.REQUEST, "ServiceType wrong"
            assert int.from_bytes(raw_packet[18:22], 'big') == instance_dcp._DCP__xid, "Xid wrong"
            assert raw_packet[22:24] == ResponseDelay.GET_SET, "Padding wrong"
            assert raw_packet[24:26] == b'\x00\x02', "Length wrong"
            assert raw_packet[26:27] == Option.IP_OPTION, "Option wrong"
            assert raw_packet[27:28] == SubOption.IP_PARAMETER, "Suboption wrong"

            assert len(raw_packet) == 28, "Length wrong"

    def test_raw_packet_get_name(self, mock_return, instance_dcp):
        """
        Check packet for get name of station is build correctly.
        """
        instance_dcp, socket = instance_dcp
        for device_mac in mock_return.dst:
            # Setup mock for call to get name of station
            mock_return.dst_custom = device_mac
            socket().recv.return_value = mock_return.identify_response('GET_NAME', xid=instance_dcp._DCP__xid + 1)
            socket().recv.return_value.append(TimeoutError)
            socket().recv.side_effect = socket().recv.return_value

            # Invoke get name of station
            instance_dcp.get_name_of_station(device_mac)

            # Check the packet was built correctly
            raw_packet = socket().send.call_args.args[0]
            assert raw_packet[0:6] == mock_return.mac_address_to_bytes(device_mac), "Destination MAC wrong"
            assert raw_packet[6:12] == mock_return.mac_address_to_bytes(mock_return.src), "Source MAC wrong"
            assert raw_packet[12:14] == DCPHeader.ETHERNET_TYPE, "Ethernet type wrong"
            assert raw_packet[14:16] == DCPHeader.FRAME_ID_GET_SET, "FrameID wrong"
            assert raw_packet[16:17] == ServiceId.GET, "ServiceID wrong"
            assert raw_packet[17:18] == ServiceType.REQUEST, "ServiceType wrong"
            assert int.from_bytes(raw_packet[18:22], 'big') == instance_dcp._DCP__xid, "Xid wrong"
            assert raw_packet[22:24] == ResponseDelay.GET_SET, "Padding wrong"
            assert raw_packet[24:26] == b'\x00\x02', "Length wrong"
            assert raw_packet[26:27] == Option.DEVICE_PROPERTIES_OPTION, "Option wrong"
            assert raw_packet[27:28] == SubOption.NAME_OF_STATION, "Suboption wrong"

            assert len(raw_packet) == 28, "Length wrong"

    def test_raw_packet_blink(self, mock_return, instance_dcp):
        """
        Check packet for blink is build correctly.
        """
        instance_dcp, socket = instance_dcp

        for device_mac in mock_return.dst:
            # Setup mock for call to blink
            mock_return.dst_custom = device_mac
            socket().recv.return_value = mock_return.identify_response('SET', xid=instance_dcp._DCP__xid + 1)
            socket().recv.return_value.append(TimeoutError)
            socket().recv.side_effect = socket().recv.return_value

            # Invoke blink
            instance_dcp.blink(device_mac)

            # Check the packet was built correctly
            raw_packet = socket().send.call_args.args[0]
            assert raw_packet[0:6] == mock_return.mac_address_to_bytes(device_mac), "Destination MAC wrong"
            assert raw_packet[6:12] == mock_return.mac_address_to_bytes(mock_return.src), "Source MAC wrong"
            assert raw_packet[12:14] == DCPHeader.ETHERNET_TYPE, "Ethernet type wrong"
            assert raw_packet[14:16] == DCPHeader.FRAME_ID_GET_SET, "FrameID wrong"
            assert raw_packet[16:17] == ServiceId.SET, "ServiceID wrong"
            assert raw_packet[17:18] == ServiceType.REQUEST, "ServiceType wrong"
            assert int.from_bytes(raw_packet[18:22], 'big') == instance_dcp._DCP__xid, "Xid wrong"
            assert raw_packet[22:24] == ResponseDelay.GET_SET, "Padding wrong"
            assert raw_packet[24:26] == b'\x00\x08', "Length wrong"
            assert raw_packet[26:27] == Option.CONTROL_OPTION, "Option wrong"
            assert raw_packet[27:28] == SubOption.SIGNAL, "Suboption wrong"
            assert raw_packet[28:30] == b'\x00\x04', "DCPBlockLength wrong"
            assert raw_packet[30:32] == BlockQualifier.NONE, "Block Qualifyer wrong (Must be set to all zeros)"
            assert raw_packet[32:34] == SignalValue.FLASH_ONCE, "Signal value wrong"

            assert len(raw_packet) == 34, "Length wrong"

    @pytest.mark.parametrize("reset_mode", [None, ResetFactoryModes.RESET_COMMUNICATION, ResetFactoryModes.RESET_ENGENEERING, 
                                            ResetFactoryModes.RESET_ALL_DATA, ResetFactoryModes.RESET_DEVICE,
                                            ResetFactoryModes.RESET_AND_RESTORE])
    def test_raw_reset_to_factory(self, mock_return, instance_dcp, reset_mode):
        """
        Check packet for reset to factory is build correctly.
        """
        instance_dcp, socket = instance_dcp
        for device_mac in mock_return.dst:
            # Setup mock for call to reset to factory
            mock_return.dst_custom = device_mac
            socket().recv.return_value = mock_return.identify_response('RESET', xid=instance_dcp._DCP__xid + 1)
            socket().recv.return_value.append(TimeoutError)
            socket().recv.side_effect = socket().recv.return_value

            # Invoke reset to factory
            if reset_mode:
                instance_dcp.reset_to_factory(device_mac, reset_mode)
            else:
                instance_dcp.reset_to_factory(device_mac)

            # Check the packet was built correctly
            raw_packet = socket().send.call_args.args[0]
            assert raw_packet[0:6] == mock_return.mac_address_to_bytes(device_mac), "Destination MAC wrong"
            assert raw_packet[6:12] == mock_return.mac_address_to_bytes(mock_return.src), "Source MAC wrong"
            assert raw_packet[12:14] == DCPHeader.ETHERNET_TYPE, "Ethernet type wrong"
            assert raw_packet[14:16] == DCPHeader.FRAME_ID_GET_SET, "FrameID wrong"
            assert raw_packet[16:17] == ServiceId.SET, "ServiceID wrong"
            assert raw_packet[17:18] == ServiceType.REQUEST, "ServiceType wrong"
            assert int.from_bytes(raw_packet[18:22], 'big') == instance_dcp._DCP__xid, "Xid wrong"
            assert raw_packet[22:24] == ResponseDelay.GET_SET, "Padding wrong"
            assert raw_packet[24:26] == b'\x00\x06', "Length wrong"
            assert raw_packet[26:27] == Option.CONTROL_OPTION, "Option wrong"
            assert raw_packet[27:28] == SubOption.RESET_TO_FACTORY, "Suboption wrong"
            assert raw_packet[28:30] == b'\x00\x02', "DCPBlockLength wrong"
            if reset_mode == None:
                assert raw_packet[30:32] == BlockQualifier.RESET_COMMUNICATION, "Block Qualifyer wrong"
            elif reset_mode == ResetFactoryModes.RESET_COMMUNICATION:
                assert raw_packet[30:32] == BlockQualifier.RESET_COMMUNICATION, "Block Qualifyer wrong"
            elif reset_mode == ResetFactoryModes.RESET_ENGENEERING:
                assert raw_packet[30:32] == BlockQualifier.RESET_ENGENEERING, "Block Qualifyer wrong"
            elif reset_mode == ResetFactoryModes.RESET_ALL_DATA:
                assert raw_packet[30:32] == BlockQualifier.RESET_ALL_DATA, "Block Qualifyer wrong"
            elif reset_mode == ResetFactoryModes.RESET_DEVICE:
                assert raw_packet[30:32] == BlockQualifier.RESET_DEVICE, "Block Qualifyer wrong"
            elif reset_mode == ResetFactoryModes.RESET_AND_RESTORE:
                assert raw_packet[30:32] == BlockQualifier.RESET_AND_RESTORE, "Block Qualifyer wrong"

            assert len(raw_packet) == 32, "Length wrong"

    def test_raw_factory_reset(self, mock_return, instance_dcp):
        """
        Check packet for factory reset is build correctly.
        """
        instance_dcp, socket = instance_dcp
        for device_mac in mock_return.dst:
            # Setup mock for call to factory reset
            mock_return.dst_custom = device_mac
            socket().recv.return_value = mock_return.identify_response('RESET', xid=instance_dcp._DCP__xid + 1)
            socket().recv.return_value.append(TimeoutError)
            socket().recv.side_effect = socket().recv.return_value

            # Invoke factory reset
            instance_dcp.factory_reset(device_mac)

            # Check the packet was built correctly
            raw_packet = socket().send.call_args.args[0]
            assert raw_packet[0:6] == mock_return.mac_address_to_bytes(device_mac), "Destination MAC wrong"
            assert raw_packet[6:12] == mock_return.mac_address_to_bytes(mock_return.src), "Source MAC wrong"
            assert raw_packet[12:14] == DCPHeader.ETHERNET_TYPE, "Ethernet type wrong"
            assert raw_packet[14:16] == DCPHeader.FRAME_ID_GET_SET, "FrameID wrong"
            assert raw_packet[16:17] == ServiceId.SET, "ServiceID wrong"
            assert raw_packet[17:18] == ServiceType.REQUEST, "ServiceType wrong"
            assert int.from_bytes(raw_packet[18:22], 'big') == instance_dcp._DCP__xid, "Xid wrong"
            assert raw_packet[22:24] == ResponseDelay.GET_SET, "Padding wrong"
            assert raw_packet[24:26] == b'\x00\x06', "Length wrong"
            assert raw_packet[26:27] == Option.CONTROL_OPTION, "Option wrong"
            assert raw_packet[27:28] == SubOption.FACTORY_RESET, "Suboption wrong"
            assert raw_packet[28:30] == b'\x00\x02', "DCPBlockLength wrong"

            assert len(raw_packet) == 32, "Length wrong"
