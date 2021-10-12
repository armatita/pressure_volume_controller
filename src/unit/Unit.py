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
from typing import Any, List, Tuple

# Local libraries
from src.utils import SingletonMetaClass
from src.settings import Settings


class ListPressureUnit:
    kPa: str = "kPa"
    Pa: str = "Pa"

    @staticmethod
    def toList() -> List[str]:
        return [ListPressureUnit.kPa, ListPressureUnit.Pa]


class ListVolumeUnit:
    cm3: str = "cm<sup>3<\sup>"
    dm3: str = "dm<sup>3<\sup>"
    m3: str = "m<sup>3<\sup>"
    ml: str = "milliliter"
    l: str = "liter"

    @staticmethod
    def toList() -> List[str]:
        return [ListVolumeUnit.cm3, ListVolumeUnit.dm3, ListVolumeUnit.m3, ListVolumeUnit.ml, ListVolumeUnit.l]



class Unit(metaclass=SingletonMetaClass):
    """
    The `Unit` is a singleton class (all instances point to the same reference).

    The `Unit` stores all data related to unit conversion.
    """
    UnitPressure: str = "Unit Pressure"
    UnitVolume: str = "Unit Volume"

    def __init__(self, settings:str) -> None:
        self._settings: Settings = settings
        self._settings.Signal.UnitPressureChanged.connect(self._unitPressureChanged)
        self._settings.Signal.PrecisionPressureChanged.connect(self._precisionPressureChanged)
        self._settings.Signal.UnitVolumeChanged.connect(self._unitVolumeChanged)
        self._settings.Signal.PrecisionVolumeChanged.connect(self._precisionVolumeChanged)

        self._unit_pressure: str = self._settings.getProperty(self._settings.UnitPressure)
        self._precision_pressure: int = self._settings.getProperty(self._settings.PrecisionPressure)
        self._unit_volume: str = self._settings.getProperty(self._settings.UnitVolume)
        self._precision_volume: int = self._settings.getProperty(self._settings.PrecisionVolume)

        self._min_pressure: float = 0.0
        self._max_pressure: float = 2000.0
        self._min_volume: float = 0.0
        self._max_volume: float = 1000000.0

    def get(self, value:Any, key:str) -> float:
        if key == self.UnitPressure:
            if self._unit_pressure == ListPressureUnit.kPa:
                return value
            elif self._unit_pressure == ListPressureUnit.Pa:
                return value*1000
        elif key == self.UnitVolume:
            if self._unit_volume == ListVolumeUnit.cm3:
                return value
            elif self._unit_volume == ListVolumeUnit.dm3:
                return value/1000
            elif self._unit_volume == ListVolumeUnit.m3:
                return value/1000000
            elif self._unit_volume == ListVolumeUnit.ml:
                return value
            elif self._unit_volume == ListVolumeUnit.l:
                return value/1000

    def getAsString(self, value: Any, key:str) -> str:
        precision = self._precision(key)
        value = self.get(value, key)
        suffix = self.getSuffix(key)
        return precision.format(value) + " " + suffix

    def getPrecision(self, key:str) -> int:
        if key == self.UnitPressure:
            return self._precision_pressure
        elif key == self.UnitVolume:
            return self._precision_volume

    def getRange(self, key:str) -> Tuple[int, int]:
        if key == self.UnitPressure:
            if self._unit_pressure == ListPressureUnit.kPa:
                return self._min_pressure, self._max_pressure
            elif self._unit_pressure == ListPressureUnit.Pa:
                return self._min_pressure*1000, self._max_pressure*1000
        elif key == self.UnitVolume:
            if self._unit_volume == ListVolumeUnit.cm3:
                return self._min_volume, self._max_volume
            elif self._unit_volume == ListVolumeUnit.dm3:
                return self._min_volume/1000, self._max_volume/1000
            elif self._unit_volume == ListVolumeUnit.m3:
                return self._min_volume/1000000, self._max_volume/1000000
            elif self._unit_volume == ListVolumeUnit.ml:
                return self._min_volume, self._max_volume
            elif self._unit_volume == ListVolumeUnit.l:
                return self._min_volume/1000, self._max_volume/1000

    def _precision(self, key: str) -> str:
        if key == self.UnitPressure:
            return '{0:.' + str(self._precision_pressure) + 'f}'
        elif key == self.UnitVolume:
            return '{0:.' + str(self._precision_volume) + 'f}'
        
    def getSuffix(self, key:str, add_space:bool=False) -> None:
        space = ""
        if add_space:
            space = " "
        if key == self.UnitPressure:
            return space + self._unit_pressure
        elif key == self.UnitVolume:
            return space + self._unit_volume

    def options(self, key:str) -> List[str]:
        if key == self.UnitPressure:
            return ListPressureUnit.toList()
        elif key == self.UnitVolume:
            return ListVolumeUnit.toList()

    def _unitPressureChanged(self, unit_pressure:str) -> None:
        self._unit_pressure = unit_pressure

    def _precisionPressureChanged(self, value:int) -> None:
        self._precision_pressure = value

    def _unitVolumeChanged(self, unit_volume:str) -> None:
        self._unit_volume = unit_volume

    def _precisionVolumeChanged(self, value:int) -> None:
        self._precision_volume = value