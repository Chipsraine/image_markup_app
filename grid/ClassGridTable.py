from grid.ResizeStrategy import ResizeStrategy
from PyQt5.QtCore import QRect

from grid.area.Area import Area

class ClassGridTable:
    
    def __init__(self, rows, cols):
        self.rows = rows
        self.cols = cols
        self.data = [[None for _ in range(cols)] for _ in range(rows)]
        
    def setSize(self, resizeStrategy: ResizeStrategy):
        resizeStrategy.resize(self)
        
    def isCellInsideGrid(self, row, col):
        return 0 <= row < self.rows and 0 <= col < self.cols 
        
        
    def setClassToCell(self, row, col, _class):
        try:
            self.data[row][col] = _class
        except IndexError as error:
            raise error
        
    def getCellClass(self, row, col):
        try:
            return self.data[row][col]
        except IndexError as error:
            raise error
        
    def fillEmptyCellsWithClass(self, _class):
        for row in range(self.rows):
            for col in range(self.cols):
                if self.data[row][col] == None:
                    self.setClassToCell(row, col, _class)
                    
        
    def removeClassFromTable(self, _class):
        for row in range(self.rows):
            for col in range(self.cols):
                if self.data[row][col] == _class:
                    self.setClassToCell(row,col, None)
                    
    def switchCellClass(self, row, col, _class):
        cellClass = self.getCellClass(row, col)
        if cellClass == _class:
            self.setClassToCell(row, col, None)
        else:
            self.setClassToCell(row, col, _class)
        
    def setClassToArea(self, area: Area, _class):
        startCol = area.firstPoint.col
        startRow = area.firstPoint.row
        endCol = area.secondPoint.col + 1
        endRow = area.secondPoint.row + 1
        for row in range(startRow, endRow, 1):
             for col in range(startCol, endCol, 1):
                 self.setClassToCell(row, col, _class)