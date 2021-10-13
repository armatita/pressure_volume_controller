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
from src.assets   import Assets


class HTMLStyle(QtWidgets.QProxyStyle):
    """
    A QProxyStyle which can be used to render HTML/Rich text inside
    QComboBoxes, QCheckBoxes and QRadioButtons.  Note that for QComboBox,
    this does NOT alter rendering of the items when you're choosing from
    the list.  For that you'll need to set an item delegate.

    SEE: https://apocalyptech.com/linux/qt/qcombobox_html/htmlwidgets.py
    """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.text_doc = QtGui.QTextDocument()
        font: QtGui.QFont = QtGui.QFont()
        font_size:int = font.pointSize()
        self.text_doc.setDefaultStyleSheet("* {font-size: " + str(font_size) + "}")

    def drawItemText(self, painter, rect, alignment, pal, enabled, text, text_role):
        """
        This is what draws the text - we use an internal QTextDocument
        to do the formatting.  The general form of this function follows the
        C++ version at https://github.com/qt/qtbase/blob/5.9/src/widgets/styles/qstyle.cpp

        Note that we completely ignore the `alignment` and `enabled` variable.
        This is always left-aligned, and does not currently support disabled
        widgets.
        """
        if not text or text == '':
            return

        # Save our current pen if we need to
        saved_pen = None
        if text_role != QtGui.QPalette.NoRole:
            saved_pen = painter.pen()
            painter.setPen(QtGui.QPen(pal.brush(text_role), saved_pen.widthF()))

        # Render the text.  There's a bit of voodoo here with the rectangles
        # and painter translation; there was various bits of finagling necessary
        # to get this to seem to work with both combo boxes and checkboxes.
        # There's probably better ways to be doing this.
        margin = 3
        painter.save()
        painter.translate(rect.left()-margin, 0)
        self.text_doc.setHtml(text)
        self.text_doc.drawContents(painter,
                QtCore.QRectF(rect.adjusted(-rect.left(), 0, -margin, 0)))
        painter.restore()

        # Restore our previous pen if we need to
        if text_role != QtGui.QPalette.NoRole:
            painter.setPen(saved_pen)

    def sizeFromContents(self, contents_type, option, size, widget=None):
        """
        For ComboBoxes, this gets called to determine the size of the list of
        options for the comboboxes.  This is too wide for our HTMLComboBox, so
        we pull in the width from there instead.
        """
        width = size.width()
        height = size.height()
        if contents_type == self.CT_ComboBox and widget and type(widget) == QtWidgets.QComboBox:
            size = widget.sizeHint()
            width = size.width() # + widget.width_adjust_contents
        return super().sizeFromContents(contents_type,
                option,
                QtCore.QSize(width, height),
                widget)


class HTMLDelegate(QtWidgets.QStyledItemDelegate):
    """
    Class for use in a QComboBox to allow HTML Text.  I'm still a bit
    miffed that this isn't just a default part of Qt.  There's a lot of
    Google hits from people looking to do this, most suggesting
    implementing something like this, but so far I've only found this
    one actual implementation, at the end of a thread here:
    http://www.qtcentre.org/threads/62867-HTML-rich-text-delegate-and-text-centering-aligning-code-amp-pictures

    I suspect this implementation is probably heavier than we actually
    need, but it seems fairly voodooey anyway.  And keep in mind that
    after all this, you've still got to produce a completely bloody
    different solution for displaying the currently-selected item in
    the QComboBox; this is only for the list of choices.  I'm happy
    to be leaving Gtk but this kind of thing makes the move more
    bittersweet than it should be.

    SEE: https://apocalyptech.com/linux/qt/qcombobox_html/htmlwidgets.py
    """

    def __init__(self, parent=None):
        super().__init__()
        self.doc = QtGui.QTextDocument(self)

    def paint(self, painter, option, index):
        """
        Paint routine for our items in the QComboBox
        """

        # Save our painter so it can be restored later
        painter.save()

        # Copy our option var so we can make some changes without modifying
        # the underlying object
        options = QtWidgets.QStyleOptionViewItem(option)
        self.initStyleOption(options, index)

        # Add in our data to our QTextDocument
        self.doc.setHtml(options.text)

        # Acquire our style
        if options.widget is None:
            style = QtWidgets.QApplication.style()
        else:
            style = options.widget.style()

        # Draw a barebones version of the control which doesn't have any
        # text specified - this is to render the background, basically, so
        # that when we're mousing over one of the items the bg changes.
        options.text = ''
        style.drawControl(QtWidgets.QStyle.CE_ItemViewItem, options, painter)

        # Grab a PaintContext and set our text color depending on if we're
        # selected or not
        ctx = QtGui.QAbstractTextDocumentLayout.PaintContext()
        if option.state & QtWidgets.QStyle.State_Selected:
            ctx.palette.setColor(QtGui.QPalette.Text, option.palette.color(
                QtGui.QPalette.Active, QtGui.QPalette.HighlightedText))
        else:
            ctx.palette.setColor(QtGui.QPalette.Text, option.palette.color(
                QtGui.QPalette.Active, QtGui.QPalette.Text))

        # Calculating some rendering geometry.
        textRect = style.subElementRect(
            QtWidgets.QStyle.SE_ItemViewItemText, options)
        textRect.adjust(3, 0, 0, 0)
        painter.translate(textRect.topLeft())
        painter.setClipRect(textRect.translated(-textRect.topLeft()))

        # Now, finally, actually render the text
        self.doc.documentLayout().draw(painter, ctx)

        # Restore our paintbrush
        painter.restore()

    def sizeHint(self, option, index):
        """
        Our size.  This actually gets called before `paint`, I think, and therefore
        is called before our text has actually been loaded into the QTextDocument,
        but apparently seems to Do The Right Thing Anyway.
        """
        return QtCore.QSize(self.doc.idealWidth(), self.doc.size().height())


