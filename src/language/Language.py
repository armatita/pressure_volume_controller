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
    Settings: str = "Settings"
    About: str = "About"

    RunManager: str = "Run Manager"

    CalibrationTitle: str = "Calibration Curve"
    RealTimeTitle: str = "Real Time Data"
    TargetTitle: str = "Input Data"
    ConfigurationTitle: str = "Configuration"
    Validate: str = "Validate"
    Connect: str = "Connect"

    Quit: str = "Quit"
    Units: str = "Units"
    Preferences: str = "Preferences"
    Information: str = "Information"
    License: str = "License"
    Help: str = "Help"
    Close: str = "Close"

    CreateCalibrationCurveTooltip: str = "Create a new calibration curve."
    DeleteCalibrationCurveTooltip: str = "Delete the selected calibration curve."
    ImportCalibrationCurveTooltip: str = "Import the selected calibration curve."
    ExportCalibrationCurveTooltip: str = "Export the selected calibration curve."
    EditCalibrationCurveTooltip: str = "Edit the selected calibration curve."

    InfoMessage: str = "This software is to be used for the management of a Pressure-Volume controller. It was originally created by: Pedro Correia and José Correia."
    LicenseMessage: str = "This software has been released under the MIT License."
    HelpMessage: str = "Currently there is no support for this application."

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
            self.About: "Acerca de...",
            self.Settings: "Definições",
            self.RunManager: "Gestor de Cenários",
            self.CalibrationTitle: "Curva de Calibração",
            self.RealTimeTitle: "Dados em Tempo Real",
            self.TargetTitle: "Dados de Entrada",
            self.ConfigurationTitle: "Configuração",
            self.Validate: "Validar",
            self.Connect: "Conectar",
            self.Quit: "Sair",
            self.Units: "Unidades",
            self.Preferences: "Preferências",
            self.Information: "Informação",
            self.License: "Licensa",
            self.Help: "Ajuda",
            self.Close: "Fechar",
            self.InfoMessage: "Este programa é para ser utilizado na gestão de operações the controlo de pressão-volume. Foi criado originalmente por: Pedro Correia, José Correia.",
            self.LicenseMessage: "Este programa é distribuido sobre a licença MIT.",
            self.HelpMessage: "De momento não está disponível suporte para esta aplicação.",
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