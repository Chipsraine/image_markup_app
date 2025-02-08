from PyQt5.QtGui import QImage, QPixmap
from PyQt5.QtCore import pyqtSignal, QSize, QObject
from Core.Grid.ClassGrid import ClassGrid
from PIL import Image
from ClassGridSerialization import ClassGridSerializer, ClassGridDeserializer
import os
from AppState import *

class Folder(QObject):
    """
    Класс для управления изображениями и разметками.
    Позволяет загружать изображения, управлять активным файлом и сохранять разметки.
    """

    sizeChangeProgressEvent = pyqtSignal(int, int)  # Сигнал прогресса изменения размеров сетки
    counterUpdateEvent = pyqtSignal(int, int)  # Сигнал обновления счетчика изображений

    gridsFolderName = "grids"

    def __init__(self, folderPath, appState):
        """
        Инициализирует объект для работы с папкой изображений.

        :param folderPath: Путь к папке с изображениями.
        :param appState: Глобальное состояние приложения.
        """
        super().__init__(None)
        self.folderPath = folderPath
        self.appState: AppState = appState
        self.imageFilenames = None
        self.activeFileIndex = -1
        self.totalFilesCount = 0

        # Создает подпапку "grids" для хранения разметок, если её нет
        grids_path = os.path.join(self.folderPath, self.gridsFolderName)
        if not os.path.exists(grids_path):
            os.makedirs(grids_path)

        self.loadDirectory()

    def loadDirectory(self):
        """
        Загружает список изображений из папки.
        """
        self.imageFilenames = self.getImageFilenames(self.folderPath)
        self.totalFilesCount = len(self.imageFilenames)

    @staticmethod
    def getImageFilenames(path):
        """
        Возвращает список имен файлов изображений в папке.

        :param path: Путь к папке.
        :return: Список имен изображений.
        """
        image_extensions = ['.jpg', '.png']
        return [filename for filename in os.listdir(path)
                if os.path.splitext(filename)[1].lower() in image_extensions and os.path.isfile(os.path.join(path, filename))]

    def getImagePath(self, filename):
        """
        Возвращает полный путь к изображению.

        :param filename: Имя файла.
        :return: Полный путь к изображению.
        """
        return os.path.join(self.folderPath, filename)

    def getGridPath(self, filename):
        """
        Возвращает путь к файлу разметки.

        :param filename: Имя файла изображения.
        :return: Полный путь к файлу разметки.
        """
        return os.path.join(self.folderPath, self.gridsFolderName, filename + ".txt")

    def getImage(self, filename):
        """
        Загружает изображение в формате QPixmap.

        :param filename: Имя файла изображения.
        :return: Объект QPixmap или None, если файл отсутствует.
        """
        imagePath = self.getImagePath(filename)
        return QPixmap(imagePath) if os.path.exists(imagePath) else None

    def getGrid(self, filename):
        """
        Загружает разметку сетки для изображения.

        :param filename: Имя файла изображения.
        :return: Объект ClassGrid или None, если файла разметки нет.
        """
        imagePath = self.getImagePath(filename)
        gridPath = self.getGridPath(filename)

        if not self.imageExists(filename) or not os.path.exists(gridPath):
            return None

        with Image.open(imagePath) as imageInfo:
            width, height = imageInfo.size

        with open(gridPath, 'r', encoding='utf-8') as fileRead:
            return ClassGridDeserializer.fromTxt(fileRead, QSize(width, height))

    def imageExists(self, filename):
        """
        Проверяет, существует ли изображение.

        :param filename: Имя файла.
        :return: True, если изображение существует, иначе False.
        """
        return os.path.exists(self.getImagePath(filename))

    def getActiveFilename(self):
        """
        Возвращает имя активного файла изображения.

        :return: Имя активного файла.
        """
        return self.imageFilenames[self.activeFileIndex]

    def saveActiveGrid(self):
        """
        Сохраняет активную разметку в файл.
        """
        if self.appState.activeGrid is None:
            return

        gridPath = self.getGridPath(self.getActiveFilename())
        with open(gridPath, 'w', encoding='utf-8') as fileWrite:
            ClassGridSerializer.toTxt(fileWrite, self.appState.activeGrid)

    def switchToPreviousImage(self):
        """
        Переключает активное изображение на предыдущее.
        """
        if 0 <= self.activeFileIndex < self.totalFilesCount:
            self.saveActiveGrid()

        self.activeFileIndex -= 1

        while self.activeFileIndex >= 0 and not self.imageExists(self.getActiveFilename()):
            self.activeFileIndex -= 1

        if 0 <= self.activeFileIndex < self.totalFilesCount:
            self.setActiveImage()
            return

        self.loadDirectory()
        if self.totalFilesCount > 0:
            self.activeFileIndex = self.totalFilesCount - 1
            self.switchToPreviousImage()

    def switchToNextImage(self):
        """
        Переключает активное изображение на следующее.
        """
        if 0 <= self.activeFileIndex < self.totalFilesCount:
            self.saveActiveGrid()

        self.activeFileIndex += 1

        while self.activeFileIndex < self.totalFilesCount and not self.imageExists(self.getActiveFilename()):
            self.activeFileIndex += 1

        if 0 <= self.activeFileIndex < self.totalFilesCount:
            self.setActiveImage()
            return

        self.loadDirectory()
        if self.totalFilesCount > 0:
            self.activeFileIndex = -1
            self.switchToNextImage()

    def setActiveImage(self):
        """
        Устанавливает текущее изображение как активное и обновляет его разметку.
        """
        imageFilename = self.getActiveFilename()
        image = self.getImage(imageFilename)
        grid = self.getGrid(imageFilename)
        self.appState.setActiveImageAndGrid(image, grid)
        self.updateCounter()

    def updateCounter(self):
        """
        Обновляет счетчик изображений.
        """
        self.counterUpdateEvent.emit(self.activeFileIndex + 1, self.totalFilesCount)

    def changeAllGridCellSizes(self, cellSize):
        """
        Изменяет размеры ячеек разметки для всех изображений в папке.

        :param cellSize: Новый размер ячеек.
        """
        for fileIndex, filename in enumerate(self.imageFilenames):
            if fileIndex == self.activeFileIndex:
                continue

            grid: ClassGrid = self.getGrid(filename)
            if grid is None or not grid.canCellSizeFitInGrid(cellSize) or grid.hasSameCellSize(cellSize):
                continue

            grid.applyResizeStrategy(cellSize)
            gridPath = self.getGridPath(filename)
            with open(gridPath, 'w', encoding='utf-8') as fileWrite:
                ClassGridSerializer.toTxt(fileWrite, grid)

            self.sizeChangeProgressEvent.emit(fileIndex + 1, self.totalFilesCount)

    def createGrids(self, cellSize):
        """
        Создает разметку сетки для всех изображений в папке.

        :param cellSize: Размер ячейки разметки.
        """
        for fileIndex, filename in enumerate(self.imageFilenames):
            if fileIndex == self.activeFileIndex or not self.imageExists(filename):
                continue

            try:
                with Image.open(self.getImagePath(filename)) as imageInfo:
                    width, height = imageInfo.size
                    gridSize = QSize(width, height)

                if not (cellSize.width() <= gridSize.width() and cellSize.height() <= gridSize.height()):
                    continue

                gridPath = self.getGridPath(filename)
                with open(gridPath, 'w', encoding='utf-8') as fileWrite:
                    new_grid = ClassGrid(None, None, cellSize, gridSize)
                    ClassGridSerializer.toTxt(fileWrite, new_grid)

                self.sizeChangeProgressEvent.emit(fileIndex + 1, self.totalFilesCount)
            except Exception:
                pass
