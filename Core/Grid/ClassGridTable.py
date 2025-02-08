from Core.Grid.GridResizeStrategy import *
from Core.Area.Area import Area

class ClassGridTable:
    """
    Класс для хранения сетки классов разметки.
    Управляет ячейками, позволяя устанавливать и удалять классы, а также изменять размеры сетки.
    """

    def __init__(self, rows, cols):
        """
        Инициализирует таблицу сетки заданного размера.

        :param rows: Количество строк в сетке.
        :param cols: Количество колонок в сетке.
        """
        self.rows = rows
        self.cols = cols
        self.data = [[None for _ in range(cols)] for _ in range(rows)]

    def setSize(self, resizeStrategy: GridResizeStrategy):
        """
        Изменяет размер сетки в соответствии с заданной стратегией.

        :param resizeStrategy: Объект стратегии изменения размеров сетки.
        """
        resizeStrategy.applyResize(self)

    def isCellInsideGrid(self, row, col):
        """
        Проверяет, находится ли ячейка в пределах сетки.

        :param row: Номер строки.
        :param col: Номер колонки.
        :return: True, если ячейка внутри границ сетки, иначе False.
        """
        return 0 <= row < self.rows and 0 <= col < self.cols

    def setClassToCell(self, row, col, _class):
        """
        Назначает класс указанной ячейке.

        :param row: Номер строки.
        :param col: Номер колонки.
        :param _class: Класс для установки.
        """
        try:
            self.data[row][col] = _class
        except IndexError as error:
            raise error

    def getCellClass(self, row, col):
        """
        Возвращает класс, назначенный ячейке.

        :param row: Номер строки.
        :param col: Номер колонки.
        :return: Класс, содержащийся в ячейке.
        """
        try:
            return self.data[row][col]
        except IndexError as error:
            raise error

    def getCellClassOrNone(self, row, col):
        """
        Возвращает класс ячейки, если она находится в пределах сетки, иначе None.

        :param row: Номер строки.
        :param col: Номер колонки.
        :return: Класс ячейки или None.
        """
        return self.data[row][col] if self.isCellInsideGrid(row, col) else None

    def fillEmptyCellsWithClass(self, _class):
        """
        Заполняет все пустые ячейки указанным классом.

        :param _class: Класс для заполнения.
        """
        for row in range(self.rows):
            for col in range(self.cols):
                if self.data[row][col] is None:
                    self.data[row][col] = _class

    def removeClassFromTable(self, _class):
        """
        Удаляет все вхождения указанного класса из таблицы.

        :param _class: Класс, который нужно удалить.
        """
        for row in range(self.rows):
            for col in range(self.cols):
                if self.data[row][col] == _class:
                    self.data[row][col] = None

    def switchCellClass(self, row, col, _class):
        """
        Переключает класс в ячейке: если он уже установлен, убирает его, иначе устанавливает.

        :param row: Номер строки.
        :param col: Номер колонки.
        :param _class: Класс для установки или удаления.
        """
        if self.getCellClass(row, col) == _class:
            self.setClassToCell(row, col, None)
        else:
            self.setClassToCell(row, col, _class)

    def setClassToArea(self, area: Area, _class):
        """
        Назначает класс всем ячейкам в указанной области.

        :param area: Область разметки.
        :param _class: Класс для установки.
        """
        startCol = min(area.firstPoint.col, area.secondPoint.col)
        startRow = min(area.firstPoint.row, area.secondPoint.row)
        endCol = max(area.firstPoint.col, area.secondPoint.col) + 1
        endRow = max(area.firstPoint.row, area.secondPoint.row) + 1

        for row in range(startRow, endRow):
            for col in range(startCol, endCol):
                self.setClassToCell(row, col, _class)
