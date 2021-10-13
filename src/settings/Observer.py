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
from typing import Any

# Qt libraries
from PyQt5 import QtCore

# Local libraries
from src.utils import SingletonMetaClass


class ObserverSignal(QtCore.QObject):
    Connect: QtCore.pyqtSignal = QtCore.pyqtSignal()
    ValuePressureChanged: QtCore.pyqtSignal = QtCore.pyqtSignal(float)

    def __init__(self):
        QtCore.QObject.__init__(self)


class Observer(metaclass=SingletonMetaClass):
    """
    The `Observer` is a singleton class (all instances point to the same reference).

    The `Observer` receives information and warns all clients about it.
    """
    UnitPressure: str = "Unit Pressure"

    def __init__(self) -> None:
        # NOTE: signal class (emitted when some relevant property has changed)
        self.Signal: ObserverSignal = ObserverSignal()

    def setValue(self, value:Any, key:str) -> None:
        if key == self.UnitPressure:
            self.Signal.ValuePressureChanged.emit(value)