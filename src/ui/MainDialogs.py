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
from PyQt5 import QtCore, QtGui, QtWidgets

# Local libraries
from src.settings import Settings, Observer
from src.language import Language
from src.unit     import Unit
from src.assets   import Assets


class UnitsDialog(QtWidgets.QDialog):
    def __init__(self, parent=None, settings:Settings=None, language:Language=None, unit:Unit=None, observer:Observer=None, assets:Assets=None):
        QtWidgets.QDialog.__init__(self, parent)

        self._settings: Settings = settings
        self._language: Language = language
        self._unit: Unit = unit
        self._observer: Observer = observer
        self._assets: Assets = assets


class InfoDialog(QtWidgets.QDialog):
    def __init__(self, parent=None, icon:QtGui.QIcon=None, text:str=None, title:str=None, close_text:str=None):
        QtWidgets.QDialog.__init__(self, parent)

        self.setWindowTitle(title)

        self._image_label: QtWidgets.QLabel = QtWidgets.QLabel("", self)
        self._image_label.setPixmap(icon.pixmap(QtCore.QSize(64, 64)))

        self._text_label: QtWidgets.QLabel = QtWidgets.QLabel(text, self)
        self._text_label.setWordWrap(True)

        self._close_button: QtWidgets.QPushButton = QtWidgets.QPushButton(close_text, self)
        self._close_button.clicked.connect(self._onClose)

        vbox: QtWidgets.QVBoxLayout = QtWidgets.QVBoxLayout()
        vbox.addWidget(self._image_label)
        vbox.addStretch()

        hbox: QtWidgets.QHBoxLayout = QtWidgets.QHBoxLayout()
        hbox.addLayout(vbox)
        hbox.addWidget(self._text_label)

        hbox_bottom: QtWidgets.QHBoxLayout = QtWidgets.QHBoxLayout()
        hbox_bottom.addStretch()
        hbox_bottom.addWidget(self._close_button)

        layout: QtWidgets.QVBoxLayout = QtWidgets.QVBoxLayout()
        layout.addLayout(hbox)
        layout.addLayout(hbox_bottom)
        layout.setSpacing(15)
        self.setLayout(layout)

    def _onClose(self) -> None:
        self.close()

