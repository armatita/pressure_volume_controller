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
import serial
from threading import Thread, Event

# Qt libraries
from PyQt5 import QtCore, QtGui, QtWidgets

# Local libraries
from src.settings import Settings, Observer
from src.unit     import Unit
from src.utils    import COMUtils
from src.language import Language
from src.assets   import Assets
from .MainDialogs import InfoDialog, UnitsDialog, HorizontalLine, PreferencesDialog, EditDialog


BIG_FONT: QtGui.QFont = QtGui.QFont()
BIG_FONT.setPointSize(64)
BIG_FONT.setBold(True)

MEDIUM_FONT: QtGui.QFont = QtGui.QFont()
MEDIUM_FONT.setPointSize(24)
MEDIUM_FONT.setBold(True)

BIG_SIZE: int = 64
MEDIUM_SIZE: int = 32

CALIBRATION_FILENAME: str = "Calibration"

class CentralWidget(QtWidgets.QWidget):
    def __init__(self, parent=None, settings:Settings=None, language:Language=None, unit:Unit=None, observer:Observer=None, assets:Assets=None):
        QtWidgets.QWidget.__init__(self, parent)

        self._settings: Settings = settings
        self._language: Language = language
        self._assets: Assets = assets
        self._unit: Unit = unit
        self._observer: Observer = observer
        self._observer.Signal.ValuePressureChanged.connect(self._onPressureChange)
        self._observer.Signal.SendInfo.connect(self._onInfo)

        if len(self._settings.calibrationCurves()) == 0:
            self._settings.createCurve(CALIBRATION_FILENAME)

        self._pressure_label: QtWidgets.QLabel = QtWidgets.QLabel(self._language.get(self._language.Pressure) + ": ", self)
        self._pressure_label.setFont(BIG_FONT)

        self._pressure_edit: QtWidgets.QLineEdit = QtWidgets.QLineEdit("0.0 kPa", self)
        self._pressure_edit.setReadOnly(True)
        self._pressure_edit.setFont(BIG_FONT)

        self._info_label: QtWidgets.QLabel = QtWidgets.QLabel("...", self)
        self._info_label.setFont(MEDIUM_FONT)
        self._info_label.setStyleSheet("""QLabel {
            color: red;
            border: 3px solid red;
            border-radius: 5px;
        }""")
        self._info_label.setAlignment(QtCore.Qt.AlignCenter)

        hbox_top: QtWidgets.QHBoxLayout = QtWidgets.QHBoxLayout()
        hbox_top.addWidget(self._pressure_label)
        hbox_top.addWidget(self._pressure_edit)

        # NOTE: tank
        self._line0: HorizontalLine = HorizontalLine()

        self._empty_tank_button: QtWidgets.QPushButton = QtWidgets.QPushButton(self._language.get(self._language.EmptyTank))
        self._fill_tank_button: QtWidgets.QPushButton = QtWidgets.QPushButton(self._language.get(self._language.FillTank))
        self._empty_tank_button.clicked.connect(self._onEmptyTank)
        self._fill_tank_button.clicked.connect(self._onFillTank)

        self._empty_tank_button.setFont(MEDIUM_FONT)
        self._fill_tank_button.setFont(MEDIUM_FONT)

        hbox_tank: QtWidgets.QHBoxLayout = QtWidgets.QHBoxLayout()
        hbox_tank.addWidget(self._empty_tank_button)
        hbox_tank.addWidget(self._fill_tank_button)

        # NOTE: calibração
        self._line1: HorizontalLine = HorizontalLine()

        self._calibration_label: QtWidgets.QLabel = QtWidgets.QLabel(self._language.get(self._language.CalibrationTitle) + ": ", self)
        self._calibration_import_button: QtWidgets.QPushButton = QtWidgets.QPushButton(self._assets.get("import"), self._language.get(self._language.Import))
        self._calibration_edit_button: QtWidgets.QPushButton = QtWidgets.QPushButton(self._assets.get("edit"), self._language.get(self._language.Edit))

        self._calibration_label.setFont(MEDIUM_FONT)
        self._calibration_import_button.setFont(MEDIUM_FONT)
        self._calibration_edit_button.setFont(MEDIUM_FONT)

        self._calibration_import_button.setIconSize(QtCore.QSize(MEDIUM_SIZE, MEDIUM_SIZE))
        self._calibration_edit_button.setIconSize(QtCore.QSize(MEDIUM_SIZE, MEDIUM_SIZE))

        self._calibration_import_button.clicked.connect(self._onImportCalibration)
        self._calibration_edit_button.clicked.connect(self._onEditCalibration)

        hbox_calibration: QtWidgets.QHBoxLayout = QtWidgets.QHBoxLayout()
        hbox_calibration.addWidget(self._calibration_label)
        hbox_calibration.addWidget(self._calibration_import_button)
        hbox_calibration.addWidget(self._calibration_edit_button)

        # NOTE: pressure validation
        self._line2: HorizontalLine = HorizontalLine()

        self._target_label: QtWidgets.QLabel = QtWidgets.QLabel(self._language.get(self._language.TargetPressure) + ":", self)
        self._target_value: QtWidgets.QDoubleSpinBox = QtWidgets.QDoubleSpinBox(self)
        self._target_value.setSuffix(self._unit.getSuffix(self._unit.UnitPressure, add_space=True))
        self._target_value.setRange(*self._unit.getRange(self._unit.UnitPressure))
        self._target_value.setDecimals(self._unit.getPrecision(self._unit.UnitPressure))
        self._target_button: QtWidgets.QPushButton = QtWidgets.QPushButton(self._assets.get("check"), self._language.get(self._language.Validate), self)
        self._target_button.clicked.connect(self._onTargetPressure)

        self._target_label.setFont(MEDIUM_FONT)
        self._target_value.setFont(MEDIUM_FONT)
        self._target_button.setFont(MEDIUM_FONT)
        self._target_button.setIconSize(QtCore.QSize(MEDIUM_SIZE, MEDIUM_SIZE))

        hbox_target: QtWidgets.QHBoxLayout = QtWidgets.QHBoxLayout()
        hbox_target.addWidget(self._target_label)
        hbox_target.addWidget(self._target_value)
        hbox_target.addWidget(self._target_button)

        # NOTE: COM port
        self._line3: HorizontalLine = HorizontalLine()

        self._comport_label: QtWidgets.QLabel = QtWidgets.QLabel(self._language.get(self._language.ComPort) + ": ", self)
        self._comport_value: QtWidgets.QComboBox = QtWidgets.QComboBox(self)
        
        for port in COMUtils.getAllCOMPortDevices():
            self._comport_value.addItem(port)
        port = self._settings.getProperty(self._settings.ComPort)
        if port != self._settings.NullString and port in COMUtils.getAllCOMPortDevices():
            self._comport_value.setCurrentText(port)
        else:
            self._settings.setProperty(self._settings.ComPort, self._comport_value.currentText())

        self._comport_description: QtWidgets.QLabel = QtWidgets.QLabel("-> " + COMUtils.getDescription(self._comport_value.currentText()), self)
        
        self._comport_label.setFont(MEDIUM_FONT)
        self._comport_value.setFont(MEDIUM_FONT)
        self._comport_description.setFont(MEDIUM_FONT)
        self._comport_value.currentTextChanged.connect(self._onComPortChanged)

        # NOTE: start button
        self._connect_button: QtWidgets.QPushButton = QtWidgets.QPushButton(self._assets.get("play"), self._language.get(self._language.Connect), self)
        self._connect_button.clicked.connect(self._onConnect)
        self._connect_button.setFont(BIG_FONT)
        self._connect_button.setIconSize(QtCore.QSize(BIG_SIZE, BIG_SIZE))

        hbox_comport: QtWidgets.QHBoxLayout = QtWidgets.QHBoxLayout()
        hbox_comport.addWidget(self._comport_label)
        hbox_comport.addWidget(self._comport_value)
        hbox_comport.addWidget(self._comport_description)

        layout: QtWidgets.QVBoxLayout = QtWidgets.QVBoxLayout()
        layout.addLayout(hbox_top)
        layout.addWidget(self._info_label)
        layout.addStretch()
        layout.addWidget(self._line0)
        layout.addLayout(hbox_tank)
        layout.addWidget(self._line1)
        layout.addLayout(hbox_calibration)
        layout.addWidget(self._line2)
        layout.addLayout(hbox_target)
        layout.addWidget(self._line3)
        layout.addLayout(hbox_comport)
        layout.addWidget(self._connect_button)
        layout.setSpacing(MEDIUM_SIZE)

        self.setLayout(layout)

    def _onImportCalibration(self) -> None:
        fic = QtWidgets.QFileDialog.getOpenFileName(self, "Abrir Ficheiro", "", "Text Files (*.csv *.txt)")
        try:
            x, y = self._settings.loadCurveFromPath(fic)
            self._settings.saveCurve(CALIBRATION_FILENAME, [x,y])
        except ValueError as err:
            QtWidgets.QMessageBox.warning(self, self._language.get(self._language.FileProblem), self._language.get(self._language.UnableToOpenFile))

    def _onEditCalibration(self) -> None:
        edit_dialog = EditDialog(self.parent(), target=CALIBRATION_FILENAME, settings=self._settings, language=self._language, unit=self._unit, observer=self._observer, assets=self._assets)
        edit_dialog.show()

    def _onInfo(self, text:str) -> None:
        self._info_label.setText(text)

    def _onEmptyTank(self) -> None:
        self._observer.Signal.EmptyTank.emit()

    def _onFillTank(self) -> None:
        self._observer.Signal.FillTank.emit()

    def _onTargetPressure(self) -> None:
        value = self._target_value.value()
        self._observer.Signal.NewTargetPressure.emit(value)

    def _onComPortChanged(self) -> None:
        port = self._comport_value.currentText()
        self._settings.setProperty(self._settings.ComPort, port)
        self._comport_description.setText("-> " + COMUtils.getDescription(self._comport_value.currentText()))

    def _onPressureChange(self, pressure:float) -> None:
        self._pressure_edit.setText("{:.2f} kPa".format(pressure))

    def setConnectionButtonState(self, flag:bool) -> None:
        if not flag:
            self._connect_button.setIcon(self._assets.get("play"))
            self._connect_button.setText(self._language.get(self._language.Connect))
        else:
            self._connect_button.setIcon(self._assets.get("stop"))
            self._connect_button.setText(self._language.get(self._language.Disconnect))

    def _onConnect(self) -> None:
        self._observer.Signal.Connect.emit()


