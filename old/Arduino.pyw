# -*- coding: utf-8 -*-
"""
Created on Mon Oct  5 18:19:45 2020
@author: José Correia
"""
import serial
import serial.tools.list_ports
ports = list(serial.tools.list_ports.comports())
baud_rate = 9600
import time
from threading import Thread


from PyQt5 import QtWidgets, uic 
from datetime import datetime
import sys

# NOTE: bibliotecas para graficos
import matplotlib.pyplot as pyplot
import numpy as np
#from scipy.stats import linregress


class JanelaCalibracao(QtWidgets.QDialog):
    def __init__(self, parent=None):

        QtWidgets.QDialog.__init__(self, parent=None)
        uic.loadUi('janela_calibracao.ui', self)
        
        self._parent = parent
        
        self.tabela.setColumnCount(2)
        self.tabela.setHorizontalHeaderItem(0, QtWidgets.QTableWidgetItem("Medidor"))
        self.tabela.setHorizontalHeaderItem(1, QtWidgets.QTableWidgetItem("Padrão"))
        
        self.tabela_descendente.setColumnCount(2)
        self.tabela_descendente.setHorizontalHeaderItem(0, QtWidgets.QTableWidgetItem("Medidor"))
        self.tabela_descendente.setHorizontalHeaderItem(1, QtWidgets.QTableWidgetItem("Padrão"))
        
        self.adicionar.clicked.connect(self._adicionar)
        self.grafico.clicked.connect(self._fazer_grafico)

    def _adicionar(self):
        m = self.medidor.value()
        p = self.padrao.value()
        if self.ordem.currentText() == "Ascendente":
            n = self.tabela.rowCount()
            if self.tabela.rowCount()==0:
                n = 0
            self.tabela.insertRow(n)
            self.tabela.setItem(n,0,QtWidgets.QTableWidgetItem(str(m)))
            self.tabela.setItem(n,1,QtWidgets.QTableWidgetItem(str(p)))
        else:  
            n = self.tabela_descendente.rowCount()
            if self.tabela_descendente.rowCount()==0:
                n = 0
            self.tabela_descendente.insertRow(n)
            self.tabela_descendente.setItem(n,0,QtWidgets.QTableWidgetItem(str(m)))
            self.tabela_descendente.setItem(n,1,QtWidgets.QTableWidgetItem(str(p)))
            
    def _fazer_grafico(self)->None:
        print(1)
        x = []
        y = []
        for i in range(self.tabela.rowCount()):
            y.append(float(self.tabela.item(i, 0).text()))
            x.append(float(self.tabela.item(i, 1).text()))
        fig, plt = pyplot.subplots()
        plt.set_ylabel('Valores no padrão')
        plt.set_xlabel('Valores no medidor') 
        plt.set_title('CALIBRAÇÃO')
        plt.scatter(x, y)
        z = np.polyfit(x, y, 2)
        self._parent._p = p = np.poly1d(z)
        plt.plot(x,p(x),"r--")
        plt.show()
        plt.text(5,0,"y=%.4fx^2+%.4fx"%(z[0],z[1]))
        plt.savefig('Calibra.png') 
        print ("y=%.4fx^2+%.4fx"%(z[0],z[1]))
        
            
    def salvar(self):
        self.fic = QtWidgets.QFileDialog.getSaveFileName(self, "Abrir Ficheiro", "", "Text Files (*.csv *.txt)")
        return self.fic[0]
        
    def accept(self):
        nomefic = "%s" %(self.salvar())
        ficheiro = open(nomefic,"w")
        dt = datetime.now()
        ficheiro.write(dt.strftime('%X %x')+"\n")
        ficheiro.write("%s\n" % "Sentido Ascendente")
        ficheiro.write("%s\n" % "V.Med. - V.Pad.")
        for i in range(self.tabela.rowCount()):
            ficheiro.write("%s %s %s\n" % (self.tabela.item(i, 0).text(),"     ",self.tabela.item(i, 1).text()))

        ficheiro.write("%s\n" % "Sentido Descendente")
        ficheiro.write("%s\n" % "V.Med. - V.Pad.")
        for i in range(self.tabela_descendente.rowCount()):
            ficheiro.write("%s %s %s\n" % (self.tabela_descendente.item(i, 0).text(),"     ",self.tabela_descendente.item(i, 1).text()))
        ficheiro.close()
        
        super().accept()

        
    def reject(self):
        print("Cancel")
        super().reject()


