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
from .MainDialogs import InfoDialog


class HorizontalLine(QtWidgets.QFrame):
    '''
    Horizontal Line.
    '''
    def __init__(self):
        QtWidgets.QFrame.__init__(self)
        self.setFrameShape(QtWidgets.QFrame.HLine)
        self.setFrameShadow(QtWidgets.QFrame.Sunken)
        self.setSizePolicy(QtWidgets.QSizePolicy.Preferred, QtWidgets.QSizePolicy.Minimum)


class CalibrationToolbar(QtWidgets.QToolBar):
    def __init__(self, parent=None, settings:Settings=None, language:Language=None, unit:Unit=None, observer:Observer=None, assets:Assets=None):
        QtWidgets.QToolBar.__init__(self, parent)

        self._settings: Settings = settings

        self._language: Language = language
        self._unit: Unit = unit

        self._observer: Observer = observer

        self._assets: Assets = assets

        self._build()

    def _build(self):
        self._create_action = self.addAction(self._assets.get('plus'),"")
        self._create_action.setToolTip(self._language.get(self._language.CreateCalibrationCurveTooltip))

        self._delete_action = self.addAction(self._assets.get('delete'),"")
        self._delete_action.setToolTip(self._language.get(self._language.DeleteCalibrationCurveTooltip))

        self._edit_action = self.addAction(self._assets.get('edit'),"")
        self._edit_action.setToolTip(self._language.get(self._language.EditCalibrationCurveTooltip))

        self.addSeparator()

        self._import_action = self.addAction(self._assets.get('import'),"")
        self._import_action.setToolTip(self._language.get(self._language.ImportCalibrationCurveTooltip))

        self._export_action = self.addAction(self._assets.get('export'),"")
        self._export_action.setToolTip(self._language.get(self._language.ExportCalibrationCurveTooltip))


