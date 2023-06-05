# PNIO-DCP

A simple Python library to send and receive messages with the Profinet Dynamic Configuration Protocol (DCP) protocol.
It can send requests and parse the corresponding responses to identify devices over the network, get and set their parameters or reset them to factory settings.

Source code: [https://gitlab.com/pyshacks/pnio_dcp](https://gitlab.com/pyshacks/pnio_dcp)

## Installation

The PNIO-DCP package itself can be installed via `pip` after cloning the repository 
```sh
pip install <path to project root>
```
It was tested with Python 3.6, other Python versions might work as well.

### Windows
To use this library on Windows, Npcap (or WinPcap) is required. Npcap can be downloaded from here: [https://nmap.org/npcap/](https://nmap.org/npcap/)

### Linux
On Linux, no additional installations are required since raw sockets are used instead. However, this requires running it with root permission.

### Other Operating Systems
PNIO-DCP has not been tested on any other operating systems besides Windows and Linux.

## Usage

This section gives a short overview of the available features and how to use them. 

Create a new DCP instance with
```python
ip = "10.0.0.76"
dcp = pnio_dcp.DCP(ip)
```
where the given IP address is the IP of the host machine in the network to use for DCP communication.

All currently available requests are described in the following.  
All requests except `identify_all` will raise a `pnio_dcp.DcpTimeoutError` if the requested device does not answer within the allowed time frame (currently 10s).

### Identify Request
Identify requests can be used to identify DCP devices in the network. 
The identified devices are always returned as pnio_dcp.Device objects.

To identify all devices in the network, use
```python
identified_devices = dcp.identify_all()
```
This returns a list containing all devices found. If no devices where found, this list is empty.

To get more information about a specific device with the MAC address `mac_address`, use
```python
mac_address = "02:00:00:00:00:00"
device = dcp.identify(mac_address)
```

### Set Requests
Set requests can be used to change parameters of the device with the MAC address `mac_address`.

Use to following, to set its name of station to the given `new_name` (a string):  
```python
new_name = "a-new-name"
dcp.set_name_of_station(mac_address, new_name)
```

Use `set_ip_address` to set the IP configuration of the device. 
You must provide the new configuration as list containing the new IP address as first element, the subnet mask as second element, and the router as third element.
```python
ip_conf = ["10.0.0.31", "255.255.240.0", "10.0.0.1"]
dcp.set_ip_address(mac_address, ip_conf)
```

### Get Requests
Get requests can be used to get information about the device with the MAC address `mac_address`.  
Two such requests are supported: use 
```python
ip = dcp.get_ip_address(mac_address)
```
to get the IP address of the device (as string) and
```python
name_of_station = dcp.get_name_of_station(mac_address)
```
to get its name of station.

### Blink LED Request
This request can be used to identify a device with a given MAC-Address physically. After the request is send the device will flash its LEDs. Usage:
```python
dcp.blink(mac_address)
```

### Reset Requests

The communication parameters of the device with the MAC address `mac_address` can be reset to the factory settings with
```python
dcp.reset_to_factory(mac_address)
```

## License

This project is licensed under the MIT license.

MIT © 2020-2022 Codewerk GmbH, Karlsruhe