class Arduino(QtWidgets.QWidget):
    def __init__(self):
       import os
       os.chdir(os.path.dirname(__file__))
       QtWidgets.QWidget.__init__(self, parent=None)
       uic.loadUi('arduino_20-5-2021.ui', self)  # Load the arduino_20-5-2021.ui file 
       
       self._p = None
       
       self._thread: Thread = None
       self._ports = list(serial.tools.list_ports.comports())
       for porta in serial.tools.list_ports.comports():
           self.PortaCom.addItem(porta.device)
       self.Exit.clicked.connect(self._onExit)
       self.btn_start.clicked.connect(self.LePressao)
       self.btn_set.clicked.connect(self.PressaoSetup)
       self.show() #Show the GUI
       self.label_9.setText("Limites Inativos")
       self.label_9.setStyleSheet("color: rgb(255, 0, 0);")
       self.btnSalvar.clicked.connect(self.abrirFic)
       self.calib_btn.clicked.connect(self._calibracao)
       self.btn_ImportCal.clicked.connect(self.abrirFic)
       self.esvaziar.clicked.connect(self._esvaziar)
       self.encher.clicked.connect(self._encher)
       
    def _esvaziar(self):
        if self.esvaziar.text() == 'Ok':
            self.esvaziar.setText(" ")
            return
        if hasattr(self, '_serial'):
            self.esvaziar.setText("Ok")
            self._serial.write(str("X").encode())
            print("Estado de esvaziar: ", str("Ok"))
        else:
            QtWidgets.QMessageBox.warning(self, "Nao efetuou a conexão", "Tem de abrir a conexão primeiro.")
        
    def _encher(self):
        if self.encher.text() == 'Ok':
            self.esvaziar.setText(" ")
            return
        if hasattr(self, '_serial'):
            self.encher.setText("Ok")
            self._serial.write(str("Y").encode())
            print("Estado de encher: ", str("Ok"))
        else:
            QtWidgets.QMessageBox.warning(self, "Nao efetuou a conexão", "Tem de abrir a conexão primeiro.")
    
    def _calibracao(self):
        self._calib_diag = JanelaCalibracao(self)
        self._calib_diag.show()
       
    def PressaoSetup(self):
        value = self.SetPressao.value()
        self._serial.write(str(value).encode())
        print("Value sent: ", str(value), str(value).encode())
        pass
        
    def LePressao(self):
        try:
            self._serial: serial.Serial = serial.Serial(self.PortaCom.currentText(), 9600)
            self._thread_flag: bool = True
            self._thread = Thread(target=self.readPressure)
            self._thread.start()
        except OSError as err:
            print("Arduino::LePresao : Não foi possivel abrir a porta " + self.PortaCom.currentText() + " com erro: ", err)
            QtWidgets.QMessageBox.warning(self, "Porta inacessível", "Nao foi possível abrir a porta "+ self.PortaCom.currentText()+".")
       
    def tempo():
        from datetime import datetime
        datetime.now().strftime('%H:%M:%S')
       
    def readPressure(self):
        while self._thread_flag:
            value = self._serial.readline()
            try:
                val = str(value).replace("\\r","").replace("\\n","").replace("''","").replace("b","").replace("'","").replace("'","")
                if val == "IC_H":
                    self.label_9.setText("Atingiu o início do curso")
                elif val == "FC_H":
                    self.label_9.setText("Atingiu o fim do curso")
                elif val == "FC_L":
                    pass
                elif val == "IC_L":
                    pass
                else:
                    self.label_9.setText("")
                    if self._p is not None:
                        print(1)
                        print(val, float(val), self._p(float(val)))
                        self.Pressao.setText('%.1f'%self._p(float(val)))
                    else:
                        print(2)
                        self.Pressao.setText(val)
            except ValueError as error:
                print(error)
            time.sleep(0.2)
            
    def closeEvent(self, event):
        result = QtWidgets.QMessageBox.question(self,
                      "Confirme a Saída...",
                      "Tem a certeza que quer sair ?",
                      QtWidgets.QMessageBox.Yes| QtWidgets.QMessageBox.No)
        event.ignore()

        if result == QtWidgets.QMessageBox.Yes:
            self._thread_flag = False
            if self._thread is not None:
                self._thread.join()
                self._serial.close()
            event.accept()
            
    def abrirFic(self):
        fic = QtWidgets.QFileDialog.getOpenFileName(self, "Abrir Ficheiro", "", "Text Files (*.csv *.txt)")
        try:   
            f = open(fic[0],'r')
            lista = f.readlines()
            numeros = []
            x = []
            y = []
            for l in lista:
                s = l.split()
                if s[0].replace('.','').isdigit():
                    numeros.append([float(num) for num in s])
                    y.append(float(s[0]))
                    x.append(float(s[1]))
            f.close()
            z = np.polyfit(x, y, 2)
            self._p = np.poly1d(z)
            print(numeros[1][1])
            print(numeros)
        except:
            print("Problema ao abrir o ficheiro")                             
        return
        try:
            f = open(fic, 'r')
            f.close()
        except:
                print("Problema ao abrir o ficheiro")
            
            
    def _onExit(self):
        self.close()
        
        
app = QtWidgets.QApplication(sys.argv)
window = Arduino()
app.exec_()
