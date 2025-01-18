from abc import ABC, abstractmethod

from Core.Grid.Class import Class
from Core.Grid import ClassGridTable as TableModule

from PyQt5.QtCore import QSize

class GridResizeStrategy(ABC):
    def __init__(self):
        super().__init__()   
    @abstractmethod
    def applyResize(grid, newCellSize):
        pass


class PixByPixResizeStrategy(GridResizeStrategy):
    def __init__(self):
        super().__init__()

    def applyResize(grid, newCellSize :QSize):
        if grid.gridSize == newCellSize:
            return
        
        newRows = grid.gridSize.height() // newCellSize.height()
        newCols = grid.gridSize.width() // newCellSize.width()
        oldCellWidth = grid.cellSize.width()
        oldCellHeight = grid.cellSize.height()
        newCellWidth = newCellSize.width()
        newCellHeight = newCellSize.height()


        newGridTable = TableModule.ClassGridTable(newRows, newCols)

        for newRow in range(newRows):
            for newCol in range(newCols):
                cellClasses : dict[Class, int] = {}
                for _class in  grid.classes:
                    cellClasses[_class] = 0
                cellClasses[None] = 0
                firstRowPix, lastRowPix = newRow * newCellHeight, (newRow + 1)  * newCellHeight
                firstColPix, lastColPix = newCol * newCellWidth, (newCol + 1 ) * newCellWidth

                for rowPix in range(firstRowPix, lastRowPix, 1):
                    for colPix in range(firstColPix, lastColPix, 1):
                        oldCol = colPix // oldCellWidth
                        oldRow = rowPix // oldCellHeight
                        cellClasses[grid.table.getCellClassOrNone(oldRow, oldCol)] += 1
                _class = max(cellClasses, key=cellClasses.get)
                newGridTable.setClassToCell(newRow, newCol, _class)
        grid.table = newGridTable
        grid.cellSize = newCellSize