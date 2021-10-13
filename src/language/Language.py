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
    Disconnect: str = "Disconnect"

    Quit: str = "Quit"
    Units: str = "Units"
    Preferences: str = "Preferences"
    Information: str = "Information"
    License: str = "License"
    Help: str = "Help"
    Close: str = "Close"
    Language: str = "Language"

    Unit: str = "Unit"
    Precision: str = "Decimals"

    Cancel: str = "Cancel"
    Apply: str = "Apply"

    Raw: str = "Raw"
    Calibrated: str = "Calibrated"

    CreateCalibrationCurveTooltip: str = "Create a new calibration curve."
    DeleteCalibrationCurveTooltip: str = "Delete the selected calibration curve."
    ImportCalibrationCurveTooltip: str = "Import the selected calibration curve."
    ExportCalibrationCurveTooltip: str = "Export the selected calibration curve."
    EditCalibrationCurveTooltip: str = "Edit the selected calibration curve."

    InfoMessage: str = "This software is to be used for the management of a Pressure-Volume controller. It was originally created by: Pedro Correia and José Correia."
    LicenseMessage: str = "This software has been released under the MIT License."
    HelpMessage: str = "Currently there is no support for this application."
    EditCurve: str = "Edit calibration curve"
    UnableToConnect: str = "Unable to connect"
    UnableToOpenPort: str = "Unable to open port. Make sure you have a connected device."

    AsteriskRestartNeeded: str = "* You'll need to restart the software for this option to take effect."

    CurveName: str = "Curve name"
    ProvideNameForNewCurve: str = "Provide a name for the new curve."
    NameAlreadyExists: str = "Name already exists!"
    YouNeedToPickANewNAme: str = "You need to pick an unique name."
    DeleteCalibrationCurve: str = "Delete calibration curve"
    AreYouSureYouWantToDeleteCurve: str = "Are you sure you want to delete the selected calibration curve?"

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
            self.Disconnect: "Desconectar",
            self.Quit: "Sair",
            self.Units: "Unidades",
            self.Language: "Idioma",
            self.Preferences: "Preferências",
            self.Information: "Informação",
            self.License: "Licensa",
            self.Help: "Ajuda",
            self.Close: "Fechar",
            self.Unit: "Unidade",
            self.Precision: "Décimais",
            self.Cancel: "Cancelar",
            self.Apply: "Salvar",
            self.Raw: "Bruto",
            self.Calibrated: "Calibrado",
            self.EditCurve: "Editar curva de calibração",
            self.CurveName: "Nome da curva de calibração",
            self.ProvideNameForNewCurve: "Dê um nome para a curva de calibração.",
            self.NameAlreadyExists: "Nome já existe!",
            self.YouNeedToPickANewNAme: "Precisa de escolher outro nome.",
            self.DeleteCalibrationCurve: "Excluir curva de calibração",
            self.AreYouSureYouWantToDeleteCurve: "Tem a certeza que quer excluir curva de calibração?",
            self.InfoMessage: "Este programa é para ser utilizado na gestão de operações the controlo de pressão-volume. Foi criado originalmente por: Pedro Correia, José Correia.",
            self.LicenseMessage: "Este programa é distribuido sobre a licença MIT.",
            self.HelpMessage: "De momento não está disponível suporte para esta aplicação.",
            self.UnableToConnect: "Impossível de conectar",
            self.UnableToOpenPort: "Abertura de porta impossível. Certifique-se que tem um aparelho compatível conectado.",
            self.CreateCalibrationCurveTooltip: "Criar nova curva de calibração.",
            self.DeleteCalibrationCurveTooltip: "Excluir curva de calibração.",
            self.ExportCalibrationCurveTooltip: "Exportar curva de calibração.",
            self.ImportCalibrationCurveTooltip: "Importar curva de calibração.",
            self.EditCalibrationCurveTooltip: "Editar curva de calibração.",
            self.AsteriskRestartNeeded: "* Necessita relançar o programa para esta opção ficar em efeito."
        }

    def get(self, key:str) -> str:
        if self._language == self.OPTION_ENGLISH:
            return key
        elif self._language == self.OPTION_PORTUGUESE:
            return self._pt[key]

    def options(self) -> List[str]:
        return self.OPTION_ENGLISH, self.OPTION_PORTUGUESE

    def _languageChanged(self, language:str) -> None:
        self._language = language