class RunWidget(QtWidgets.QWidget):
    """
    This is the Objects managing widget for Golab. It has an object tree plus a 
    few other widgets for object inspection and manipulation.
    """
    def __init__(self, parent=None, settings:Settings=None, language:Language=None, unit:Unit=None, observer:Observer=None, assets:Assets=None):
        QtWidgets.QWidget.__init__(self, parent)

        self._settings: Settings = settings
        self._settings.Signal.LanguageChanged.connect(self._languageChanged)
        self._settings.Signal.UnitPressureChanged.connect(self._unitPressureChanged)
        self._settings.Signal.UnitVolumeChanged.connect(self._unitVolumeChanged)
        self._settings.Signal.PrecisionPressureChanged.connect(self._unitPressureChanged)
        self._settings.Signal.PrecisionVolumeChanged.connect(self._unitVolumeChanged)

        self._language: Language = language
        self._unit: Unit = unit

        self._observer: Observer = observer
        self._observer.Signal.ValuePressureChanged.connect(self._onValuePressureChanged)

        self._assets: Assets = assets

        # NOTE: local variables
        self._current_pressure: float = 0.0
        self._current_volume: float = 0.0

        # NOTE: font to be used in titles
        title_font: QtGui.QFont = QtGui.QFont()
        title_font.setBold(True)

        # NOTE: calibration curve widgets
        self._calibration_title: QtWidgets.QLabel = QtWidgets.QLabel(self._language.get(self._language.CalibrationTitle), self)
        self._calibration_title.setFont(title_font)
        self._line1: HorizontalLine = HorizontalLine()
        
        self._calibration_toolbar: CalibrationToolbar = CalibrationToolbar(self, settings=self._settings, language=self._language, unit=self._unit, observer=self._observer, assets=self._assets)
        self._calibration_list: QtWidgets.QListWidget = QtWidgets.QListWidget(self)

        # NOTE: real time data widgets
        self._realtime_title: QtWidgets.QLabel = QtWidgets.QLabel(self._language.get(self._language.RealTimeTitle), self)
        self._realtime_title.setFont(title_font)
        self._line2: HorizontalLine = HorizontalLine()

        self._pressure_label: QtWidgets.QLabel = QtWidgets.QLabel(self._language.get(self._language.Pressure) + ":", self)
        self._pressure_edit: QtWidgets.QLabel = QtWidgets.QLabel(self._unit.getAsString(self._current_pressure, self._unit.UnitPressure), self)

        self._volume_label: QtWidgets.QLabel = QtWidgets.QLabel(self._language.get(self._language.Volume) + ":", self)
        self._volume_edit: QtWidgets.QLabel = QtWidgets.QLabel(self._unit.getAsString(self._current_volume, self._unit.UnitVolume), self)

        # NOTE: input data widgets
        self._target_title: QtWidgets.QLabel = QtWidgets.QLabel(self._language.get(self._language.TargetTitle), self)
        self._target_title.setFont(title_font)
        self._line3: HorizontalLine = HorizontalLine()

        self._target_label: QtWidgets.QLabel = QtWidgets.QLabel(self._language.get(self._language.TargetPressure) + ":", self)
        self._target_value: QtWidgets.QDoubleSpinBox = QtWidgets.QDoubleSpinBox(self)
        self._target_value.setSuffix(self._unit.getSuffix(self._unit.UnitPressure, add_space=True))
        self._target_value.setRange(*self._unit.getRange(self._unit.UnitPressure))
        self._target_value.setDecimals(self._unit.getPrecision(self._unit.UnitPressure))
        self._target_button: QtWidgets.QPushButton = QtWidgets.QPushButton(self._assets.get("check"), self._language.get(self._language.Validate), self)

        # NOTE: configuration widgets
        self._configuration_title: QtWidgets.QLabel = QtWidgets.QLabel(self._language.get(self._language.ConfigurationTitle), self)
        self._configuration_title.setFont(title_font)
        self._line4: HorizontalLine = HorizontalLine()
        self._comport_label: QtWidgets.QLabel = QtWidgets.QLabel(self._language.get(self._language.ComPort) + ":", self)
        self._comport_value: QtWidgets.QComboBox = QtWidgets.QComboBox(self)
        
        for port in COMUtils.getAllCOMPortDevices():
            self._comport_value.addItem(port)
        port = self._settings.getProperty(self._settings.ComPort)
        if port != self._settings.NullString and port in COMUtils.getAllCOMPortDevices():
            self._comport_value.setCurrentText(port)
        else:
            self._settings.setProperty(self._settings.ComPort, port)

        # NOTE: start button
        self._connect_button: QtWidgets.QPushButton = QtWidgets.QPushButton(self._assets.get("play"), self._language.get(self._language.Connect), self)

        # NOTE: layout
        grid_layout: QtWidgets.QGridLayout = QtWidgets.QGridLayout()
        i: int = -1
        i += 1
        grid_layout.addWidget(self._calibration_title, i, 0)
        grid_layout.addWidget(self._line1, i, 1, 1, 2)
        i += 1
        grid_layout.addWidget(self._calibration_toolbar, i, 0, 1, 3)
        i += 1
        grid_layout.addWidget(self._calibration_list, i, 0, 1, 3)
        i += 1
        grid_layout.addWidget(self._realtime_title, i, 0)
        grid_layout.addWidget(self._line2, i, 1, 1, 2)
        i += 1
        grid_layout.addWidget(self._pressure_label, i, 0)
        grid_layout.addWidget(self._pressure_edit, i, 1)
        i += 1
        grid_layout.addWidget(self._volume_label, i, 0)
        grid_layout.addWidget(self._volume_edit, i, 1)
        i += 1
        grid_layout.addWidget(self._target_title, i, 0)
        grid_layout.addWidget(self._line3, i, 1, 1, 2)
        i += 1
        grid_layout.addWidget(self._target_label, i, 0)
        grid_layout.addWidget(self._target_value, i, 1)
        grid_layout.addWidget(self._target_button, i, 2)
        i += 1
        grid_layout.addWidget(self._configuration_title, i, 0)
        grid_layout.addWidget(self._line4, i, 1, 1, 2)
        i += 1
        grid_layout.addWidget(self._comport_label, i, 0)
        grid_layout.addWidget(self._comport_value, i, 1)

        layout: QtWidgets.QVBoxLayout = QtWidgets.QVBoxLayout()
        layout.addLayout(grid_layout)
        layout.addStretch()
        layout.addWidget(self._connect_button)

        self.setLayout(layout)

    def _languageChanged(self) -> None:
        self._pressure_label.setText(self._language.get(self._language.Pressure) + ":")
        self._volume_label.setText(self._language.get(self._language.Volume) + ":")
        self._target_label.setText(self._language.get(self._language.TargetPressure) + ":")

    def _unitPressureChanged(self, unit_pressure:str) -> None:
        self._pressure_edit.setText(self._unit.getAsString(self._current_pressure, self._unit.UnitPressure))
        value: float = self._target_value.value()
        self._target_value.setSuffix(self._unit.getSuffix(self._unit.UnitPressure, add_space=True))
        self._target_value.setRange(*self._unit.getRange(self._unit.UnitPressure))
        self._target_value.setValue(self._unit.get(value, self._unit.UnitPressure))

    def _onValuePressureChanged(self, value:float) -> None:
        self._current_pressure = value
        self._unitPressureChanged("")

    def _unitPressureChanged(self, unit_volume:str) -> None:
        self._pressure_edit.setText(self._unit.getAsString(self._current_pressure, self._unit.UnitPressure))

    def _onValuevolumeChanged(self, value:float) -> None:
        self._current_volume = value
        self._unitVolumeChanged("")

    def _unitVolumeChanged(self, unit_volume:str) -> None:
        self._volume_edit.setText(self._unit.getAsString(self._current_volume, self._unit.UnitVolume))


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
        self._edit_menu:QtWidgets.QMenu = self.menuBar().addMenu(self._language.get(self._language.Edit))
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
        pass

    def _onPreferences(self) -> None:
        pass

    def _onInformation(self) -> None:
        info_dialog = InfoDialog(self, self._assets.get("info"), text=self._language.get(self._language.InfoMessage), title=self._language.get(self._language.Information), close_text=self._language.get(self._language.Close))
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