# -*- coding: utf-8 -*-
"""
Created on Mon Oct  5 18:19:45 2020

@author: José Correia
"""

from PyQt5 import QtWidgets, uic
import sys


class Arduino(QtWidgets.QWidget):
    def __init__(self):
        QtWidgets.QWidget.__init__(self, parent=None)
        uic.loadUi('arduino.ui', self)  # Load the .ui file
        
        
        #self.setGeometry(200, 200, 200, 100)
        #self.PortaCom.textEdited.connect(self.LePorta)
        #self.Pressao.valueChanged.connect(self.LePressao)
        #self.Volume.valueChanged.connect(self.LeVolume)
        
        
        self.show() # Show the GUI
        
    def LePressao(self):
        #print(self.Pressao.value())
        return
        

        
    def LeVolume(self, nome:str)->None:

        self.Volume.setValue(len(nome))
  
        self.QPushButton('Exit', self)
        quit = QtWidgets.QPushButton('Exit', self)
        self.connect(quit, uic.SIGNAL('clicked()'),
        QtWidgets.qApp, uic.SLOT('quit()'))

app = QtWidgets.QApplication(sys.argv)
window = Arduino()
app.exec_()
