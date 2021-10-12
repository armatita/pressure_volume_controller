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


# Local libraries
from src.utils import SingletonMetaClass
from src.settings import Settings


class Language(metaclass=SingletonMetaClass):
    """
    The `Language` is a singleton class (all instances point to the same reference).

    The `Language` stores all data related to language and translation.
    """
    Start: str = "Start"
    Pressure: str = "Pressure"
    Volume: str = "Volume"
    ComPort: str = "COM Port"
    TargetPressure: str = "Target Pressure"

    File: str = "File"
    Edit: str = "Edit"
    View: str = "View"

    RunManager: str = "Run Manager"

    CalibrationTitle: str = "Calibration Curve"
    RealTimeTitle: str = "Real Time Data"
    TargetTitle: str = "Input Data"
    ConfigurationTitle: str = "Configuration"
    Validate: str = "Validate"
    Connect: str = "Connect"

    Quit: str = "Quit"


    CreateCalibrationCurveTooltip: str = "Create a new calibration curve."
    DeleteCalibrationCurveTooltip: str = "Delete a new calibration curve."
    ImportCalibrationCurveTooltip: str = "Import a new calibration curve."
    ExportCalibrationCurveTooltip: str = "Export a new calibration curve."
    EditCalibrationCurveTooltip: str = "Edit a new calibration curve."

    OPTION_PORTUGUESE: str = "Portuguese"
    OPTION_ENGLISH: str = "English"
    def __init__(self, settings:str) -> None:
        self._settings: Settings = settings
        self._settings.Signal.LanguageChanged.connect(self._languageChanged)

        self._language: str = self._settings.getProperty(self._settings.Language)

        self._pt = {
            self.Start: "Correr",
            self.Pressure: "Pressão",
            self.Volume: "Volume",
            self.ComPort: "Porta COM",
            self.TargetPressure: "Pressão Alvo",
            self.File: "Ficheiro",
            self.Edit: "Editar",
            self.View: "Ver",
            self.RunManager: "Gestor de Cenários",
            self.CalibrationTitle: "Curva de Calibração",
            self.RealTimeTitle: "Dados em Tempo Real",
            self.TargetTitle: "Dados de Entrada",
            self.ConfigurationTitle: "Configuração",
            self.Validate: "Validar",
            self.Connect: "Conectar",
            self.Quit: "Sair",
            self.CreateCalibrationCurveTooltip: "Criar nova curva de calibração.",
            self.DeleteCalibrationCurveTooltip: "Excluir curva de calibração.",
            self.ExportCalibrationCurveTooltip: "Exportar curva de calibração.",
            self.ImportCalibrationCurveTooltip: "Importar curva de calibração.",
            self.EditCalibrationCurveTooltip: "Editar curva de calibração."
        }

    def get(self, key:str) -> str:
        if self._language == self.OPTION_ENGLISH:
            return key
        elif self._language == self.OPTION_PORTUGUESE:
            return self._pt[key]

    def _languageChanged(self, language:str) -> None:
        self._language = language