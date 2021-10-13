import pnio_dcp
import pytest
import time

from test_socket import pcap_available, get_ip


@pytest.mark.skip
class TestStressTests:

    @pytest.mark.skipif(not pcap_available(), reason="Could not find Pcap")
    def test_initialization_stress(self):
        ip = get_ip()

        repetitions = 100
        wait_duration = 5

        for _ in range(repetitions):
            dcp = pnio_dcp.DCP(ip)
            time.sleep(wait_duration)
            del dcp
            time.sleep(wait_duration)
