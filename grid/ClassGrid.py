from grid.Class import Class
from grid.ClassGridTable import ClassGridTable
from grid.SimpleResizeStrategy import SimpleResizeStrategy
from grid.ComplexResizeStrategy import ComplexResizeStrategy
from grid.ResizeStrategy import ResizeStrategy
from PyQt5.QtCore import pyqtSignal, QObject
from typing import Type

from forms.implemented_widgets.ClassGridGraphicsView import Area, Point

class Signals(QObject):
    updateAllCells = pyqtSignal()
    updateCell = pyqtSignal(int, int)

class ClassGrid:
    def init(self):
        self.table : ClassGridTable = None
        self.classes : dict[str, Class] = {}
        self.cellSize : dict[str, int] = {"width": 0, "height": 0}
        self.gridSize : dict[str, int] = {"width": 0, "height": 0}
        self.resizeStrategy : Type[ResizeStrategy] = None
        self.signals_emitter = Signals()

    def __init__(self, table, classes, cellSize, gridSize):
        self.init()
        self.table = table
        self.classes = classes
        self.cellSize = cellSize
        self.gridSize = gridSize
        self.resizeStrategy = SimpleResizeStrategy
        

        
    def setResizeStrategy(self, strategy : Type[ResizeStrategy]):
        self.resizeStrategy = strategy
        
    def setCellSize(self, newCellsize):
        self.table.setSize(self.resizeStrategy(self.cellSize, newCellsize, self.gridSize))
        self.cellSize = newCellsize
        self.signals_emitter.updateAllCells.emit()

    
    def setClasses(self, classes: dict[str, Class]):
        for name, _class in self.classes.items():
            if classes.get(name) == None:
                self.table.removeClassFromTable(_class)
        self.signals_emitter.updateAllCells.emit()

                
        
    def getCellClass(self, row, col):
        return self.table.getCellClass(row, col)
        
    def setClassToCell(self, row, col, _class):

        self.table.switchCellClass(row, col, _class)
        self.signals_emitter.updateCell.emit(row, col)
        
    def removeClassFromCell(self, row, col):
        self.table.setClassToCell(row, col, None)
        
        self.signals_emitter.updateCell.emit(row, col)
        
    def removeClassFromGrid(self, _class):
        self.classes.pop(_class._name)
        self.table.removeClassFromTable(_class)
        self.signals_emitter.updateAllCells.emit()
    
    def changeClassColor(self, className, color):
        self.classes[className]._color = color
        self.signals_emitter.updateAllCells.emit()
          
    def changeClassName(self, prevName, newName):
        _class = self.classes.pop(prevName)
        _class._name = newName
        self.classes[newName] = _class
                    
    def fillEmptyCellsWithClass(self, _class):
        self.table.fillEmptyCellsWithClass(_class)
        self.signals_emitter.updateAllCells.emit()
        
    def setClassToArea(self, area: Area, _class):
        self.table.setClassToArea(area, _class)
        self.signals_emitter.updateAllCells.emit()
        
        
    def removeClassesFromArea(self, area: Area):
        self.table.setClassToArea(area, None)
        self.signals_emitter.updateAllCells.emit()