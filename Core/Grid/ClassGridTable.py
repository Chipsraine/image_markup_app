from Core.Grid.GridResizeStrategy import *
from Core.Area.Area import Area

class ClassGridTable:
    
    def __init__(self, rows, cols):
        self.rows = rows
        self.cols = cols
        self.data = [[None for _ in range(cols)] for _ in range(rows)]
        
    def setSize(self, resizeStrategy: GridResizeStrategy):
        resizeStrategy.applyResize(self)
        
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
        
    def getCellClassOrNone(self, row, col):
        if self.isCellInsideGrid(row, col):
            return self.data[row][col]
        else:
            return None
        
        
    def fillEmptyCellsWithClass(self, _class):
        for row in range(self.rows):
            for col in range(self.cols):
                if self.data[row][col] == None:
                    self.data[row][col] = _class
                    
        
    def removeClassFromTable(self, _class):
        for row in range(self.rows):
            for col in range(self.cols):
                if self.data[row][col] == _class:
                     self.data[row][col] = None
                    
    def switchCellClass(self, row, col, _class):
        cellClass = self.getCellClass(row, col)
        if cellClass == _class:
            self.setClassToCell(row, col, None)
        else:
            self.setClassToCell(row, col, _class)
        
    def setClassToArea(self, area: Area, _class):
        startCol = min(area.firstPoint.col, area.secondPoint.col)
        startRow = min(area.firstPoint.row, area.secondPoint.row)
        
        offsetCol = 1 if area.secondPoint.col >= area.firstPoint.col else 0
        offsetRow = 1 if area.secondPoint.row >= area.firstPoint.row else 0
        endCol = max(area.firstPoint.col, area.secondPoint.col) + offsetCol
        endRow = max(area.firstPoint.row, area.secondPoint.row) + offsetRow
        
        for row in range(startRow, endRow, 1):
             for col in range(startCol, endCol, 1):
                 self.setClassToCell(row, col, _class)