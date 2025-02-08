from abc import ABC, abstractmethod
from Core.Grid.Class import Class
from Core.Grid import ClassGridTable as TableModule
from PyQt5.QtCore import QSize

class GridResizeStrategy(ABC):
    """
    Абстрактный класс для стратегии изменения размеров сетки.
    Позволяет определить разные методы изменения размеров ячеек в сетке.
    """

    def __init__(self):
        super().__init__()

    @abstractmethod
    def applyResize(grid, newCellSize: QSize):
        """
        Абстрактный метод, который должен быть реализован в подклассах.
        Определяет, как изменять размеры сетки.

        :param grid: Экземпляр ClassGrid, который нужно изменить.
        :param newCellSize: Новый размер ячеек.
        """
        pass


class PixByPixResizeStrategy(GridResizeStrategy):
    """
    Стратегия изменения размеров сетки, при которой каждая новая ячейка получает класс,
    основываясь на пиксельном большинстве предыдущих ячеек.
    """

    def __init__(self):
        super().__init__()

    def applyResize(grid, newCellSize: QSize):
        """
        Изменяет размеры сетки, вычисляя новые классы на основе большинства пикселей.

        :param grid: Экземпляр ClassGrid, который изменяется.
        :param newCellSize: Новый размер ячейки.
        """
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
                cellClasses: dict[Class, int] = {cls: 0 for cls in grid.classes}
                cellClasses[None] = 0  # Счетчик для пустых ячеек

                firstRowPix, lastRowPix = newRow * newCellHeight, (newRow + 1) * newCellHeight
                firstColPix, lastColPix = newCol * newCellWidth, (newCol + 1) * newCellWidth

                # Анализируем предыдущие ячейки и считаем, какие классы встречаются чаще
                for rowPix in range(firstRowPix, lastRowPix):
                    for colPix in range(firstColPix, lastColPix):
                        oldCol = colPix // oldCellWidth
                        oldRow = rowPix // oldCellHeight
                        cellClass = grid.table.getCellClassOrNone(oldRow, oldCol)
                        cellClasses[cellClass] += 1

                # Назначаем новый класс по большинству пикселей
                dominantClass = max(cellClasses, key=cellClasses.get)
                newGridTable.setClassToCell(newRow, newCol, dominantClass)

        grid.table = newGridTable
        grid.cellSize = newCellSize
