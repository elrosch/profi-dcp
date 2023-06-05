"""
Copyright (c) 2020 Codewerk GmbH, Karlsruhe.
All Rights Reserved.
License: MIT License see LICENSE.md in the pnio_dcp root directory.
"""

# the multicast address for identify all requests
PROFINET_MULTICAST_MAC_IDENTIFY = '01:0e:cf:00:00:00'
# the response delay value for DCP requests
RESPONSE_DELAY = 0x0080
# Ether type of DCP packets
ETHER_TYPE = 0x8892
# Value for letting the LED blink
LED_BLINK_VALUE = [0x01, 0x00]


class FrameID:
    """Constants for the different DCP frame IDs"""
    GET_SET = 0xfefd
    IDENTIFY_REQUEST = 0xfefe


class BlockQualifier:
    """"DCP block qualifiers"""
    # Indicate that a value should be stored permanently
    STORE_PERMANENT = [0x00, 0x01]
    # Reset to factory with mode communication
    RESET_COMMUNICATION = [0x00, 0x04]
    # Used for ControlOption with Suboption other than SuboptionResetToFactory (eg. when flashing LED)
    RESERVED = [0x00, 0x00]


class ServiceType:
    """Service type of a DCP packet"""
    REQUEST = 0
    RESPONSE = 1


class ServiceID:
    """Service ID of a DCP packet"""
    GET = 3
    SET = 4
    IDENTIFY = 5


class Option:
    """Option and suboption pairs for DCP blocks."""
    IP_ADDRESS = (1, 2)
    DEVICE_FAMILY = (2, 1)
    NAME_OF_STATION = (2, 2)
    DEVICE_ID = (2, 3)
    BLINK_LED = (5, 3)
    RESET_TO_FACTORY = (5, 6)
    ALL = (0xFF, 0xFF)
