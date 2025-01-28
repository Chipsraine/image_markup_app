from PyQt5.QtCore import QObject, pyqtSignal
from Core.Grid.Class import Class

class ClassList(QObject):
    classAdded = pyqtSignal(Class)
    classRemoved = pyqtSignal(Class)
    classChanged = pyqtSignal()
    
    def __init__(self):
        super().__init__(None)
        self.classes : list[Class] = []
        
    def addClassToList(self, _class):
        self.classes
        
    def onClassChange(self):
        self.classChanged.emit()