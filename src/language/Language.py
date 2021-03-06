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
    Import: str = "Import"

    EmptyTank: str = "Empty Tank"
    FillTank: str = "Fill Tank"

    CreateCalibrationCurveTooltip: str = "Create a new calibration curve."
    DeleteCalibrationCurveTooltip: str = "Delete the selected calibration curve."
    ImportCalibrationCurveTooltip: str = "Import the selected calibration curve."
    ExportCalibrationCurveTooltip: str = "Export the selected calibration curve."
    EditCalibrationCurveTooltip: str = "Edit the selected calibration curve."

    InfoMessage: str = "This software is to be used for the management of a Pressure-Volume controller. It was originally created by: Pedro Correia and Jos?? Correia."
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
    AreYouSureYouWishToExit: str = 'Are you sure you want to quit?'

    EmptyingTank: str = "Emptying Tank"
    FillinTank: str = "Filling Tank"
    NoConnection: str = "No Connection"
    YouMustOpenAConnection: str = "You must open a connection first."

    FileProblem: str = "Problem with File"
    UnableToOpenFile: str = "Unable to open File. Please check the format."
    ReachedBeginning: str = "Reached beginning for course."
    ReachedEnd: str = "Reached end for course."

    OPTION_PORTUGUESE: str = "Portuguese"
    OPTION_ENGLISH: str = "English"
    def __init__(self, settings: Settings) -> None:
        self._settings: Settings = settings
        self._settings.Signal.LanguageChanged.connect(self._languageChanged)

        self._language: str = self._settings.getProperty(self._settings.Language)

        self._pt = {
            self.Start: "Correr",
            self.Pressure: "Press??o",
            self.Volume: "Volume",
            self.ComPort: "Porta COM",
            self.TargetPressure: "Press??o Alvo",
            self.File: "Ficheiro",
            self.Edit: "Editar",
            self.View: "Ver",
            self.About: "Acerca de...",
            self.Settings: "Defini????es",
            self.RunManager: "Gestor de Cen??rios",
            self.CalibrationTitle: "Curva de Calibra????o",
            self.RealTimeTitle: "Dados em Tempo Real",
            self.TargetTitle: "Dados de Entrada",
            self.ConfigurationTitle: "Configura????o",
            self.Validate: "Validar",
            self.Connect: "Conectar",
            self.Disconnect: "Desconectar",
            self.Quit: "Sair",
            self.Units: "Unidades",
            self.Language: "Idioma",
            self.Preferences: "Prefer??ncias",
            self.Information: "Informa????o",
            self.License: "Licensa",
            self.Help: "Ajuda",
            self.Close: "Fechar",
            self.Unit: "Unidade",
            self.Precision: "D??cimais",
            self.Cancel: "Cancelar",
            self.Apply: "Salvar",
            self.Raw: "Bruto",
            self.Calibrated: "Calibrado",
            self.Import: "Importar",
            self.EmptyTank: "Esvaziar Tanque",
            self.FillTank: "Encher Tanque",
            self.EmptyingTank: "A esvaziar tanque.",
            self.FillinTank: "A encher tanque.",
            self.NoConnection: "Sem conex??o",
            self.YouMustOpenAConnection: "Tem de abrir uma conex??o primeiro.",
            self.FileProblem: "Problema com ficheiro",
            self.UnableToOpenFile: "N??o foi poss??vel abrir o ficheiro. Verifique a formata????o.",
            self.EditCurve: "Editar curva de calibra????o",
            self.CurveName: "Nome da curva de calibra????o",
            self.ProvideNameForNewCurve: "D?? um nome para a curva de calibra????o.",
            self.NameAlreadyExists: "Nome j?? existe!",
            self.YouNeedToPickANewNAme: "Precisa de escolher outro nome.",
            self.DeleteCalibrationCurve: "Excluir curva de calibra????o",
            self.AreYouSureYouWantToDeleteCurve: "Tem a certeza que quer excluir curva de calibra????o?",
            self.AreYouSureYouWishToExit: 'Tem a certeza que quer sair?',
            self.InfoMessage: "Este programa ?? para ser utilizado na gest??o de opera????es the controlo de press??o-volume. Foi criado originalmente por: Pedro Correia, Jos?? Correia.",
            self.LicenseMessage: "Este programa ?? distribuido sobre a licen??a MIT.",
            self.HelpMessage: "De momento n??o est?? dispon??vel suporte para esta aplica????o.",
            self.UnableToConnect: "Imposs??vel de conectar",
            self.UnableToOpenPort: "Abertura de porta imposs??vel. Certifique-se que tem um aparelho compat??vel conectado.",
            self.ReachedBeginning: "Chegou ao ??nicio do percurso.",
            self.ReachedEnd: "Chegou ao fim do percurso.",
            self.CreateCalibrationCurveTooltip: "Criar nova curva de calibra????o.",
            self.DeleteCalibrationCurveTooltip: "Excluir curva de calibra????o.",
            self.ExportCalibrationCurveTooltip: "Exportar curva de calibra????o.",
            self.ImportCalibrationCurveTooltip: "Importar curva de calibra????o.",
            self.EditCalibrationCurveTooltip: "Editar curva de calibra????o.",
            self.AsteriskRestartNeeded: "* Necessita relan??ar o programa para esta op????o ficar em efeito."
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