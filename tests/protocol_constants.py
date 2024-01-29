

MULTICAST_PN_ADDRESS = b'\x01\x0E\xCF\x00\x00\x00'


class DCPHeader:
    ETHERNET_TYPE = b'\x88\x92'
    FRAME_ID_GET_SET = b'\xfe\xfd'
    FRAME_ID_IDENTIFY = b'\xfe\xfe'


class ServiceId:
    GET = b'\x03'
    SET = b'\x04'
    IDENTIFY = b'\x05'


class ServiceType:
    REQUEST = b'\x00'


class ResponseDelay:
    GET_SET = b'\x00\x00'
    IDENTIFY = b'\x00\x80'  # Note this is custom defined in profi_dcp/dcp_constants.py


class Option:
    IP_OPTION = b'\x01'
    DEVICE_PROPERTIES_OPTION = b'\x02'
    CONTROL_OPTION = b'\x05'
    ALL_SELECTOR_OPTION = b'\xFF'


class SubOption:
    NAME_OF_STATION = b'\x02'
    IP_PARAMETER = b'\x02'
    SIGNAL = b'\x03'
    FACTORY_RESET = b'\x05'
    RESET_TO_FACTORY = b'\x06'
    ALL_SELECTOR = b'\xFF'


class BlockQualifier:
    TEMPORARY = b'\x00\x00'
    NONE = b'\x00\x00'
    PERMANENT = b'\x00\x01'
    RESET_APPLICATION_DATA = b'\x00\x02'
    RESET_COMMUNICATION = b'\x00\x04'
    RESET_ENGENEERING = b'\x00\x06'
    RESET_ALL_DATA = b'\x00\x08'
    RESET_DEVICE = b'\x00\x10'
    RESET_AND_RESTORE = b'\x00\x12'


class SignalValue:
    FLASH_ONCE = b'\x01\x00'
