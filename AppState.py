from Core.Grid.Class import Class
from Core.Grid.ClassGrid import ClassGrid
from enum import Enum
from PyQt5.QtCore import QObject, pyqtSignal
from PyQt5.QtGui import QPixmap
from Core.Folder import Folder
from typing import Optional


class Tool(Enum):
    """
    Перечисление инструментов для работы с разметкой.
    """
    NO_TOOL = 1  # Без инструмента
    ASSIGN_TOOL = 2  # Назначение класса ячейке
    DELETE_TOOL = 3  # Удаление класса из ячейки
    SELECT_AREA_TOOL = 4  # Выделение области


class AppEvents(QObject):
    """
    Класс сигналов для событий приложения.
    Позволяет реагировать на изменения состояния.
    """

    beforeGridSetEvent = pyqtSignal()  # Перед установкой новой сетки
    afterGridSetEvent = pyqtSignal()  # После установки новой сетки
    onImageSetEvent = pyqtSignal()  # При установке нового изображения
    beforeToolChangeEvent = pyqtSignal()  # Перед сменой инструмента
    afterToolChangeEvent = pyqtSignal()  # После смены инструмента
    beforeFolderSetEvent = pyqtSignal()  # Перед сменой папки с изображениями
    afterFolderSetEvent = pyqtSignal()  # После смены папки с изображениями
    activeClassChanged = pyqtSignal(object)  # Передает новый активный класс разметки


class AppState:
    """
    Глобальное состояние приложения, хранящее активные классы, сетку, изображение, инструмент и папку.
    """

    def __init__(self):
        """
        Инициализирует состояние приложения.
        """
        self.events = AppEvents()
        self.activeClass: Class = None  # Текущий активный класс разметки
        self.activeTool: Tool = Tool.NO_TOOL  # Текущий инструмент разметки
        self.activeGrid: ClassGrid = None  # Текущая сетка разметки
        self.activeImage: QPixmap = None  # Текущее изображение
        self.activeFolder: Folder = None  # Текущая папка с изображениями

    def setActiveGrid(self, grid: ClassGrid):
        """
        Устанавливает активную сетку разметки и обновляет активный класс.

        :param grid: Экземпляр ClassGrid.
        """
        if self.activeGrid is not None:
            self.events.beforeGridSetEvent.emit()
        self.activeGrid = grid

        if self.activeGrid is not None and self.activeGrid.classes:
            # Если в сетке есть классы, выбираем первый в качестве активного
            self.setActiveClass(self.activeGrid.classes[0])

        self.events.afterGridSetEvent.emit()

    def setActiveImage(self, image: QPixmap):
        """
        Устанавливает активное изображение.

        :param image: Экземпляр QPixmap.
        """
        self.activeImage = image
        self.events.onImageSetEvent.emit()

    def setActiveImageAndGrid(self, image: QPixmap, grid: Optional[ClassGrid]):
        """
        Устанавливает активное изображение и сетку одновременно.

        :param image: Экземпляр QPixmap.
        :param grid: Экземпляр ClassGrid или None.
        """
        self.setActiveImage(image)
        self.setActiveGrid(grid)

    def setActiveTool(self, tool: Tool):
        """
        Устанавливает активный инструмент для разметки.

        :param tool: Инструмент из перечисления Tool.
        """
        if self.activeTool == Tool.SELECT_AREA_TOOL:
            self.events.beforeToolChangeEvent.emit()
        self.activeTool = tool
        self.events.afterToolChangeEvent.emit()  # Эмитируем событие после смены инструмента

    def setActiveClass(self, _class: Class):
        """
        Устанавливает активный класс разметки.

        :param _class: Экземпляр Class.
        """
        self.activeClass = _class
        self.events.activeClassChanged.emit(_class)  # Эмитируем сигнал о смене класса

    def setActiveFolder(self, folder: Folder):
        """
        Устанавливает активную папку с изображениями.

        :param folder: Экземпляр Folder.
        """
        if self.activeFolder is not None:
            self.events.beforeFolderSetEvent.emit()
        self.activeFolder = folder
        self.events.afterFolderSetEvent.emit()
