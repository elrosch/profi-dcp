# Changelog

## Version 1.0.0: Initial Release
* Python library for the Profinet Dynamic Configuration Protocol (DCP)
* Send identify, get, set, and reset requests to DCP devices and receive the responses
* Windows only

## Version 1.1.0: Linux Support
* Add Linux support via raw sockets
* Internal refactoring and improvement of code quality
    * completely rewrite packet data structures
    * improve names of internal functions and member variables

## Version 1.1.1: Improved Error Handling and Logging
* Switch to package-wide logging namespace instead of by file
* Improve error handling for invalid ip addresses
* Add test for invalid ips and stress test for initialization

## Version 1.1.2: Hotfix for PyPI Deployment
* Fix PyPI classifier format

## Version 1.1.3: Hotfix for Cross-Platform MAC Address Inference and Reduced Verbosity
* Use `psutil.AF_LINK` to filter the response of `psutil.net_if_addrs()` instead of using a workaround to determine it for cross-platform use.
* Remove logging output when ignoring packets with unexpected XIDs as can result in significant log volume even though no user action is required. 

## Version 1.1.4: Resolved Issue that led to Packets being dropped
* The issue was caused by the pcap-buffer being full in environments with lots of network traffic
* Pcap filter is now set correctly
* Pcap buffer will be emptied before sending a packet
* Improved file structure in `tests/` directory
