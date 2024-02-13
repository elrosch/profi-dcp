# PROFI-DCP

A simple Python library to send and receive messages with the Profinet Discovery and basic Configuration Protocol (DCP) protocol.
It can send requests and parse the corresponding responses to identify devices over the network, get and set their parameters or reset them to factory settings.
Documentation can be found [here](https://profinet-dcp-evileli-d85b3cec0c8c34ea4cf0296dc0474a82da67a09ab0.gitlab.io/) and in the [examples](./examples) directory.

**This is a fork from [pnio_dcp](https://gitlab.com/pyshacks/pnio_dcp).**

## Installation
### Release
The latest release is available in the public PyPi repo. 
Install via pip:
```
pip install profi-dcp
```
### From git repo
You can also install directly from the git repo.

1. Clone the repository

```
git clone <git-url> <destination>
```

2. Change into the clone directory
```
cd <destination>
```

3. Install via pip
```
pip install .
```

### Windows
To use this library on Windows, Npcap (or WinPcap) is required. Npcap can be downloaded from here: [https://nmap.org/npcap/](https://nmap.org/npcap/)

### Linux
On Linux, no additional installations are required since raw sockets are used instead. However, this requires running it with root permission.

### Other Operating Systems
PNIO-DCP has not been tested on any other operating systems besides Windows and Linux.

### [CLI](https://profinet-dcp-evileli-d85b3cec0c8c34ea4cf0296dc0474a82da67a09ab0.gitlab.io/profi_dcp.cli.html)
`profi-dcp` is the main entry point to the CLI.
It supports various subcommands which execute some basic functions.

For more information use the help flag  (`profi-dcp -h`).

#### Subcommands
- `identify` is a subcommand to identify devices.
- `set-ip` is a subcommand to set a new ip address for a device.