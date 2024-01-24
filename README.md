# PROFINET-DCP

This is a fork from [profinet_dcp](https://gitlab.com/pyshacks/profinet_dcp).

A simple Python library to send and receive messages with the Profinet Discovery and basic Configuration Protocol (DCP) protocol.
It can send requests and parse the corresponding responses to identify devices over the network, get and set their parameters or reset them to factory settings.

Source code: [https://gitlab.com/pyshacks/profinet_dcp](https://gitlab.com/pyshacks/profinet_dcp)

## Installation

The PNIO-DCP package itself can be installed via `pip` after cloning the repository 
```sh
pip install <path to project root>
```
or from pypi with
```sh
pip install profinet_dcp
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
from profinet_dcp import DCP
ip = "10.0.0.76"
dcp = profinet_dcp.DCP(ip)
```
where the given IP address is the IP of the host machine in the network to use for DCP communication.

All currently available requests are described in the following.  
All requests except `identify_all` will raise a `profinet_dcp.DcpTimeoutError` if the requested device does not answer within the allowed time frame (currently 7s).

### Identify Request
Identify requests can be used to identify DCP devices in the network. 
The identified devices are always returned as profinet_dcp.Device objects.

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
By default name or IP configuration will be stored permanent, meaning that they will surrive a
power reset of the device. By setting `store_permanent=False` the parameters will only be saved
temporary.

Use the following, to set the device's name of station to the given `new_name` (a string),
remember that there are [requirements for device names](https://profinetuniversity.com/naming-addressing/profinet-naming-convention):
```python
new_name = "a-new-name"
dcp.set_name_of_station(mac_address, new_name)
```

Or to set it temporary:
```python
new_name = "a-new-name"
dcp.set_name_of_station(mac_address, new_name, False)
```

Use `set_ip_address` to set the IP configuration of the device. 
You must provide the new configuration as list containing the new IP address as first element, the subnet mask as second element, and the router as third element.
```python
ip_conf = ["10.0.0.31", "255.255.240.0", "10.0.0.1"]
dcp.set_ip_address(mac_address, ip_conf)
```

Set the IP configuration temporary:
```python
ip_conf = ["10.0.0.31", "255.255.240.0", "10.0.0.1"]
dcp.set_ip_address(mac_address, ip_conf, False)
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

There are two reset functions defined in the DCP specification. For both the MAC-Address of the device must be given as a string.

`factory_reset` is optional in the device implementation and can be invoked with:
```python
dcp.factory_reset(mac_address)
```

The `reset_to_factory` method is mandatory for all devices and can be used to reset certain data or parameter of the device, depending on the reset mode. The `reset_mode` parameter is optional, if not given the communication parameters will be reset (similar to `mode=ResetFactoryModes.RESET_COMMUNICATION`). Usage:

```python
dcp.reset_to_factory(mac_address, mode=ResetFactoryModes.RESET_COMMUNICATION)
```

The following modes are provided in `ResetFactoryModes`, they can be imported with `from dcp import ResetFactoryModes` :
* `RESET_APPLICATION_DATA`: Reset data which have been stored permanent in submodules and 
modules to factory values.
* `RESET_COMMUNICATION`: All parameters active for the interface or the ports and the ARs are set to the default values and if permanently stored reset. This is the default option.
* `RESET_ENGENEERING`: Reset engineering parameters which have been stored permanently to its factory values.
* `RESET_ALL_DATA`: Reset all stored data on the interface to its factory default values.
* `RESET_DEVICE`: Reset the communication parameters of all interfaces of the device and reset all parameters of the device.
* `RESET_AND_RESTORE`: Reset installed software revisions to factory images.

**Note:** Some of these modes may not be supported by all devices.


## License

This project is licensed under the MIT license.

MIT © 2020-2023 Codewerk GmbH, Karlsruhe
