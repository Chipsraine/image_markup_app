from Core.Grid.Class import Class
from Core.Grid.ClassGridTable import ClassGridTable
from Core.Grid.ClassGrid import ClassGrid
from io import TextIOWrapper
from PyQt5.QtGui import QColor
from PyQt5.QtCore import QSize


class ClassGridDeserializer:
    """
    Класс для десериализации (загрузки) сетки разметки из текстового файла.
    """

    @staticmethod
    def fromTxt(file: TextIOWrapper, imageSize: QSize) -> ClassGrid:
        """
        Загружает объект ClassGrid из текстового файла.

        :param file: Открытый текстовый файл с данными разметки.
        :param imageSize: Размер изображения, для которого создается сетка.
        :return: Экземпляр ClassGrid.
        """
        # Читаем размер ячеек
        cellSize = QSize(*map(int, file.readline().split()))

        # Читаем список классов
        classes: list[Class] = []
        for item in file.readline().strip().split(';'):
            class_name, color = item.strip().split("~")
            classes.append(Class(class_name, QColor(color)))

        # Создаем таблицу сетки
        table = ClassGridTable(imageSize.height() // cellSize.height(), imageSize.width() // cellSize.width())

        # Читаем данные сетки и заполняем таблицу
        for row in range(table.rows):
            cells = list(map(int, file.readline().split()))
            for col in range(table.cols):
                classIndex = cells[col]
                if classIndex != 0:
                    table.setClassToCell(row, col, classes[classIndex - 1])

        return ClassGrid(table, classes, cellSize, imageSize)


class ClassGridSerializer:
    """
    Класс для сериализации (сохранения) сетки разметки в текстовый файл.
    """

    @staticmethod
    def toTxt(file: TextIOWrapper, grid: ClassGrid):
        """
        Сохраняет объект ClassGrid в текстовый файл.

        :param file: Открытый текстовый файл для записи.
        :param grid: Экземпляр ClassGrid для сохранения.
        """
        # Записываем размер ячеек
        file.write(f"{grid.cellSize.width()} {grid.cellSize.height()}\n")

        # Записываем список классов с их цветами
        classes = [f'{_class._name}~{_class._color.name()}' for _class in grid.classes]
        file.write(f"{';'.join(classes)}\n")

        # Записываем данные сетки
        for row in range(grid.table.rows):
            cells = [0] * grid.table.cols  # По умолчанию все ячейки пустые
            for col in range(grid.table.cols):
                _class = grid.table.getCellClass(row, col)
                if _class is not None:
                    cells[col] = grid.classes.index(_class) + 1  # Индексация классов с 1
            file.write(f"{' '.join(map(str, cells))}\n")