class HorizontalLine(QtWidgets.QFrame):
    '''
    Horizontal Line.
    '''
    def __init__(self):
        QtWidgets.QFrame.__init__(self)
        self.setFrameShape(QtWidgets.QFrame.HLine)
        self.setFrameShadow(QtWidgets.QFrame.Sunken)
        self.setSizePolicy(QtWidgets.QSizePolicy.Preferred, QtWidgets.QSizePolicy.Minimum)


class UnitsDialog(QtWidgets.QDialog):
    def __init__(self, parent=None, settings:Settings=None, language:Language=None, unit:Unit=None, observer:Observer=None, assets:Assets=None):
        QtWidgets.QDialog.__init__(self, parent)

        self._settings: Settings = settings
        self._language: Language = language
        self._unit: Unit = unit
        self._observer: Observer = observer
        self._assets: Assets = assets

        self.setWindowTitle(self._language.get(self._language.Units))

        bold_font: QtGui.QFont = QtGui.QFont()
        bold_font.setBold(True)

        self._unit_label: QtWidgets.QLabel = QtWidgets.QLabel(self._language.get(self._language.Unit), self)
        self._unit_label.setFont(bold_font)
        self._precision_label: QtWidgets.QLabel = QtWidgets.QLabel(self._language.get(self._language.Precision), self)
        self._precision_label.setFont(bold_font)

        self._pressure_label: QtWidgets.QLabel = QtWidgets.QLabel(self._language.get(self._language.Pressure) + ":", self)
        self._pressure_unit: QtWidgets.QComboBox = QtWidgets.QComboBox(self)
        self._pressure_unit.setStyle(HTMLStyle())
        self._pressure_unit.setItemDelegate(HTMLDelegate())
        self._pressure_unit.addItems(self._unit.options(self._unit.UnitPressure))
        self._pressure_unit.setCurrentText(self._settings.getProperty(self._settings.UnitPressure))
        self._pressure_precision: QtWidgets.QSpinBox = QtWidgets.QSpinBox(self)
        self._pressure_precision.setRange(0, 10)
        self._pressure_precision.setValue(self._settings.getProperty(self._settings.PrecisionPressure))

        self._volume_label: QtWidgets.QLabel = QtWidgets.QLabel(self._language.get(self._language.Volume) + ":", self)
        self._volume_unit: QtWidgets.QComboBox = QtWidgets.QComboBox(self)
        self._volume_unit.setStyle(HTMLStyle())
        self._volume_unit.setItemDelegate(HTMLDelegate())
        self._volume_unit.addItems(self._unit.options(self._unit.UnitVolume))
        self._volume_unit.setCurrentText(self._settings.getProperty(self._settings.UnitVolume))
        self._volume_precision: QtWidgets.QSpinBox = QtWidgets.QSpinBox(self)
        self._volume_precision.setRange(0, 10)
        self._volume_precision.setValue(self._settings.getProperty(self._settings.PrecisionVolume))

        self._cancel_button: QtWidgets.QPushButton = QtWidgets.QPushButton(self._language.get(self._language.Cancel), self)
        self._cancel_button.clicked.connect(self._onClose)
        self._apply_button: QtWidgets.QPushButton = QtWidgets.QPushButton(self._language.get(self._language.Apply), self)
        self._apply_button.clicked.connect(self._onApply)

        top_layout: QtWidgets.QGridLayout = QtWidgets.QGridLayout()
        i: int = -1
        i += 1
        top_layout.addWidget(self._unit_label, i, 1)
        top_layout.addWidget(self._precision_label, i, 2)
        i += 1
        top_layout.addWidget(self._pressure_label, i, 0)
        top_layout.addWidget(self._pressure_unit, i, 1)
        top_layout.addWidget(self._pressure_precision, i, 2)
        i += 1
        top_layout.addWidget(self._volume_label, i, 0)
        top_layout.addWidget(self._volume_unit, i, 1)
        top_layout.addWidget(self._volume_precision, i, 2)

        layout_bottom: QtWidgets.QHBoxLayout = QtWidgets.QHBoxLayout()
        layout_bottom.addStretch()
        layout_bottom.addWidget(self._apply_button)
        layout_bottom.addWidget(self._cancel_button)

        layout: QtWidgets.QVBoxLayout = QtWidgets.QVBoxLayout()
        layout.addLayout(top_layout)
        layout.addLayout(layout_bottom)

        self.setLayout(layout)

    def _onClose(self) -> None:
        self.close()

    def _onApply(self) -> None:
        pressure_unit: str = self._pressure_unit.currentText()
        pressure_precision: int = self._pressure_precision.value()
        volume_unit: str = self._volume_unit.currentText()
        volume_precision: int = self._volume_precision.value()

        self._settings.setProperty(self._settings.UnitPressure, pressure_unit)
        self._settings.setProperty(self._settings.PrecisionPressure, pressure_precision)
        self._settings.setProperty(self._settings.UnitVolume, volume_unit)
        self._settings.setProperty(self._settings.PrecisionVolume, volume_precision)

        print("UnitsDialog::_onApply : saved unit data as -> Pressure=(", pressure_unit, ",", pressure_precision, ") , Volume=(", volume_unit, ",", volume_precision, ")")

        self._onClose()


