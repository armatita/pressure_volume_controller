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
from typing import Any

# Local libraries
from src.utils import SingletonMetaClass


class Settings(metaclass=SingletonMetaClass):
    """
    The `Settings` is a singleton class (all instances point to the same reference).

    The `Settings` stores all data related to preferences and configuration.
    """
    Name: str = "Name"
    Version: str = "Version"
    Language: str = "Language"
    ComPort: str = "COM Port"
    def __init__(self, user_folder:str=None, name:str=None, version:str=None) -> None:
        self._user_folder: str = user_folder

        self._user_file: str = os.path.join(self._user_folder, "configuration.json")

        # NOTE: default properties (properties will be initialized from these if not already existing)
        self._defaults: dict = {}
        self._defaults[self.Name] = name
        self._defaults[self.Version] = version
        self._defaults[self.Language] = "English"
        self._defaults[self.ComPort] = "None"
        
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