import pytest
import time

from util import pcap_available, get_ip
from profi_dcp.profi_dcp import DCP


@pytest.mark.skip
class TestStressTests:
    """
    Test creating and deleating multiple dcp-classes (which open and close
    their own pcap buffer).
    """

    @pytest.mark.skipif(not pcap_available(), reason="Could not find Pcap")
    def test_initialization_stress(self):
        """
        Test create and delete of multiple dcp instance.
        """
        ip = get_ip()

        repetitions = 100
        wait_duration = 5

        for _ in range(repetitions):
            dcp = DCP(ip)
            time.sleep(wait_duration)
            del dcp
            time.sleep(wait_duration)
