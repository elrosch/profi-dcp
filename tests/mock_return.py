import binascii
import random
import pnio_dcp.protocol
import pnio_dcp.util


class MockDevice:
    def __init__(self, name, mac, ip_conf, err_code, family):
        self.NameOfStation = name
        self.MAC = mac
        self.ip_conf = ip_conf
        self.IP = ip_conf[0]
        self.Netmask = ip_conf[1]
        self.Gateway = ip_conf[2]
        self.Family = family

        self.err_code = err_code


class MockReturn:
    testnetz = {'Testnetz': [{'family': -1, 1: '00-50-56-AC-DD-2E', 'netmask': None, 'broadcast': None, 'ptp': None},
                             {'family': 2, 1: '10.0.2.124', 'netmask': '255.255.240.0', 'broadcast': None, 'ptp': None}]}
    src = '00:50:56:ac:dd:2e'
    dst = ['00:0c:29:66:47:a5', '00:0e:8c:e5:3c:58', '00:e0:7c:c8:72:58', '40:ec:f8:04:bf:5e', '40:ec:f8:03:b7:df']
    dst_custom = '01:0e:cf:00:00:00'
    eth_type = 0x8892
    frame_id = None
    service_id = None
    service_type = pnio_dcp.protocol.dcp_header.RESPONSE
    devices = {'00:0c:29:66:47:a5': MockDevice('win-4faufud472v', '00:0c:29:66:47:a5', ['10.0.0.251', '255.255.240.0', '10.0.0.1'], b'00', "Win"),
               '00:0e:8c:e5:3c:58': MockDevice('spsw-11', '00:0e:8c:e5:3c:58', ['10.0.0.30', '255.255.240.0', '10.0.0.1'], random.choice([b'01', b'02', b'03']), "SPSW"),
               '00:e0:7c:c8:72:58': MockDevice('cwl-r90g66zd', '00:e0:7c:c8:72:58', ['10.0.4.53', '255.255.240.0', '10.0.0.1'], b'00', "CWL"),
               '40:ec:f8:04:bf:5e': MockDevice('sibasxx', '40:ec:f8:04:bf:5e', ['10.0.0.120', '255.255.240.0', '10.0.0.1'], random.choice([b'03', b'04', b'05']), "Sibas PN"),
               '40:ec:f8:03:b7:df': MockDevice('cp1604-11', '40:ec:f8:03:b7:df', ['10.0.0.20', '255.255.240.0', '10.0.0.1'], random.choice([b'04', b'05', b'06']), "CP16")}
    block = None
    xid = 0x7010052

    def ip_to_hex(self, ip_conf):
        str_hex = ''
        for param in ip_conf:
            nums = list(param.split('.'))
            for i in nums:
                str_hex += hex(int(i))[2:].zfill(2)
        return bytes.fromhex(str_hex)

    def identify_response(self, resp_type, xid=0x7010052):
        self.xid = xid

        if resp_type == 'IDENTIFY_ALL':
            identified = []
            for addr in self.dst:
                self.dst_custom = addr
                identified.extend(self.generate_identify())
            return identified
        if resp_type == 'IDENTIFY':
            return self.generate_identify()
        if resp_type.startswith('GET_'):
            if resp_type == 'GET_IP':
                return self.generate_get('IP')
            elif resp_type == 'GET_NAME':
                return self.generate_get('NAME')
        if resp_type == 'SET':
            return self.generate_set()
        if resp_type == 'RESET':
            return self.generate_reset()

    def generate_identify(self):
        self.frame_id = 0xfeff
        self.service_id = pnio_dcp.protocol.dcp_header.IDENTIFY
        if len(self.devices[self.dst_custom].NameOfStation) % 2 == 1:
            name = bytes([0x00, 0x00]) + bytes(self.devices[self.dst_custom].NameOfStation, encoding='ascii') + bytes([0x00])
            len_name = bytes.fromhex(format(len(name) - 1, '04x'))
        else:
            name = bytes([0x00, 0x00]) + bytes(self.devices[self.dst_custom].NameOfStation, encoding='ascii')
            len_name = bytes.fromhex(format(len(name), '04x'))
        content_name = bytes([0x02, 0x02]) + len_name + name

        ip = bytes([0x00, 0x01]) + self.ip_to_hex(self.devices[self.dst_custom].ip_conf)
        len_ip = bytes.fromhex(format(len(ip), '04x'))
        content_ip = bytes([0x01, 0x02]) + len_ip + ip

        family = self.devices[self.dst_custom].Family
        if len(family) % 2 == 1:
            family = bytes([0x00, 0x00]) + bytes(family, encoding='ascii') + bytes([0x00])
            len_family = bytes.fromhex(format(len(family) - 1, '04x'))
        else:
            family = bytes([0x00, 0x00]) + bytes(family, encoding='ascii')
            len_family = bytes.fromhex(format(len(family), '04x'))
        content_family = bytes([0x02, 0x01]) + len_family + family

        self.block = content_name + content_ip + content_family
        return self.compose_response()

    def generate_get(self, param):
        self.frame_id = 0xfefd
        self.service_id = pnio_dcp.protocol.dcp_header.GET
        content_tail = bytes([0x05, 0x04, 0x0003, 0x000001])

        if param == 'IP':
            opt, subopt = 0x01, 0x02
            content = bytes([0x00, 0x01]) + self.ip_to_hex(self.devices[self.dst_custom].ip_conf)
        else:
            opt, subopt = 0x02, 0x02
            if len(self.devices[self.dst_custom].NameOfStation) % 2 == 1:
                content = bytes([0x00, 0x00]) + bytes(self.devices[self.dst_custom].NameOfStation,
                                                      encoding='ascii') + bytes([0x00])
            else:
                content = bytes([0x00, 0x00]) + bytes(self.devices[self.dst_custom].NameOfStation, encoding='ascii')
        block_content = content + content_tail
        self.block = pnio_dcp.protocol.DCPBlockRequest(opt, subopt, len(content) + (1 if len(content) % 2 == 1 else 0), block_content)
        return self.compose_response()

    def generate_set(self):
        self.frame_id = 0xfefd
        self.service_id = pnio_dcp.protocol.dcp_header.SET
        block_content = bytes([0x02, 0x02]) + binascii.unhexlify(self.devices[self.dst_custom].err_code)
        self.block = pnio_dcp.protocol.DCPBlockRequest(0x05, 0x04, len(block_content), block_content)
        return self.compose_response()

    def generate_reset(self):
        self.frame_id = 0xfefd
        self.service_id = pnio_dcp.protocol.dcp_header.SET
        opt, subopt = 0x05, 0x04
        req_opt, req_subopt = 0x05, 0x06
        block_content = bytes([req_opt, req_subopt]) + binascii.unhexlify(self.devices[self.dst_custom].err_code)
        self.block = pnio_dcp.protocol.DCPBlockRequest(opt, subopt, len(block_content), block_content)
        return self.compose_response()

    def compose_response(self):
        dcp = pnio_dcp.protocol.dcp_header(self.frame_id, self.service_id, self.service_type, self.xid, 0x0000, len(self.block), payload=self.block)
        eth = pnio_dcp.protocol.eth_header(pnio_dcp.util.mac_to_hex(self.src), pnio_dcp.util.mac_to_hex(self.dst_custom), self.eth_type, payload=dcp)
        return [bytes(eth)]
