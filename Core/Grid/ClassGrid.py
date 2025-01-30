from Core.Grid.Class import Class
from Core.Grid.ClassGridTable import ClassGridTable
from Core.Grid.GridResizeStrategy import *
from PyQt5.QtCore import pyqtSignal, QObject, QSize, QRect, QPoint, Qt
from typing import Type

from Core.Area.Area import Area
class Signals(QObject):
    updateAllCells = pyqtSignal()
    updateCell = pyqtSignal(int, int)

class ClassGrid:
    def init(self):
        self.table : ClassGridTable = None
        self.classes : list[Class] = []
        self.cellSize : QSize = None
        self.gridSize : QSize = None
        self.borderOffset = 0
        self.borderWidth = 0
        self.resizeStrategy : Type[GridResizeStrategy] = None
        self.signals_emitter = Signals()

    def __init__(self, table, classes, cellSize, gridSize):
        self.init()
        if (table != None):
            self.table = table
        else:
            self.table = ClassGridTable(int(gridSize.height() // cellSize.height()), int(gridSize.width() // cellSize.width()))
        
        if (classes != None):
            self.classes = classes
        else:
            self.classes = [Class.default()]
        
        self.cellSize = cellSize
        self.gridSize = gridSize
        self.updateBorderInfo()
        self.resizeStrategy = PixByPixResizeStrategy
        
        
    def updateBorderInfo(self):
        lesserSide = min(self.cellSize.width(), self.cellSize.height())
        if lesserSide < 8:
            self.borderOffset = 1
        elif lesserSide < 16:
            self.borderOffset = 2
        else:
            self.borderOffset = 3
        
        self.borderWidth = self.borderOffset * 2
        
    def setResizeStrategy(self, strategy : Type[GridResizeStrategy]):
        self.resizeStrategy = strategy
        
    def applyResizeStrategy(self, newCellSize):
        self.resizeStrategy.applyResize(self, newCellSize)
    
    def hasSameCellSize(self, cellSize):
        return cellSize.width() == self.cellSize.width() and cellSize.height() == self.cellSize.height()
        
    def canCellSizeFitInGrid(self, cellSize):
        return cellSize.width() <= self.gridSize.width() and cellSize.height() <= self.gridSize.height()
        
    def changeCellSize(self, newCellsize):
        self.applyResizeStrategy(newCellsize)
        self.updateBorderInfo()
        self.signals_emitter.updateAllCells.emit()
        

    def getCellByCoordinates(self, x:int, y:int):
        row, col = y // self.cellSize.width(), x // self.cellSize.height()
        return self.table.getCellClass(row, col)
    
    def getCellCoordinates(self, row, col):
        if not self.table.isCellInsideGrid(row, col):
            return None
        
        return self.cellSize.width() * col, self.cellSize.height() * row
    
    def getCellRect(self, row :int, col:int):
        topLeft = self.getCellCoordinates(row, col)
        if topLeft is None:
            return None
        return QRect(topLeft, QPoint(topLeft.x() + self.cellSize.width() - 1, topLeft.y() + self.cellSize.height() - 1))
    
    def setClasses(self, classes: list[Class]):
        for _class in self.classes:
            classIndex = 0
            try:
                classIndex = classes.index(_class)
                self.table.removeClassFromTable(classes[classIndex])
            except ValueError:
                pass             
        self.classes = classes
        self.signals_emitter.updateAllCells.emit()
                
        
    def getCellClass(self, row, col):
        return self.table.getCellClass(row, col)
        
    def setClassToCell(self, row, col, _class):
        self.table.setClassToCell(row, col, _class)   
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