class PreferencesDialog(QtWidgets.QDialog):
    def __init__(self, parent=None, settings:Settings=None, language:Language=None, unit:Unit=None, observer:Observer=None, assets:Assets=None):
        QtWidgets.QDialog.__init__(self, parent)

        self._settings: Settings = settings
        self._language: Language = language
        self._unit: Unit = unit
        self._observer: Observer = observer
        self._assets: Assets = assets

        self.setWindowTitle(self._language.get(self._language.Preferences))

        bold_font: QtGui.QFont = QtGui.QFont()
        bold_font.setBold(True)

        self._language_label: QtWidgets.QLabel = QtWidgets.QLabel(self._language.get(self._language.Language) + "*:", self)
        self._language_option: QtWidgets.QComboBox = QtWidgets.QComboBox(self)
        self._language_option.addItems(self._language.options())
        self._language_option.setCurrentText(self._settings.getProperty(self._settings.Language))

        self._asterisk_label: QtWidgets.QLabel = QtWidgets.QLabel(self._language.get(self._language.AsteriskRestartNeeded), self)

        self._cancel_button: QtWidgets.QPushButton = QtWidgets.QPushButton(self._language.get(self._language.Cancel), self)
        self._cancel_button.clicked.connect(self._onClose)
        self._apply_button: QtWidgets.QPushButton = QtWidgets.QPushButton(self._language.get(self._language.Apply), self)
        self._apply_button.clicked.connect(self._onApply)

        top_layout: QtWidgets.QGridLayout = QtWidgets.QGridLayout()
        i: int = -1
        i += 1
        top_layout.addWidget(self._language_label, i, 0)
        top_layout.addWidget(self._language_option, i, 1)
        i += 1
        top_layout.addWidget(self._asterisk_label, i, 0, 1, 2)

        layout_bottom: QtWidgets.QHBoxLayout = QtWidgets.QHBoxLayout()
        layout_bottom.addStretch()
        layout_bottom.addWidget(self._apply_button)
        layout_bottom.addWidget(self._cancel_button)

        layout: QtWidgets.QVBoxLayout = QtWidgets.QVBoxLayout()
        layout.addLayout(top_layout)
        layout.addLayout(layout_bottom)

        self.setLayout(layout)

    def _onClose(self) -> None:
        self.close()

    def _onApply(self) -> None:
        language: str = self._language_option.currentText()
        
        self._settings.setProperty(self._settings.Language, language)

        print("PreferencesDialog::_onApply : saved preferences data as -> Language=(", language, ")")

        self._onClose()


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


