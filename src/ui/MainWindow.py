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
import time

# Qt libraries
from PyQt5 import QtCore, QtGui, QtWidgets

# Local libraries
from src.settings import Settings, Observer
from src.language import Language
from src.unit     import Unit
from src.utils    import COMUtils
from src.assets   import Assets
from .MainDialogs import InfoDialog, UnitsDialog, HorizontalLine, PreferencesDialog
from .SideWidgets import CalibrationToolbar, RunWidget


class RunDockWidget(QtWidgets.QDockWidget):
    def __init__(self, parent=None, settings:Settings=None, language:Language=None, unit:Unit=None, observer:Observer=None, assets:Assets=None):
        self._settings: Settings = settings
        self._language: Language = language
        self._unit: Unit = unit
        self._observer: Observer = observer
        self._assets: Assets = assets

        self._object_widget: RunWidget = RunWidget(parent, settings=self._settings, language=self._language, unit=self._unit, observer=self._observer, assets=self._assets)

        QtWidgets.QDockWidget.__init__(self, self._language.get(self._language.RunManager), parent)

        self.setWidget(self._object_widget)
        self.setAllowedAreas(QtCore.Qt.LeftDockWidgetArea | QtCore.Qt.RightDockWidgetArea)


class CentralWidget(QtWidgets.QWidget):
    def __init__(self, parent):
        QtWidgets.QWidget.__init__(self, parent)

        self.setSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Expanding)


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
        self._language: Language = Language(settings=self._settings)

        # NOTE: units object (for conversion)
        self._unit: Unit = Unit(settings=self._settings)

        # NOTE: the observer class warns when a real time value has changed
        self._observer: Observer = Observer()

        # NOTE: assets object
        self._assets: Assets = Assets()

        # NOTE: setting up window icon
        self.setWindowIcon(self._assets.get("logo"))

        # NOTE: dock widgets
        self._dock_runs_widget: RunDockWidget = RunDockWidget(self, settings=self._settings, language=self._language, unit=self._unit, observer=self._observer, assets=self._assets)
        self.addDockWidget(QtCore.Qt.LeftDockWidgetArea, self._dock_runs_widget)

        # NOTE: central widget
        self._central_widget: CentralWidget = CentralWidget(self)
        self.setCentralWidget(self._central_widget)

        # NOTE: building menu.
        self._buildMenuBar()

        # NOTE: Maximizing on startup
        self.showMaximized()

    def _buildMenuBar(self):
        self._file_menu:QtWidgets.QMenu = self.menuBar().addMenu(self._language.get(self._language.File))
        # self._edit_menu:QtWidgets.QMenu = self.menuBar().addMenu(self._language.get(self._language.Edit))
        self._view_menu:QtWidgets.QMenu = self.menuBar().addMenu(self._language.get(self._language.View))
        self._settings_menu: QtWidgets.QMenu = self.menuBar().addMenu(self._language.get(self._language.Settings))
        self._about_menu: QtWidgets.QMenu = self.menuBar().addMenu(self._language.get(self._language.About))

        self._quit_action: QtWidgets.QAction = QtWidgets.QAction(self._assets.get("close"), self._language.get(self._language.Quit), self)
        self._quit_action.triggered.connect(self._onExit)

        self._file_menu.addSeparator()
        self._file_menu.addAction(self._quit_action)

        self._view_menu.addAction(self._dock_runs_widget.toggleViewAction())

        self._units_action: QtWidgets.QAction = QtWidgets.QAction(self._assets.get("ruler"), self._language.get(self._language.Units), self)
        self._units_action.triggered.connect(self._onUnits)

        self._preferences_action: QtWidgets.QAction = QtWidgets.QAction(self._assets.get("gear"), self._language.get(self._language.Preferences), self)
        self._preferences_action.triggered.connect(self._onPreferences)

        self._settings_menu.addAction(self._units_action)
        self._settings_menu.addSeparator()
        self._settings_menu.addAction(self._preferences_action)

        self._information_action: QtWidgets.QAction = QtWidgets.QAction(self._assets.get("info"), self._language.get(self._language.Information), self)
        self._information_action.triggered.connect(self._onInformation)

        self._license_action: QtWidgets.QAction = QtWidgets.QAction(self._assets.get("license"), self._language.get(self._language.License), self)
        self._license_action.triggered.connect(self._onLicense)

        self._help_action: QtWidgets.QAction = QtWidgets.QAction(self._assets.get("help"), self._language.get(self._language.Help), self)
        self._help_action.triggered.connect(self._onHelp)

        self._about_menu.addAction(self._information_action)
        self._about_menu.addAction(self._license_action)
        self._about_menu.addSeparator()
        self._about_menu.addAction(self._help_action)

    def _onUnits(self) -> None:
        units_dialog = UnitsDialog(self, settings=self._settings, language=self._language, unit=self._unit, observer=self._observer, assets=self._assets)
        units_dialog.show()

    def _onPreferences(self) -> None:
        preferences_dialog = PreferencesDialog(self, settings=self._settings, language=self._language, unit=self._unit, observer=self._observer, assets=self._assets)
        preferences_dialog.show()

    def _onInformation(self) -> None:
        info_dialog = InfoDialog(self, self._assets.get("info"), text=self._language.get(self._language.InfoMessage), title=self._language.get(self._language.Information) + " " + self._name + " " + self._version, close_text=self._language.get(self._language.Close))
        info_dialog.show()

    def _onLicense(self) -> None:
        info_dialog = InfoDialog(self, self._assets.get("license"), text=self._language.get(self._language.LicenseMessage), title=self._language.get(self._language.License), close_text=self._language.get(self._language.Close))
        info_dialog.show()

    def _onHelp(self) -> None:
        info_dialog = InfoDialog(self, self._assets.get("help"), text=self._language.get(self._language.HelpMessage), title=self._language.get(self._language.Help), close_text=self._language.get(self._language.Close))
        info_dialog.show()

    def _onExit(self) -> None:
        self.close()

    def closeEvent(self, event) -> None:
        reply = QtWidgets.QMessageBox.question(self, 'Quit ' + self._name + "?", 'Are you sure you want to quit?', QtWidgets.QMessageBox.Yes | QtWidgets.QMessageBox.No, QtWidgets.QMessageBox.No)
        if reply == QtWidgets.QMessageBox.Yes:
            self._settings.save()
            print("MainWindow::closeEvent : quitting software at: ", time.asctime())
            QtWidgets.QApplication.instance().quit()