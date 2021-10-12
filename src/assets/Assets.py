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
from typing import Dict

# Qt libraries
from PyQt5 import QtCore, QtGui

# Local libraries
from src.utils import SingletonMetaClass


class Assets(metaclass=SingletonMetaClass):
    """
    The `Assets` is a singleton class (all instances point to the same reference).

    The `Assets` that store graphical assets for this software.
    """
    def __init__(self) -> None:
        
        self._icons: Dict[str, QtGui.QIcon] = {}

        self._loadIcons()

    def get(self, name:str) -> QtGui.QIcon:
        return self._icons[name]

    def _loadIcons(self) -> None:
        folder = os.path.join(os.path.dirname(__file__), "svg")
        files = self._get_all_filepaths(folder, "svg")
        for fid in files:
            self._icons[self._get_file_name(fid)] = QtGui.QIcon(fid)

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