class NumericDelegate(QtWidgets.QStyledItemDelegate):
    """
    SEE: https://stackoverflow.com/questions/63149168/how-to-accept-only-numeric-values-as-input-for-the-qtablewidget-disable-the-al
    """
    def createEditor(self, parent, option, index):
        editor = super(NumericDelegate, self).createEditor(parent, option, index)
        if isinstance(editor, QtWidgets.QLineEdit):
            reg_ex = QtCore.QRegExp("[0-9]+.?[0-9]{,2}")
            validator = QtGui.QRegExpValidator(reg_ex, editor)
            editor.setValidator(validator)
        return editor


class EditDialog(QtWidgets.QDialog):
    def __init__(self, parent=None, target:str=None, settings:Settings=None, language:Language=None, unit:Unit=None, observer:Observer=None, assets:Assets=None):
        QtWidgets.QDialog.__init__(self, parent)

        self._target: str = target
        self._settings: Settings = settings
        self._language: Language = language
        self._unit: Unit = unit
        self._observer: Observer = observer
        self._assets: Assets = assets

        self._data: List[list, list] = self._settings.loadCurve(self._target)

        self.setWindowTitle(self._language.get(self._language.EditCurve))

        self._base_table: QtWidgets.QTableWidget = QtWidgets.QTableWidget(len(self._data[0]), 2, self)
        delegate = NumericDelegate(self._base_table)
        self._base_table.setItemDelegate(delegate)
        self._base_table.setHorizontalHeaderLabels([self._language.get(self._language.Raw), self._language.get(self._language.Calibrated)])
        self._base_table.horizontalHeader().setSectionResizeMode(QtWidgets.QHeaderView.Stretch)
        counter: int = 0
        for x, y in zip(self._data[0], self._data[1]):
            xitem = QtWidgets.QTableWidgetItem(str(x))
            xitem.setTextAlignment(QtCore.Qt.AlignCenter)
            yitem = QtWidgets.QTableWidgetItem(str(y))
            yitem.setTextAlignment(QtCore.Qt.AlignCenter)
            self._base_table.setItem(counter, 0, xitem)
            self._base_table.setItem(counter, 1, yitem)
            counter += 1

        self._toolbar: QtWidgets.QToolBar = QtWidgets.QToolBar(self)
        self._add_action: QtWidgets.QAction = QtWidgets.QAction(self._assets.get("plus"), "")
        self._add_action.triggered.connect(self._addAction)
        self._delete_action: QtWidgets.QAction = QtWidgets.QAction(self._assets.get("delete"), "")
        self._delete_action.triggered.connect(self._deleteAction)
        self._toolbar.addAction(self._add_action)
        self._toolbar.addAction(self._delete_action)


        self._cancel_button: QtWidgets.QPushButton = QtWidgets.QPushButton(self._language.get(self._language.Cancel), self)
        self._cancel_button.clicked.connect(self._onClose)
        self._apply_button: QtWidgets.QPushButton = QtWidgets.QPushButton(self._language.get(self._language.Apply), self)
        self._apply_button.clicked.connect(self._onApply)

        layout_bottom: QtWidgets.QHBoxLayout = QtWidgets.QHBoxLayout()
        layout_bottom.addStretch()
        layout_bottom.addWidget(self._apply_button)
        layout_bottom.addWidget(self._cancel_button)

        layout: QtWidgets.QVBoxLayout = QtWidgets.QVBoxLayout()
        layout.addWidget(self._toolbar)
        layout.addWidget(self._base_table)
        layout.addLayout(layout_bottom)

        self.setLayout(layout)

    def _addAction(self) -> None:
        count = self._base_table.rowCount()
        self._base_table.insertRow(count)
        if count > 0:
            xitem = QtWidgets.QTableWidgetItem(self._base_table.item(count - 1, 0))
            yitem = QtWidgets.QTableWidgetItem(self._base_table.item(count - 1, 1))
        else:
            xitem = QtWidgets.QTableWidgetItem(str(0.0))
            yitem = QtWidgets.QTableWidgetItem(str(0.0))
        self._base_table.setItem(count, 0, xitem)
        self._base_table.setItem(count, 1, yitem)

    def _deleteAction(self) -> None:
        count = self._base_table.rowCount()
        if count > 0:
            self._base_table.removeRow(count - 1)

    def _onClose(self) -> None:
        self.close()

    def _onApply(self) -> None:
        x, y = [], []
        for i in range(self._base_table.rowCount()):
            x.append(float(self._base_table.item(i, 0).text()))
            y.append(float(self._base_table.item(i, 1).text()))
        if len(x) > 0:
            data = [x, y]
            self._settings.saveCurve(self._target, data)
        self._onClose()