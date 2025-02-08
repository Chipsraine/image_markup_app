from Core.Grid.ClassGridTable import ClassGridTable
from Core.Grid.GridResizeStrategy import *
from PyQt5.QtCore import pyqtSignal, QObject, QSize, QRect, QPoint
from typing import Type
from Core.Area.Area import Area


class Signals(QObject):
    """
    Класс для определения сигналов, используемых в ClassGrid.
    """
    updateAllCells = pyqtSignal()  # Сигнал для обновления всей сетки
    updateCell = pyqtSignal(int, int)  # Сигнал для обновления конкретной ячейки


class ClassGrid:
    """
    Класс для управления сеткой разметки, включающей таблицу классов, размеры ячеек и сигналы для обновления.
    """

    def init(self):
        """
        Инициализирует внутренние переменные сетки.
        """
        self.table: ClassGridTable = None
        self.classes: list[Class] = []
        self.cellSize: QSize = None
        self.gridSize: QSize = None
        self.borderOffset = 0
        self.borderWidth = 0
        self.resizeStrategy: Type[GridResizeStrategy] = None
        self.signals_emitter = Signals()

    def __init__(self, table, classes, cellSize, gridSize):
        """
        Конструктор, создающий сетку с таблицей классов, размерами ячеек и стратегией изменения размеров.

        :param table: Таблица классов (ClassGridTable).
        :param classes: Список классов.
        :param cellSize: Размер одной ячейки.
        :param gridSize: Общий размер сетки.
        """
        self.init()
        if table is not None:
            self.table = table
        else:
            self.table = ClassGridTable(int(gridSize.height() // cellSize.height()),
                                        int(gridSize.width() // cellSize.width()))

        self.classes = classes if classes is not None else [Class.default()]
        self.cellSize = cellSize
        self.gridSize = gridSize
        self.updateBorderInfo()
        self.resizeStrategy = PixByPixResizeStrategy

    def updateBorderInfo(self):
        """
        Обновляет информацию о ширине границы ячеек на основе их размеров.
        """
        lesserSide = min(self.cellSize.width(), self.cellSize.height())
        if lesserSide < 8:
            self.borderOffset = 1
        elif lesserSide < 16:
            self.borderOffset = 2
        else:
            self.borderOffset = 3
        self.borderWidth = self.borderOffset * 2

    def setResizeStrategy(self, strategy: Type[GridResizeStrategy]):
        """
        Устанавливает стратегию изменения размеров ячеек.

        :param strategy: Класс стратегии изменения размеров.
        """
        self.resizeStrategy = strategy

    def applyResizeStrategy(self, newCellSize):
        """
        Применяет стратегию изменения размеров ячеек.

        :param newCellSize: Новый размер ячейки.
        """
        self.resizeStrategy.applyResize(self, newCellSize)

    def hasSameCellSize(self, cellSize):
        """
        Проверяет, совпадают ли размеры ячеек.

        :param cellSize: Размер ячейки для сравнения.
        :return: True, если размеры совпадают, иначе False.
        """
        return cellSize.width() == self.cellSize.width() and cellSize.height() == self.cellSize.height()

    def canCellSizeFitInGrid(self, cellSize):
        """
        Проверяет, вписываются ли размеры ячеек в размеры сетки.

        :param cellSize: Размер ячейки для проверки.
        :return: True, если размеры подходят, иначе False.
        """
        return cellSize.width() <= self.gridSize.width() and cellSize.height() <= self.gridSize.height()

    def changeCellSize(self, newCellsize):
        """
        Изменяет размеры ячеек, применяя стратегию изменения, и обновляет границы.

        :param newCellsize: Новый размер ячейки.
        """
        self.applyResizeStrategy(newCellsize)
        self.updateBorderInfo()
        self.signals_emitter.updateAllCells.emit()

    def getCellByCoordinates(self, x: int, y: int):
        """
        Возвращает класс ячейки по координатам.

        :param x: Координата x.
        :param y: Координата y.
        :return: Класс ячейки.
        """
        row, col = y // self.cellSize.width(), x // self.cellSize.height()
        return self.table.getCellClass(row, col)

    def getCellCoordinates(self, row, col):
        """
        Возвращает координаты верхнего левого угла ячейки по строке и колонке.

        :param row: Номер строки.
        :param col: Номер колонки.
        :return: Координаты (x, y) или None, если ячейка вне сетки.
        """
        if not self.table.isCellInsideGrid(row, col):
            return None
        return self.cellSize.width() * col, self.cellSize.height() * row

    def getCellRect(self, row: int, col: int):
        """
        Возвращает прямоугольник ячейки.

        :param row: Номер строки.
        :param col: Номер колонки.
        :return: QRect объекта ячейки или None, если ячейка вне сетки.
        """
        topLeft = self.getCellCoordinates(row, col)
        if topLeft is None:
            return None
        return QRect(topLeft, QPoint(topLeft.x() + self.cellSize.width() - 1, topLeft.y() + self.cellSize.height() - 1))

    def setClasses(self, classes: list[Class]):
        """
        Устанавливает список классов для сетки.

        :param classes: Новый список классов.
        """
        for _class in self.classes:
            try:
                classIndex = classes.index(_class)
                self.table.removeClassFromTable(classes[classIndex])
            except ValueError:
                pass
        self.classes = classes
        self.signals_emitter.updateAllCells.emit()

    def getCellClass(self, row, col):
        """
        Возвращает класс ячейки по строке и колонке.

        :param row: Номер строки.
        :param col: Номер колонки.
        :return: Класс ячейки.
        """
        return self.table.getCellClass(row, col)

    def setClassToCell(self, row, col, _class):
        """
        Устанавливает класс в ячейку.

        :param row: Номер строки.
        :param col: Номер колонки.
        :param _class: Класс для установки.
        """
        self.table.setClassToCell(row, col, _class)
        self.signals_emitter.updateCell.emit(row, col)

    def removeClassFromCell(self, row, col):
        """
        Удаляет класс из ячейки.

        :param row: Номер строки.
        :param col: Номер колонки.
        """
        self.table.setClassToCell(row, col, None)
        self.signals_emitter.updateCell.emit(row, col)

    def removeClassFromGrid(self, _class):
        """
        Удаляет класс из всей сетки.

        :param _class: Класс для удаления.
        """
        self.classes.remove(_class)
        self.table.removeClassFromTable(_class)
        self.signals_emitter.updateAllCells.emit()

    def changeClassColor(self, className, color):
        """
        Изменяет цвет класса.

        :param className: Имя класса.
        :param color: Новый цвет.
        """
        self.classes[className]._color = color
        self.signals_emitter.updateAllCells.emit()

    def changeClassName(self, prevName, newName):
        """
        Изменяет имя класса.

        :param prevName: Старое имя класса.
        :param newName: Новое имя класса.
        """
        _class = self.classes.pop(prevName)
        _class._name = newName
        self.classes[newName] = _class

    def fillEmptyCellsWithClass(self, _class):
        """
        Заполняет пустые ячейки указанным классом.

        :param _class: Класс для заполнения.
        """
        self.table.fillEmptyCellsWithClass(_class)
        self.signals_emitter.updateAllCells.emit()

    def setClassToArea(self, area: Area, _class):
        """
        Устанавливает класс для области.

        :param area: Область (Area).
        :param _class: Класс для установки.
        """
        self.table.setClassToArea(area, _class)
        self.signals_emitter.updateAllCells.emit()

    def removeClassesFromArea(self, area: Area):
        """
        Удаляет классы из указанной области.

        :param area: Область (Area).
        """
        self.table.setClassToArea(area, None)
        self.signals_emitter.updateAllCells.emit()
