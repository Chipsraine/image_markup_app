from grid.Class import Class
from PyQt5.QtGui import QColor
from PyQt5.QtCore import pyqtSignal, QObject

class Signals(QObject):
    updateAllCells = pyqtSignal()
    updateCell = pyqtSignal(int, int)

class ClassGrid:

        
    
    def __init__(self):
        self.table : dict[int, dict[int, Class]] = {}
        self.classes : dict[str, Class] = {}
        self.cellSize = 0
        self.signals_emitter = Signals()
        
    def setCellSize(self, pixelsCount):
        self.cellSize = pixelsCount
    
    def setClasses(self, classes: dict[Class]):
        self.classes = classes
        
    def getCellClass(self, row, col):
        if self.table.get(row) == None:
            return None
        if self.table[row].get(col) == None:
            return None 
        
        return self.table[row][col]
        
    def setClassToCell(self, row, col, _class):
        if self.getCellClass(row, col) == _class:
            self.table[row][col] = None
        else:
            if self.table.get(row) == None:
                self.table[row] = {}
            self.table[row][col] = _class
        
        self.signals_emitter.updateCell.emit(row, col)
        
    # def removeClassFromCell(self, row, col):
    #     if self.table.get(row) == None:
    #         return
    #     if self.table[row].get(col) == None:
    #         return 
        
    #     self.table[row][col] = None
        
    #     self.updateCell.emit(row, col)
        
    def removeClassFromGrid(self, className):
        _class = self.classes.pop(className)
        
        for row in self.table.values():
            for col, cell in row.items():
                if cell == _class:
                    row[col] = None
        
        self.signals_emitter.updateAllCells.emit()
    
    def changeClassColor(self, className, color):
        self.classes[className]._color = color
        
        self.signals_emitter.updateAllCells.emit()
          
    def changeClassName(self, prevName, newName):
        _class = self.classes.pop(prevName)
        _class._name = newName
        self.classes[newName] = _class
                    
    def fillEmptyCellsWithClass(self, rows, cols, _class):
        for row in range(rows):
            for col in range(cols):
                if self.getCellClass(row, col) == None:
                    self.setClassToCell(row, col, _class)
        self.signals_emitter.updateAllCells.emit()
        
    def setTable(self, dct):
        self.table = {}
        
        for entry in dct:
            row = entry["row"]
            col = entry["col"]
            if self.table.get(row) == None:
                self.table[row] = {}
            self.table[row][col] = self.classes[entry["class"]]
        
    @staticmethod
    def fromJson(dict):
        classGrid = ClassGrid()
        classGrid.setClasses(Class.dictFromJson(dict["classes"]))
        classGrid.setCellSize(dict["cell_size"])
        classGrid.setTable(dict["table"])
        return classGrid
        
        
        