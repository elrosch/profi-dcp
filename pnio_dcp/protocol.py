"""
Copyright (c) 2020 Codewerk GmbH, Karlsruhe.
All Rights Reserved.
License: MIT License see LICENSE.md in the pnio_dcp root directory.
"""
from .util import create_bytestr, hex_to_mac


# Constants for the different DCP frame IDs
DCP_FRAME_ID_GET_SET = 0xfefd
DCP_FRAME_ID_IDENTIFY_REQUEST = 0xfefe

# the multicast address for identify all requests
PROFINET_MULTICAST_MAC_IDENTIFY = '01:0e:cf:00:00:00'
# the response delay value for DCP requests
RESPONSE_DELAY = 0x0080
# DCP block qualifier to indicate that a value should be stored permanently
DCP_QUALIFIER_STORE_PERMANENT = [0x00, 0x01]
# DCP qualifier to for reset to factory with mode communication
DCP_QUALIFIER_RESET_COMMUNICATION = [0x00, 0x04]


eth_header = create_bytestr("eth_header", (
    ("destination",  ("6s", hex_to_mac)),
    ("source",       ("6s", hex_to_mac)),
    ("type",         ("H", "0x%04X"))
))
"""
Define a eth_header class using create_bytestr with the following characteristics:
- a subclass of a namedtuple with the attributes: destination, source, type, and payload
- the __new__ method takes either
    - the 3 values for destination, source, and type as args and the value for payload as kwargs
    - or a single bytes object as args which will be unpacked to an eth_header (see below for the expected format)
- a __bytes__ method to convert the eth_header to a bytes object with the following format:
    - a preamble with the struct format ">6s6sH"
    - followed by a payload of arbitrary length
    - this is also the format expected by __new__ when given only a single args
- a __len__ method the get the length
"""

dcp_header = create_bytestr("dcp_header", (
    ("frame_id",     ("H", "0x%04X")),
    ("service_id",   "B"),
    ("service_type", "B"),
    ("xid",          ("I", "0x%08X")),
    ("resp",         "H"),
    ("len",          "H")
), options={
    "ETHER_TYPE": 0x8892,
    "GET": 3,
    "SET": 4,
    "IDENTIFY": 5,
    "REQUEST": 0,
    "RESPONSE": 1
})
"""
Define a dcp_header class using create_bytestr with the following characteristics:
- a subclass of a namedtuple with the attributes: frame_id, service_id, service_type, xid, resp, len, and payload
- additional attributes ETHER_TYPE, GET, SET, IDENTIFY, REQUEST, and RESPONSE with the values as defined above.
- the __new__ method takes either
    - 6 values for frame_id, service_id, service_type, xid, resp, and len as args and the value for payload as kwargs
    - or a single bytes object as args which will be unpacked to a dcp_header (see below for the expected format)
- a __bytes__ method to convert the dcp_header to a bytes object with the following format:
    - a preamble with the struct format ">HBBIHH"
    - followed by a payload of arbitrary length
    - this is also the format expected by __new__ when given only a single args
- a __len__ method the get the length
"""

DCPBlockRequest = create_bytestr("DCPBlockRequest", (
    ("opt",    "B"),
    ("subopt", "B"),
    ("len",    "H")
), payload_field_len="len")
"""
Define a DCPBlockRequest class using create_bytestr with the following characteristics:
- a subclass of a namedtuple with the attributes: opt, subopt, len, and payload
- the __new__ method takes either
    - the 3 values for opt, subopt, and len as args and the value for payload as kwargs
    - or a single bytes object as args which will be unpacked to a DCPBlockRequest (see below for the expected format)
- a __bytes__ method to convert the DCPBlockRequest to a bytes object with the following format:
    - a preamble with the struct format ">BBH"
    - followed by a payload of length equal to the length specified by the len field
    - this is also the format expected by __new__ when given only a single args
- a __len__ method the get the length
"""


class DCPBlock(create_bytestr("DCPBlockRequest", (
    ("opt",    "B"),
    ("subopt", "B"),
    ("len",    "H"),
    ("status",    "H"),
), payload_field_len="len", offset=-2)):
    """
    The DCPBlock inherits from a class defined by create_bytestr with the following characteristics:
    - a subclass of a namedtuple with the attributes: opt, subopt, len, status, and payload
    - the __new__ method takes either
        - the 4 values for opt, subopt, len, and status as args and the value for payload as kwargs
        - or a single bytes object as args which will be unpacked to this class (see below for the expected format)
    - a __bytes__ method to convert the class to a bytes object with the following format:
        - a preamble with the struct format ">BBHH"
        - followed by a payload of length equal to the length specified by the len field - 2
        - this is also the format expected by __new__ when given only a single args
    - a __len__ method the get the length
    """
    IP_ADDRESS = (1, 2)
    DEVICE_FAMILY = (2, 1)
    NAME_OF_STATION = (2, 2)
    DEVICE_ID = (2, 3)
    RESET_TO_FACTORY = (5, 6)
    ALL = (0xFF, 0xFF)
