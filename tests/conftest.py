from fixtures.mock_return import mock_return
from fixtures.instance_dcp import instance_dcp
from fixtures.l2_socket import l2_sockets
from fixtures.l2_socket import loopback_sockets
import logging

logging.basicConfig(level='DEBUG',
                    format='%(asctime)8s | %(name)-12s | %(levelname)-8s | %(message)s',
                    datefmt='%H:%M:%S')