class MiniMainWindow(QtWidgets.QMainWindow):
    """
    This is the Main Window for Prime. It stores the permanent data and
    initializes all the manager objects.
    """
    def __init__(self, name:str, version:str, user_folder:str):
        QtWidgets.QMainWindow.__init__(self)

        self._name: str = name
        self._version: str = version
        self._user_folder: str = user_folder
        self.setWindowTitle(self._name + " " + self._version)

        self._settings: Settings = Settings(user_folder=user_folder, name=name, version=version)
        self._language: Language = Language(settings=self._settings)
        self._observer: Observer = Observer()
        self._observer.Signal.Connect.connect(self._onConnection)
        self._observer.Signal.NewTargetPressure.connect(self._onNewTargetPressure)
        self._observer.Signal.FillTank.connect(self._fillTank)
        self._observer.Signal.EmptyTank.connect(self._emptyTank)

        # NOTE: units object (for conversion)
        self._unit: Unit = Unit(settings=self._settings)

        # NOTE: assets object
        self._assets: Assets = Assets()

        # NOTE: units object (for conversion)
        self._unit: Unit = Unit(settings=self._settings)

        self._central_widget: CentralWidget = CentralWidget(self, settings=self._settings, language=self._language, unit=self._unit, observer=self._observer, assets=self._assets)
        self.setCentralWidget(self._central_widget)

        self._connection_thread_flag: bool = False
        self._connection_thread_event: Event = None
        self._connection_thread: Thread = None

        # NOTE: setting up window icon
        self.setWindowIcon(self._assets.get("logo"))

        # NOTE: building menu.
        self._buildMenuBar()

        # NOTE: Maximizing on startup
        self.showMaximized()

    def _buildMenuBar(self):
        """
        Adding the top menu to this application.
        """
        self._file_menu:QtWidgets.QMenu = self.menuBar().addMenu(self._language.get(self._language.File))
        self._settings_menu: QtWidgets.QMenu = self.menuBar().addMenu(self._language.get(self._language.Settings))
        self._about_menu: QtWidgets.QMenu = self.menuBar().addMenu(self._language.get(self._language.About))

        self._quit_action: QtWidgets.QAction = QtWidgets.QAction(self._assets.get("close"), self._language.get(self._language.Quit), self)
        self._quit_action.triggered.connect(self._onExit)

        self._file_menu.addSeparator()
        self._file_menu.addAction(self._quit_action)

        self._preferences_action: QtWidgets.QAction = QtWidgets.QAction(self._assets.get("gear"), self._language.get(self._language.Preferences), self)
        self._preferences_action.triggered.connect(self._onPreferences)

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

    def _emptyTank(self):
        if self._serial != None:
            self._observer.Signal.SendInfo.emit(self._language.get(self._language.EmptyingTank))
            self._serial.write(str("X").encode())
            print("MiniMainWindow::_emptyTank :", str("Ok"))
        else:
            QtWidgets.QMessageBox.warning(self, self._language.get(self._language.NoConnection), self._language.get(self._language.YouMustOpenAConnection))
        
    def _fillTank(self):
        if self._serial != None:
            self._observer.Signal.SendInfo.emit(self._language.get(self._language.FillingTank))
            self._serial.write(str("Y").encode())
            print("MiniMainWindow::_fillTank :", str("Ok"))
        else:
            QtWidgets.QMessageBox.warning(self, self._language.get(self._language.NoConnection), self._language.get(self._language.YouMustOpenAConnection))

    def _onNewTargetPressure(self, value:float) -> None:
        if self._serial is not None:
            self._serial.write(str(int(value)).encode())
            print("MiniMainWindow::_onNewTargetPressure : new target pressure ->", str(value))

    def _onExit(self) -> None:
        self.close()

    def closeEvent(self, event) -> None:
        reply = QtWidgets.QMessageBox.question(self, self._language.get(self._language.Quit) + " " + self._name + "?", 'Are you sure you want to quit?', QtWidgets.QMessageBox.Yes | QtWidgets.QMessageBox.No, QtWidgets.QMessageBox.No)
        if reply == QtWidgets.QMessageBox.Yes:
            self._settings.save()
            print("MiniMainWindow::closeEvent : quitting software at: ", time.asctime())
            QtWidgets.QApplication.instance().quit()
        else:
            event.ignore()

    def _onConnection(self) -> None:
        if not self._connection_thread_flag:
            try:
                x, y = self._settings.loadCurve(CALIBRATION_FILENAME)
                if len(x) > 2:
                    z = np.polyfit(x, y, 2)
                    self._p = np.poly1d(z)
                else:
                    self._p = None

                port = self._settings.getProperty(self._settings.ComPort)
                self._serial: serial.Serial = serial.Serial(port, 9600)
                self._thread_flag: bool = True
                self._connection_thread_event = Event()
                self._connection_thread = Thread(target=self._onReadPressureThread)
                self._connection_thread.start()
                self._connection_thread_flag = True
                self._central_widget.setConnectionButtonState(True)
            except OSError as err:
                self._central_widget.setConnectionButtonState(False)
                QtWidgets.QMessageBox.warning(self, self._language.get(self._language.UnableToConnect), self._language.get(self._language.UnableToOpenPort))
        else:
            self._serial.close()
            self._serial = None
            self._connection_thread_flag = False
            self._connection_thread_event.set()
            self._connection_thread.join()
            self._connection_thread_flag = False
            self._central_widget.setConnectionButtonState(False)

    def _onReadPressureThread(self) -> None:
        while self._connection_thread_flag:
            value = self._serial.readline()
            try:
                val = str(value).replace("\\r","").replace("\\n","").replace("''","").replace("b","").replace("'","").replace("'","")
                if val == "IC_H":
                    self._observer.Signal.SendInfo(self._language.get(self._language.ReachedBeginning))
                elif val == "FC_H":
                    self._observer.Signal.SendInfo(self._language.get(self._language.ReachedEnd))
                elif val == "FC_L":
                    pass
                elif val == "IC_L":
                    pass
                else:
                    if self._p is not None:
                        self._observer.Signal.ValuePressureChanged.emit(self._p(float(val)))
                    else:
                        self._observer.Signal.ValuePressureChanged.emit(float(val))
                        print(2)
            except ValueError as error:
                print(error)
            self._connection_thread_event.wait(0.2)

