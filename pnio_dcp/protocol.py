"""
Copyright (c) 2020 Codewerk GmbH, Karlsruhe.
All Rights Reserved.
License: MIT License see LICENSE.md in the pnio_dcp root directory.
"""
import struct
from pnio_dcp import util, dcp_constants
import logging

logger = logging.getLogger(__name__)


class HeaderField:
    """Used to describe a header field in a packet header."""

    def __init__(self, name, field_format, default_value=None, pack_function=None, unpack_function=None):
        """
        Defines a field in a packet header. At least a name and format must be provided. Optionally, a default value
        can be given or additional pack and unpack functions to apply before/after packing/unpacking a value.
        :param name: The name of the header field.
        :type name: string
        :param field_format: The struct format for values stored in this field.
        :type field_format: string
        :param default_value: A default value to use for this header field when no other value is given.
        :type default_value: Optional[Any]
        :param pack_function: An additional function applied to the field's value before packing.
        :type pack_function: Optional[Any -> Any]
        :param unpack_function: An additional function applied after unpacking a value. Should be inverse to
        pack_function. An example would be converting mac addresses to binary with the pack_function and reverting them
        to string with the unpack_function.
        :type unpack_function: Optional[Any -> Any]
        """
        self.name = name
        self.field_format = field_format
        self.default_value = default_value
        self.pack_function = pack_function
        self.unpack_function = unpack_function

    def pack(self, value):
        """
        Pack the given value using the pack_function (if defined).
        When the given value is None, the default value is used.
        :param value: The value to pack.
        :type value: Any
        :return: The packed value.
        :rtype: Any
        """
        if value is None:
            value = self.default_value
        if self.pack_function is not None:
            value = self.pack_function(value)
        return value

    def unpack(self, value):
        """
        Unpack the given value using the unpack_function (if defined).
        :param value: The packed value.
        :type value: Any
        :return: The unpacked value.
        :rtype: Any
        """
        if self.unpack_function is not None:
            value = self.unpack_function(value)
        return value


class Packet:
    """Base class to represent packets and pack/unpack them."""

    # Defines all fields in the packet header in the correct order.
    # Each field is defined through a HeaderField object defined above.
    HEADER_FIELD_FORMATS = []

    def __init__(self, data=None, payload=None, **kwargs):
        """
        Create a new packet. If data is given, the packets is initialized by unpacking the data. Otherwise, the payload
        and header fields are initialized from the remaining arguments.
        :param data: A packed packet as expected by unpack.
        :type data: bytes
        :param payload: The payload of the packet.
        :type payload: Any
        :param kwargs: Can be used to initialize the header fields defined in HEADER_FIELD_FORMATS
        :type kwargs: Any
        """
        self.header_format = ">" + "".join([field.field_format for field in self.HEADER_FIELD_FORMATS])
        self.header_length = struct.calcsize(self.header_format)

        self.payload = 0

        if data:
            self.unpack(data)
        else:
            valid_header_fields = [field.name for field in self.HEADER_FIELD_FORMATS]
            invalid_kwargs = [name for name in kwargs.keys() if name not in valid_header_fields]
            if invalid_kwargs:
                logger.warning(f"Invalid kwargs passed to Packet for keys: {invalid_kwargs}")

            for name, value in kwargs.items():
                if name in valid_header_fields:
                    setattr(self, name, value)

            if payload:
                self.payload = payload

    def unpack(self, data):
        """
        Unpack the packet from the given data.
        :param data: The packet packed to a bytes object i.e. by Packet.pack()
        :type data: bytes
        """
        unpacked_header = struct.unpack(self.header_format, data[:self.header_length])
        for field, value in zip(self.HEADER_FIELD_FORMATS, unpacked_header):
            setattr(self, field.name, field.unpack(value))

        self.unpack_payload(data)

    def unpack_payload(self, data):
        """
        Unpack the payload from the data after the header has already been unpacked.
        :param data: The whole packet as bytes.
        :type data: bytes
        """
        self.payload = data[self.header_length:]

    def pack(self):
        """
        Pack this packet into a bytes object containing the header and the optional payload.
        The header fields are packed according to the format defined by 'preamble'.
        If there is a payload, it is converted to bytes and appended to the packed fields.
        :return: This packet converted to a bytes object.
        :rtype: bytes
        """
        ordered_header_fields = [field.pack(getattr(self, field.name, None))
                                 for field in self.HEADER_FIELD_FORMATS]
        packed = struct.pack(self.header_format, *ordered_header_fields)
        packed += bytes(self.payload)
        return packed

    def __bytes__(self):
        """
        Pack this packet into a bytes object using the pack function.
        :return: This packet as bytes object.
        :rtype: bytes
        """
        return self.pack()

    def __len__(self):
        """
        Compute and return the length of the packet.
        That is the size of the preamble + the length of the payload (if there is a payload).
        :return: The length of the packet.
        :rtype: int
        """
        payload_length = len(bytes(self.payload))
        return self.header_length + payload_length


