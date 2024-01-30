from profi_dcp.profi_dcp import DCP

dcp = DCP("192.168.0.1")

identified_devices = dcp.identify_all()
for dev in identified_devices:
    print(dev)
