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

# Qt libraries
from PyQt5 import QtCore, QtWidgets

# Local libraries
from src.settings import Settings
from src.language import Language
from src.utils    import COMUtils


class RunWidget(QtWidgets.QWidget):
    """
    This is the Objects managing widget for Golab. It has an object tree plus a 
    few other widgets for object inspection and manipulation.
    """
    def __init__(self, parent=None, settings:Settings=None, language:Language=None):
        QtWidgets.QWidget.__init__(self, parent)

        self._settings: Settings = settings
        self._language: Language = language


class RunDockWidget(QtWidgets.QDockWidget):
    def __init__(self, parent=None, settings:Settings=None, language:Language=None):
        self._settings: Settings = settings
        self._language: Language = language

        self._object_widget: RunWidget = RunWidget(parent, settings=self._settings, language=self._language)

        QtWidgets.QDockWidget.__init__(self, self._language.get(self._language.RunManager), parent)

        self.setWidget(self._object_widget)
        self.setAllowedAreas(QtCore.Qt.LeftDockWidgetArea | QtCore.Qt.RightDockWidgetArea)


class MainWindow(QtWidgets.QMainWindow):
    """
    This is the Main Window for Prime. It stores the permanent data and
    initializes all the manager objects.
    """
    def __init__(self, name:str, version:str, user_folder:str):
        QtWidgets.QMainWindow.__init__(self)

        # NOTE: General properties
        self._name: str        = name
        self._version: str     = version
        self._user_folder: str = user_folder
        self.setWindowTitle(self._name + " " + self._version)

        # NOTE: settings (for preferences and configurations)
        self._settings: Settings = Settings(user_folder=self._user_folder, name=self._name, version=self._version)

        # NOTE: language object (for translations)
        self._language: Language = Language(language=self._settings.getProperty(self._settings.Language))

        # NOTE: dock widgets
        # Building main widgets
        self._dock_runs_widget: RunDockWidget = RunDockWidget(self, settings=self._settings, language=self._language)
        self.addDockWidget(QtCore.Qt.LeftDockWidgetArea, self._dock_runs_widget)

        # NOTE: building menu.
        self._buildMenuBar()

        # NOTE: Maximizing on startup
        self.showMaximized()

    def _buildMenuBar(self):
        self._file_menu:QtWidgets.QMenu = self.menuBar().addMenu(self._language.get(self._language.File))
        self._edit_menu:QtWidgets.QMenu = self.menuBar().addMenu(self._language.get(self._language.Edit))
        self._view_menu:QtWidgets.QMenu = self.menuBar().addMenu(self._language.get(self._language.View))

        self._view_menu.addAction(self._dock_runs_widget.toggleViewAction())