class EthernetPacket(Packet):
    """An Ethernet packet consisting of destination and source mac address and an ether type."""
    HEADER_FIELD_FORMATS = [
        HeaderField("destination", "6s", None, util.mac_address_to_bytes, util.mac_address_to_string),
        HeaderField("source", "6s", None, util.mac_address_to_bytes, util.mac_address_to_string),
        HeaderField("ether_type", "H"),
    ]

    def __init__(self, destination=None, source=None, ether_type=None, payload=None, data=None):
        """
        Create a new ethernet packet. If data is given, the packets is initialized by unpacking the data. Otherwise,
        the payload and header fields are initialized from the remaining arguments.
        :param destination: The mac address of the destination to send to (as ':' separated string).
        :type destination: string
        :param source: The mac address of source (as ':' separated string).
        :type source: string
        :param ether_type: The ethernet type (i.e. protocol ID).
        :type ether_type: int
        :param payload: The payload of the packet.
        :type payload: Any
        :param data: A packed ethernet packet.
        :type data: bytes
        """
        self.destination = None
        self.source = None
        self.ether_type = None
        if data:
            super().__init__(data=data)
        else:
            super().__init__(destination=destination, source=source, ether_type=ether_type, payload=payload)


class DCPPacket(Packet):
    """A DCP packet"""
    HEADER_FIELD_FORMATS = [
        HeaderField("frame_id", "H"),
        HeaderField("service_id", "B"),
        HeaderField("service_type", "B"),
        HeaderField("xid", "I"),
        HeaderField("response_delay", "H"),
        HeaderField("length", "H"),
    ]

    def __init__(self, frame_id=None, service_id=None, service_type=None, xid=None,
                 response_delay=0, length=None, payload=0, data=None):
        """
        Create a new DCP packet. If data is given, the packets is initialized by unpacking the data. Otherwise, the
        payload and header fields are initialized from the remaining arguments.
        :param frame_id: The DCP frame ID.
        :type frame_id: int
        :param service_id: The DCP service ID.
        :type service_id: int
        :param service_type: The DCP service type.
        :type service_type: int
        :param xid: The xid, used to identify the transaction.
        :type xid: int
        :param response_delay: The response delay, default is 0, should be set only for multi-cast requests like identify all.
        :type response_delay: int
        :param length: The length of the DCP data in the payload. Computed automatically from the provided payload if
        not specified.
        :type length: int
        :param payload: The payload of the packet.
        :type payload: Any
        :param data: A DCP packet as expected to be unpacked.
        :type data: bytes
        """
        self.frame_id = None
        self.service_id = None
        self.service_type = None
        self.xid = None
        self.response_delay = None
        self.length = None
        if data:
            super().__init__(data=data)
        else:
            length = len(payload) if length is None else length
            super().__init__(frame_id=frame_id, service_id=service_id, service_type=service_type, xid=xid,
                             response_delay=response_delay, length=length, payload=payload)

    def unpack_payload(self, data):
        """
        Unpack the payload of length self.len from the data after the header has already been unpacked.
        :param data: The whole packet as bytes.
        :type data: bytes
        """
        payload_end = self.header_length + self.length
        self.payload = data[self.header_length:payload_end]


class DCPBlockRequest(Packet):
    """A DCP block packet for a DCP request."""
    HEADER_FIELD_FORMATS = [
        HeaderField("opt", "B"),
        HeaderField("subopt", "B"),
        HeaderField("length", "H"),
    ]

    def __init__(self, opt=None, subopt=None, length=None, payload=0, data=None):
        """
        Create a new DCP block request packet. If data is given, the packets is initialized by unpacking the data.
        Otherwise, the payload and header fields are initialized from the remaining arguments.
        :param opt: The DCP option.
        :type opt: int
        :param subopt: The DCP sub-option.
        :type subopt: int
        :param length: The length of the payload.
        :type length: int
        :param payload: The payload of the packet. If the payload has uneven length, it will automatically padded with
        zeros to even length.
        :type payload: Any
        :param data: A DCP packet as expected to be unpacked.
        :type data: bytes
        """
        self.opt = None
        self.subopt = None
        self.length = None
        if data:
            super().__init__(data=data)
        else:
            length = len(payload) if length is None else length
            if length % 2:  # if the payload has odd length, add one byte padding at the end
                payload += bytes([0x00])
            super().__init__(opt=opt, subopt=subopt, length=length, payload=payload)

    def unpack_payload(self, data):
        """
        Unpack the payload of length self.len from the data after the header has already been unpacked.
        :param data: The whole packet as bytes.
        :type data: bytes
        """
        payload_end = self.header_length + self.length
        self.payload = data[self.header_length:payload_end]


class DCPBlock(Packet):
    """A DCP block packet."""
    HEADER_FIELD_FORMATS = [
        HeaderField("opt", "B"),
        HeaderField("subopt", "B"),
        HeaderField("length", "H"),
        HeaderField("status", "H"),
    ]

    def __init__(self, opt=None, subopt=None, length=None, status=None, payload=0, data=None):
        """
        Create a new DCP block packet. If data is given, the packets is initialized by unpacking the data. Otherwise,
        the payload and header fields are initialized from the remaining arguments.
        :param opt: The DCP option.
        :type opt: int
        :param subopt: The DCP sub-option.
        :type subopt: int
        :param length: The length of the payload.
        :type length: int
        :param status: The block status
        :type status: int
        :param payload: The payload of the packet.
        :type payload: Any
        :param data: A DCP packet as expected to be unpacked.
        :type data: bytes
        """
        self.opt = None
        self.subopt = None
        self.length = None
        self.status = None
        if data:
            super().__init__(data=data)
        else:
            length = len(payload) if length is None else length
            super().__init__(opt=opt, subopt=subopt, length=length, status=status, payload=payload)

    def unpack_payload(self, data):
        """
        Unpack the payload of length self.length - 2 from the data after the header has already been unpacked.
        :param data: The whole packet as bytes.
        :type data: bytes
        """
        payload_end = self.header_length + self.length - 2
        self.payload = data[self.header_length:payload_end]
