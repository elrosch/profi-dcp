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
* fix PyPI classifier format
