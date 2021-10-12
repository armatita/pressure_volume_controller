"""
MIT License

Copyright (c) 2021 Pedro Correia

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
"""

# Python libraries
from typing import List

# COM port communication library
import serial.tools.list_ports


PORTS: list = list(serial.tools.list_ports.comports())


class COMUtils:
    """
    Utilities regarding the management of COM ports.
    """
    @staticmethod
    def getAllCOMPorts() -> List[str]:
        return [(port_.device, port_.description) for port_ in PORTS]

    @staticmethod
    def getAllCOMPortDevices() -> List[str]:
        return [port_.device for port_ in PORTS]

    @staticmethod
    def getDescription(device:str) -> str:
        for port_ in PORTS:
            if port_.device == device:
                return port_.description
    
    @staticmethod
    def getDevice(description:str) -> str:
        for port_ in PORTS:
            if port_.description == description:
                return port_.device


if __name__ == "__main__":
    print(COMUtils.getAllCOMPorts())
    devices = COMUtils.getAllCOMPortDevices()
    print(COMUtils.getDescription(devices[0]))

