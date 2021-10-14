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

# Qt libraries
from PyQt5 import QtCore, QtGui, QtWidgets

# Local libraries
from src.settings import Settings, Observer
from src.language import Language
from src.unit     import Unit
from src.utils    import COMUtils
from src.assets   import Assets
from .MainDialogs import InfoDialog, UnitsDialog, HorizontalLine, PreferencesDialog, EditDialog


class CalibrationToolbar(QtWidgets.QToolBar):
    Create: QtCore.pyqtSignal = QtCore.pyqtSignal()
    Delete: QtCore.pyqtSignal = QtCore.pyqtSignal()
    Edit: QtCore.pyqtSignal = QtCore.pyqtSignal()
    Import: QtCore.pyqtSignal = QtCore.pyqtSignal()
    Export: QtCore.pyqtSignal = QtCore.pyqtSignal()

    def __init__(self, parent=None, settings:Settings=None, language:Language=None, unit:Unit=None, observer:Observer=None, assets:Assets=None):
        QtWidgets.QToolBar.__init__(self, parent)

        self._settings: Settings = settings

        self._language: Language = language
        self._unit: Unit = unit

        self._observer: Observer = observer

        self._assets: Assets = assets

        self._build()

        self.setHasSelection(False)

    def setHasSelection(self, flag:bool) -> None:
        self._delete_action.setEnabled(flag)
        self._edit_action.setEnabled(flag)

    def _build(self):
        self._create_action = self.addAction(self._assets.get('plus'),"")
        self._create_action.setToolTip(self._language.get(self._language.CreateCalibrationCurveTooltip))

        self._delete_action = self.addAction(self._assets.get('delete'),"")
        self._delete_action.setToolTip(self._language.get(self._language.DeleteCalibrationCurveTooltip))

        self._edit_action = self.addAction(self._assets.get('edit'),"")
        self._edit_action.setToolTip(self._language.get(self._language.EditCalibrationCurveTooltip))

        # self.addSeparator()

        # self._import_action = self.addAction(self._assets.get('import'),"")
        # self._import_action.setToolTip(self._language.get(self._language.ImportCalibrationCurveTooltip))

        # self._export_action = self.addAction(self._assets.get('export'),"")
        # self._export_action.setToolTip(self._language.get(self._language.ExportCalibrationCurveTooltip))

        self._create_action.triggered.connect(self._onCreateAction)
        self._delete_action.triggered.connect(self._onDeleteAction)
        self._edit_action.triggered.connect(self._onEditAction)
        # self._import_action.triggered.connect(self._onImportAction)
        # self._export_action.triggered.connect(self._onExportAction)

    def _onCreateAction(self) -> None:
        self.Create.emit()

    def _onDeleteAction(self) -> None:
        self.Delete.emit()

    def _onEditAction(self) -> None:
        self.Edit.emit()

    def _onImportAction(self) -> None:
        self.Import.emit()

    def _onExportAction(self) -> None:
        self.Export.emit()


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
        self._calibration_toolbar.Create.connect(self._onCreateCurve)
        self._calibration_toolbar.Delete.connect(self._onDeleteCurve)
        self._calibration_toolbar.Edit.connect(self._onEditCurve)
        self._calibration_toolbar.Import.connect(self._onImportCurve)
        self._calibration_toolbar.Export.connect(self._onExportCurve)
        
        self._calibration_list: QtWidgets.QListWidget = QtWidgets.QListWidget(self)
        self._populateCurveList()
        self._calibration_list.itemSelectionChanged.connect(self._onCurveSelectionChanged)
        self._calibration_list.itemDoubleClicked.connect(self._onEditCurve)

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

        self._comport_value.currentTextChanged.connect(self._onComPortChanged)

        # NOTE: start button
        self._connect_button: QtWidgets.QPushButton = QtWidgets.QPushButton(self._assets.get("play"), self._language.get(self._language.Connect), self)
        self._connect_button.clicked.connect(self._onConnect)

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

    def setConnectionButtonState(self, flag:bool) -> None:
        if not flag:
            self._connect_button.setIcon(self._assets.get("stop"))
            self._connect_button.setText(self._language.get(self._language.Connect))
        else:
            self._connect_button.setIcon(self._assets.get("play"))
            self._connect_button.setText(self._language.get(self._language.Disconnect))

    def _onConnect(self) -> None:
        self._observer.Signal.Connect.emit()

    def _languageChanged(self) -> None:
        # self._pressure_label.setText(self._language.get(self._language.Pressure) + ":")
        # self._volume_label.setText(self._language.get(self._language.Volume) + ":")
        # self._target_label.setText(self._language.get(self._language.TargetPressure) + ":")
        pass

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

    def _onComPortChanged(self) -> None:
        port = self._comport_value.currentText()
        self._settings.setProperty(self._settings.ComPort, port)

    def _populateCurveList(self) -> None:
        self._calibration_list.clear()
        curves = self._settings.calibrationCurves()
        self._calibration_list.addItems(curves)

    def _onCreateCurve(self) -> None:
        name = QtWidgets.QInputDialog.getText(self.parent(), self._language.get(self._language.CurveName), self._language.get(self._language.ProvideNameForNewCurve))
        if name != "":
            if name in self._settings.calibrationCurves():
                QtWidgets.QMessageBox.warning(self.parent(), self._language.get(self._language.NameAlreadyExists), self._language.get(self._language.YouNeedToPickANewNAme))
            else:
                self._settings.createCurve(name[0])
                self._populateCurveList()

    def _onDeleteCurve(self) -> None:
        reply = QtWidgets.QMessageBox.question(self.parent(), self._language.get(self._language.DeleteCalibrationCurve), self._language.get(self._language.AreYouSureYouWantToDeleteCurve))
        if reply == QtWidgets.QMessageBox.Yes:
            name = self._curveSelection()
            self._settings.deleteCurve(name[0])
            self._populateCurveList()

    def _onEditCurve(self) -> None:
        name = self._curveSelection()
        edit_dialog = EditDialog(self.parent(), target=name[0], settings=self._settings, language=self._language, unit=self._unit, observer=self._observer, assets=self._assets)
        edit_dialog.show()

    def _onImportCurve(self) -> None:
        pass

    def _onExportCurve(self) -> None:
        pass

    def _curveSelection(self) -> List[str]:
        items = self._calibration_list.selectedItems()
        text = []
        for item in items:
            text.append(item.text())
        return text

    def _onCurveSelectionChanged(self) -> None:
        items = self._curveSelection()
        if len(items) > 0:
            self._calibration_toolbar.setHasSelection(True)
        else:
            self._calibration_toolbar.setHasSelection(False)