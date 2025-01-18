from PyQt5.QtGui import QColor
from PyQt5.QtCore import pyqtSignal, QObject

class Class(QObject):
    colorChanged = pyqtSignal(QColor)
    nameChanged = pyqtSignal(str)
    
    def __init__(self, name : str, color : QColor):
        super().__init__(None)
        self._name : str = name
        self._color : QColor = color
    
    def color(self):
        return self._color
    
    def name(self):
        return self._name
    
    def setColor(self, color):
        self._color = color
        self.colorChanged.emit(color)
        
    def setName(self, name):
        self._name = name
        self.nameChanged.emit(name)