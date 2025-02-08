from PyQt5.QtWidgets import QGraphicsScene, QGraphicsPixmapItem
from PyQt5.QtGui import QImage, QPainter, QColor, QPen, QBrush, QMouseEvent
from PyQt5.QtCore import Qt, QRect, QPoint, QSize, QRectF

import numpy as np
from PyQt5.uic.properties import QtCore, QtGui

from forms.implemented_widgets.ZoomableGraphicsView import ZoomableGraphicsView
from Core.Area.Area import Area
from Core.Area.Point import Point
from AppState import *


class ClassGridGraphicsView(ZoomableGraphicsView):
    """
    Виджет для отображения изображения с наложенной сеткой разметки.
    Позволяет взаимодействовать с разметкой: выделять области, изменять классы,
    рисовать ячейки сетки и изменять их параметры.
    """

    def __init__(self, parent=None):
        """
        Инициализирует графическое представление сетки разметки.

        :param parent: Родительский объект.
        """
        super().__init__(parent)
        self.setScene(QGraphicsScene())

        # Создаем графические элементы для изображения, маски и инструментов
        self.source_image_item = QGraphicsPixmapItem()
        self.mask_image_item = QGraphicsPixmapItem()
        self.tool_image_item = QGraphicsPixmapItem()

        self.source_image = None
        self.mask_image = None
        self.tool_image = None

        self.scene().addItem(self.source_image_item)
        self.scene().addItem(self.mask_image_item)
        self.scene().addItem(self.tool_image_item)

        # Назначаем обработчики событий мыши
        self.source_image_item.mousePressEvent = self.mousePressOnGrid
        self.source_image_item.mouseMoveEvent = self.mouseMoveOnGrid
        self.source_image_item.mouseReleaseEvent = self.mouseReleaseOnGrid

        self.appState: AppState = None
        self.selectArea: Area = Area()

        self.mouseInside = False
        self.mousePressed = False
        self.lastTouchedPoint = None

        self.borderOpacity = 196
        self.backgroundOpacity = 128
        self.brushesLookup: dict[str, dict] = {}

    def isGridSet(self):
        """
        Проверяет, установлена ли сетка и изображение.

        :return: True, если сетка и изображение загружены, иначе False.
        """
        return self.appState.activeGrid is not None and self.appState.activeImage is not None


    def isInteractable(self):
        """
        Проверяет, можно ли взаимодействовать с разметкой.

        :return: True, если активен класс разметки и установлена сетка.
        """
        return self.appState.activeClass is not None and self.isGridSet()

    def setAppSettings(self, settings: AppState):
        """
        Устанавливает настройки приложения.

        :param settings: Экземпляр AppState.
        """
        self.appState = settings


    def setAllEmptyCellsToActiveClass(self):
        """
        Заполняет все пустые ячейки текущим активным классом разметки.
        """
        if self.isInteractable():
            self.appState.activeGrid.fillEmptyCellsWithClass(self.appState.activeClass)

    def getEventPoint(self, event):
        """
        Получает координаты точки в сетке из события мыши.

        :param event: Событие мыши.
        :return: Объект Point с координатами в сетке или None, если сетка не установлена.
        """
        if not self.isGridSet():
            return None  # Безопасная проверка, если сетка еще не загружена

        x = int(event.pos().x())
        y = int(event.pos().y())

        col = x // self.appState.activeGrid.cellSize.width()
        row = y // self.appState.activeGrid.cellSize.height()

        return Point(row, col)

    def fitImageInView(self):
        """
        Масштабирует изображение так, чтобы оно полностью вписывалось в область отображения.
        """
        try:
            rect = self.source_image_item.boundingRect()
            if rect.width() > 0 and rect.height() > 0:
                ratioX = self.contentsRect().width() / rect.width()
                ratioY = self.contentsRect().height() / rect.height()
                self.resetTransform()
                self.scale(min(ratioX, ratioY), min(ratioX, ratioY))
        except Exception:
            pass  # Игнорируем возможные ошибки, чтобы не прерывать выполнение программы

    def mousePressOnGrid(self, event: QMouseEvent):
        """
        Обрабатывает нажатие кнопки мыши по сетке разметки.

        :param event: Событие нажатия мыши.
        """
        if not self.isGridSet():
            return

        # Проверяем, была ли нажата только левая кнопка мыши
        if event.buttons() != Qt.LeftButton:
            self.mousePressed = False
            return

        eventPoint = self.getEventPoint(event)
        self.lastTouchedPoint = eventPoint

        # Проверяем, находится ли точка внутри сетки
        if self.appState.activeGrid.table.isCellInsideGrid(eventPoint.row, eventPoint.col):
            if self.appState.activeTool == Tool.SELECT_AREA_TOOL:
                self.selectArea.setFirstPoint(eventPoint)
                self.selectArea.setSecondPoint(eventPoint)
            self.manageMouseTool(eventPoint)

        self.mousePressed = True

    def mouseInWidget(self, event):
        """
        Проверяет, находится ли курсор мыши внутри виджета с учетом прокрутки.

        :param event: Событие перемещения мыши.
        :return: True, если курсор внутри виджета, иначе False.
        """
        scrollOffsetX = self.verticalScrollBar().width() if self.verticalScrollBar().isVisible() else 0
        scrollOffsetY = self.horizontalScrollBar().height() if self.horizontalScrollBar().isVisible() else 0

        widgetWidth = self.geometry().width() - scrollOffsetX
        widgetHeight = self.geometry().height() - scrollOffsetY

        allowedAreaRect = QRect(self.mapToGlobal(self.geometry().topLeft()), QSize(widgetWidth, widgetHeight))

        return allowedAreaRect.contains(self.mapToParent(event.screenPos()))

    def mouseMoveOnGrid(self, event):
        """
        Обрабатывает перемещение мыши по сетке.

        :param event: Событие перемещения мыши.
        """
        if not self.mousePressed or not self.isGridSet() or not self.mouseInWidget(event):
            return

        eventPoint = self.getEventPoint(event)

        # Проверяем, изменилась ли точка или находится ли она внутри сетки
        if self.lastTouchedPoint == eventPoint or not self.appState.activeGrid.table.isCellInsideGrid(eventPoint.row,
                                                                                                      eventPoint.col):
            return

        if self.appState.activeTool == Tool.SELECT_AREA_TOOL:
            self.selectArea.setSecondPoint(eventPoint)

        self.manageMouseTool(eventPoint)
        self.lastTouchedPoint = eventPoint

    def mouseReleaseOnGrid(self, event):
        """
        Обрабатывает отпускание кнопки мыши на сетке.

        :param event: Событие отпускания мыши.
        """
        if self.appState.activeTool == Tool.SELECT_AREA_TOOL:
            self.fillSelectedArea()
            self.resetToolLayer()  # Сбрасывает выделенную область после заполнения

        self.lastTouchedPoint = None
        self.mousePressed = False

    def manageMouseTool(self, point):
        """
        Управляет действиями инструментов разметки в зависимости от выбранного режима.

        :param point: Точка, в которой выполняется действие.
        """
        activeTool = self.appState.activeTool
        activeClass = self.appState.activeClass
        activeGrid = self.appState.activeGrid

        if activeTool == Tool.ASSIGN_TOOL and activeClass is not None:
            activeGrid.setClassToCell(point.row, point.col, activeClass)
        elif activeTool == Tool.DELETE_TOOL and activeGrid.getCellClass(point.row, point.col) is not None:
            activeGrid.setClassToCell(point.row, point.col, None)
        elif activeTool == Tool.SELECT_AREA_TOOL:
            self.paintToolArea()

    def updateCellHandler(self, row, col):
        """
        Обновляет ячейку разметки в графическом интерфейсе.

        :param row: Номер строки ячейки.
        :param col: Номер колонки ячейки.
        """
        painter = QPainter()
        painter.begin(self.mask_image)

        cellClass = self.appState.activeGrid.getCellClass(row, col)

        self.eraseCell(painter, row, col)

        if cellClass is not None:
            self.paintCell(painter, row, col, cellClass._color)

        painter.end()

        self.mask_image_item.setPixmap(self.mask_image)

    def setImage(self):
        """
        Устанавливает изображение в графическую сцену и масштабирует его.
        """
        self.sourceHeight = self.appState.activeImage.size().height()
        self.sourceWidth = self.appState.activeImage.size().width()
        self.source_image_item.setPixmap(self.appState.activeImage)
        self.scene().setSceneRect(self.source_image_item.boundingRect())
        self.fitImageInView()

    def resizeEvent(self, event):
        """
        Обрабатывает изменение размера виджета.

        :param event: Событие изменения размера.
        """
        self.fitImageInView()

    def unlinkGrid(self):
        """
        Отключает сетку разметки, сбрасывая все связанные элементы.
        """
        self.resetMask()
        self.resetToolLayer()
        if self.appState.activeGrid is None:
            return

        self.appState.activeGrid.signals_emitter.updateCell.disconnect(self.updateCellHandler)
        self.appState.activeGrid.signals_emitter.updateAllCells.disconnect(self.updateAllCellsHandler)


    def linkGrid(self):
        """
        Подключает сетку разметки, обновляя все связанные элементы.
        """
        if self.appState.activeGrid is None:
            return

        self.appState.activeGrid.signals_emitter.updateCell.connect(self.updateCellHandler)
        self.appState.activeGrid.signals_emitter.updateAllCells.connect(self.updateAllCellsHandler)
        self.updateAllCellsHandler()

    def createBlankImage(self):
        """
        Создает пустое изображение (QPixmap) с размерами активного изображения.
        Используется для маски и инструментов рисования.

        :return: Пустой QPixmap соответствующего размера.
        """
        try:
            rect = self.source_image_item.boundingRect()

            # Если boundingRect пустой, используем размеры активного изображения
            if rect.isEmpty():
                if self.appState and self.appState.activeImage:
                    rect = self.appState.activeImage.rect()
                else:
                    rect = QRectF(0, 0, 100, 100)  # Значение по умолчанию

            img_width = int(rect.width())
            img_height = int(rect.height())

            # Если размеры недопустимы, устанавливаем стандартные 100x100
            if img_width <= 0 or img_height <= 0:
                img_width, img_height = 100, 100

            n_channels = 4  # RGBA-формат
            blank_array = np.zeros((img_height, img_width, n_channels), dtype=np.uint8)

            qimg = QImage(blank_array.data, img_width, img_height, 4 * img_width, QImage.Format_RGBA8888)
            pixmap = QPixmap.fromImage(qimg.copy())  # Создаем копию QImage для безопасности

            return pixmap
        except Exception:
            return QPixmap(100, 100)  # Если произошла ошибка, возвращаем пустой 100x100 QPixmap

    def resetMask(self):
        """
        Сбрасывает маску разметки, создавая новое пустое изображение.
        """
        self.mask_image = self.createBlankImage()
        self.mask_image_item.setPixmap(self.mask_image)

    def getTransparentColor(self, color, alpha):
        """
        Создает прозрачную версию заданного цвета.

        :param color: Исходный цвет (QColor).
        :param alpha: Уровень прозрачности (0-255).
        :return: Новый QColor с заданной прозрачностью.
        """
        transparent_color = QColor(color)
        transparent_color.setAlpha(alpha)
        return transparent_color

    def getColorBrushes(self, color: QColor):
        """
        Возвращает кисти для границы и фона ячейки разметки.
        Если кисти для данного цвета уже существуют, использует кэш.

        :param color: Цвет (QColor).
        :return: Словарь с кистями для границы и фона.
        """
        if color.name() not in self.brushesLookup:
            self.brushesLookup[color.name()] = {
                "border": QBrush(self.getTransparentColor(color, self.borderOpacity)),
                "background": QBrush(self.getTransparentColor(color, self.backgroundOpacity))
            }
        return self.brushesLookup[color.name()]

    def paintCell(self, painter: QPainter, row, col, color: QColor):
        """
        Отрисовывает ячейку разметки с заданным цветом.

        :param painter: Объект QPainter для рисования.
        :param row: Номер строки ячейки.
        :param col: Номер колонки ячейки.
        :param color: Цвет заливки ячейки.
        """
        painter.setPen(Qt.PenStyle.NoPen)

        width = self.appState.activeGrid.cellSize.width()
        height = self.appState.activeGrid.cellSize.height()
        borderOffset = self.appState.activeGrid.borderOffset
        borderTotalWidth = self.appState.activeGrid.borderWidth

        topLeftX = col * width
        topLeftY = row * height

        brushes = self.getColorBrushes(color)

        # Рисуем границу ячейки
        painter.setBrush(brushes["border"])
        painter.drawRect(topLeftX, topLeftY, width, height)

        # Если ячейка не минимального размера, рисуем фон
        if width > 1 and height > 1:
            mode = painter.compositionMode()
            painter.setCompositionMode(QPainter.CompositionMode.CompositionMode_DestinationAtop)
            painter.setBrush(brushes["background"])
            painter.drawRect(topLeftX + borderOffset, topLeftY + borderOffset, width - borderTotalWidth,
                             height - borderTotalWidth)
            painter.setCompositionMode(mode)

    def eraseCell(self, painter: QPainter, row, col):
        """
        Очищает ячейку разметки, делая ее прозрачной.

        :param painter: Объект QPainter для рисования.
        :param row: Номер строки ячейки.
        :param col: Номер колонки ячейки.
        """
        painter.setPen(Qt.PenStyle.NoPen)
        width = self.appState.activeGrid.cellSize.width()
        height = self.appState.activeGrid.cellSize.height()

        mode = painter.compositionMode()
        painter.setCompositionMode(QPainter.CompositionMode.CompositionMode_Clear)
        painter.setBrush(QBrush(QColor(0, 0, 0, 0)))
        painter.drawRect(QRect(col * width, row * height, width, height))
        painter.setCompositionMode(mode)

    def updateAllCellsHandler(self):
        """
        Обновляет всю сетку разметки в графическом интерфейсе.
        """
        self.resetMask()

        painter = QPainter()
        painter.begin(self.mask_image)

        activeGrid = self.appState.activeGrid

        for row in range(activeGrid.table.rows):
            for col in range(activeGrid.table.cols):
                cell = activeGrid.getCellClass(row, col)
                if cell is not None:
                    self.paintCell(painter, row, col, cell._color)

        painter.end()
        self.mask_image_item.setPixmap(self.mask_image)

    def paintToolArea(self):
        """
        Отрисовывает выделенную область для инструмента выделения.
        """
        if not self.isGridSet():
            return

        painter = QPainter()
        self.tool_image = self.createBlankImage()
        painter.begin(self.tool_image)

        if self.selectArea.firstPoint and self.selectArea.secondPoint:
            cellWidth = self.appState.activeGrid.cellSize.width()
            cellHeight = self.appState.activeGrid.cellSize.height()

            x1, y1 = min(self.selectArea.firstPoint.col, self.selectArea.secondPoint.col) * cellWidth, min(
                self.selectArea.firstPoint.row, self.selectArea.secondPoint.row) * cellHeight
            x2, y2 = max(self.selectArea.firstPoint.col, self.selectArea.secondPoint.col) * cellWidth, max(
                self.selectArea.firstPoint.row, self.selectArea.secondPoint.row) * cellHeight
            areaWidth = (x2 - x1) + cellWidth
            areaHeight = (y2 - y1) + cellHeight

            paintingRect = QRect(x1, y1, areaWidth, areaHeight)
            painter.setPen(
                QPen(Qt.GlobalColor.red, 2, Qt.PenStyle.SolidLine, Qt.PenCapStyle.FlatCap, Qt.PenJoinStyle.MiterJoin))
            painter.setBackground(QColor(0, 0, 0, 0))
            painter.drawRect(paintingRect)

        painter.end()
        self.tool_image_item.setPixmap(self.tool_image)

    def fillSelectedArea(self):
        """
        Заполняет выделенную область активным классом разметки.
        """
        if not self.isGridSet():
            return

        if self.selectArea.firstPoint and self.selectArea.secondPoint:
            self.appState.activeGrid.setClassToArea(self.selectArea, self.appState.activeClass)

    def fillEmptyCellsWithClass(self):
        """
        Заполняет все пустые ячейки активным классом разметки.
        """
        if not self.isGridSet():
            return

        self.appState.activeGrid.fillEmptyCellsWithClass(self.appState.activeClass)

    def resetToolLayer(self):
        """
        Сбрасывает слой инструмента, очищая выделенные области.
        """
        self.selectArea.setFirstPoint(None)
        self.selectArea.setSecondPoint(None)
        self.lastTouchedPoint = None

        try:
            blank_pixmap = self.createBlankImage()
        except Exception:
            blank_pixmap = QtGui.QPixmap(100, 100)
            blank_pixmap.fill(QtCore.Qt.transparent)

        self.tool_image = blank_pixmap
        self.tool_image_item.setPixmap(self.tool_image)

