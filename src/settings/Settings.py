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
import os
import json
import warnings
from typing import Any, List, Tuple

# Qt libraries
from PyQt5 import QtCore

# Local libraries
from src.utils import SingletonMetaClass


class SettingsSignal(QtCore.QObject):
    NameChanged: QtCore.pyqtSignal = QtCore.pyqtSignal(str)
    VersionChanged: QtCore.pyqtSignal = QtCore.pyqtSignal(str)
    LanguageChanged: QtCore.pyqtSignal = QtCore.pyqtSignal(str)
    ComPortChanged: QtCore.pyqtSignal = QtCore.pyqtSignal(str)
    UnitPressureChanged: QtCore.pyqtSignal = QtCore.pyqtSignal(str)
    UnitVolumeChanged: QtCore.pyqtSignal = QtCore.pyqtSignal(str)
    PrecisionPressureChanged: QtCore.pyqtSignal = QtCore.pyqtSignal(int)
    PrecisionVolumeChanged: QtCore.pyqtSignal = QtCore.pyqtSignal(int)

    def __init__(self):
        QtCore.QObject.__init__(self)


class Settings(metaclass=SingletonMetaClass):
    """
    The `Settings` is a singleton class (all instances point to the same reference).

    The `Settings` stores all data related to preferences and configuration.
    """
    Name: str = "Name"
    Version: str = "Version"
    Language: str = "Language"
    ComPort: str = "COM Port"

    UnitPressure: str = "Unit Pressure"
    UnitVolume: str = "Unit Volume"

    PrecisionPressure: str = "Precision Pressure"
    PrecisionVolume: str = "Precision Volume"

    NullString: str = "None"
    def __init__(self, user_folder:str=None, name:str=None, version:str=None) -> None:
        # NOTE: signal class (emitted when some relevant property has changed)
        self.Signal: SettingsSignal = SettingsSignal()

        # NOTE: relevant paths to user folder and configuration file.
        self._user_folder: str = user_folder
        self._user_file: str = os.path.join(self._user_folder, "configuration.json")
        self._calibration_folder: str = os.path.join(self._user_folder, "Calibration")
        self._calibration_extension: str = "csv"

        # NOTE: default properties (properties will be initialized from these if not already existing)
        self._defaults: dict = {}
        self._defaults[self.Name] = name
        self._defaults[self.Version] = version
        self._defaults[self.Language] = "English"
        self._defaults[self.ComPort] = self.NullString
        self._defaults[self.UnitPressure] = "kPa"
        self._defaults[self.UnitVolume] = "cm<sup>3<\sup>"
        self._defaults[self.PrecisionPressure] = 2
        self._defaults[self.PrecisionVolume] = 2

        # NOTE: associated signals
        self._signals: dict = {}
        self._signals[self.Name] = self.Signal.NameChanged
        self._signals[self.Version] = self.Signal.VersionChanged
        self._signals[self.Language] = self.Signal.LanguageChanged
        self._signals[self.ComPort] = self.Signal.ComPortChanged
        self._signals[self.UnitPressure] = self.Signal.UnitPressureChanged
        self._signals[self.UnitVolume] = self.Signal.UnitVolumeChanged
        self._signals[self.PrecisionPressure] = self.Signal.PrecisionPressureChanged
        self._signals[self.PrecisionVolume] = self.Signal.PrecisionVolumeChanged
        
        # NOTE: properties dictionary (the real settings)
        self._properties: dict = {}

        # NOTE: loading properties from file.
        self.load()

    def getProperty(self, param:str) -> Any:
        """
        Get a property from the 'SettingsManager'.
        """
        if param in self.keys():
            return self._properties[param]
        else:
            warnings.warn("SettingsManager::get : The property <%s> does not seem to exist."%param, UserWarning)

    def setProperty(self, param:str, value:Any) -> None:
        """
        Set a property in the ´SettingsManager'.
        """
        if param in self.keys():
            self._properties[param] = value
            self._signals[param].emit(value)
        else:
            warnings.warn("SettingsManager::get : The property <%s> does not seem to exist."%param, UserWarning)

    def save(self) -> bool:
        """
        Stores all the information on this manager to file.
        """
        str_dict = json.dumps(self._properties)
        with open(self._user_file, 'w') as fid:
            fid.write(str_dict)
        return True

    def load(self) -> bool:
        """
        Loads all information from file to this manager.
        """
        if not os.path.exists(self._calibration_folder):
            os.mkdir(self._calibration_folder)
        if not os.path.exists(self._user_file):
            self._propertyCheck()
            self.save()
            return False
        file_str = ""
        with open(self._user_file, 'r') as fid:
            file_str = fid.read()
        self._properties = json.loads(file_str)
        self._properties[self.Name] = self._defaults[self.Name]
        self._properties[self.Version] = self._defaults[self.Version]
        if self._propertyCheck():
            self.save()
        return True

    def keys(self)->list:
        """
        Returns a list with all available permanent properties.
        """
        return [key for key in self._properties.keys()]

    def calibrationCurves(self) -> List[str]:
        return self._loadFiles(self._calibration_folder)

    def loadCurve(self, name: str) -> Tuple[list, list]:
        x = []
        y = []
        if name in self.calibrationCurves():
            with open(os.path.join(self._calibration_folder, name + "." + self._calibration_extension), "r") as fid:
                lines = fid.readlines()
                for line in lines:
                    s = line.split(";")
                    x.append(float(s[0]))
                    y.append(float(s[1]))
        return x, y

    def loadCurveFromPath(self, path: str) -> Tuple[list, list]:
        x = []
        y = []
        with open(path, "r") as fid:
            lines = fid.readlines()
            for line in lines:
                s = line.split(";")
                x.append(float(s[0]))
                y.append(float(s[1]))
        return x, y

    def saveCurve(self, name:str, data:Tuple[list, list]) -> None:
        with open(os.path.join(self._calibration_folder, name + "." + self._calibration_extension), "w") as fid:
            for x, y in zip(data[0], data[1]):
                fid.write(f"{x};{y}\n")

    def createCurve(self, name:str) -> None:
        if name not in self.calibrationCurves():
            fid = open(os.path.join(self._calibration_folder, name + "." + self._calibration_extension), "w")
            fid.close()

    def deleteCurve(self, name:str) -> None:
        if name in self.calibrationCurves():
            os.remove(os.path.join(self._calibration_folder, name + "." + self._calibration_extension))

    def _loadFiles(self, folder) -> None:
        files = self._get_all_filepaths(folder, self._calibration_extension)
        paths = []
        for fid in files:
            paths.append(self._get_file_name(fid))
        return paths

    def _get_file_name(self, path):
        if not os.path.isdir(path):
            return os.path.splitext(os.path.basename(path))[0].split(".")[0]

    def _get_all_filepaths(self, root_path, ext):
        import os
        all_files = []
        for root, dirs, files in os.walk(root_path):
            for filename in files:
                if filename.lower().endswith(ext):
                    all_files.append(os.path.join(root, filename))
        return all_files

    def _propertyCheck(self)->None:
        """
        Check if all relevant properties exist on the local
        properties dictionary.
        """
        properties = list(self._defaults.keys())
        has_correction = False
        for param in properties:
            if param not in self._properties.keys():
                self._properties[param] = self._defaults[param]
                has_correction = True
        return has_correction