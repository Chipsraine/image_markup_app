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
    def __init__(self, parent=None):
        print("ClassGridGraphicsView: __init__()")
        super().__init__(parent)

        self.setScene(QGraphicsScene())
        print("Scene created.")

        self.source_image_item = QGraphicsPixmapItem()
        self.mask_image_item = QGraphicsPixmapItem()
        self.tool_image_item = QGraphicsPixmapItem()

        self.source_image = None
        self.mask_image = None
        self.tool_image = None

        self.scene().addItem(self.source_image_item)
        self.scene().addItem(self.mask_image_item)
        self.scene().addItem(self.tool_image_item)
        print("Pixmap items added to scene.")

        # Переназначаем обработчики событий мыши для source_image_item
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
        print("ClassGridGraphicsView: Initialization complete.")

    def isGridSet(self):
        return self.appState.activeGrid != None and self.appState.activeImage != None

    def isInteractable(self):
        return self.appState.activeClass != None and self.isGridSet()

    def setAppSettings(self, settings : AppState):
        print("setAppSettings() called")
        self.appState = settings

    def setAllEmptyCellsToActiveClass(self):
        if self.isInteractable():
            self.appState.activeGrid.fillEmptyCellsWithClass(self.appState.activeClass)

    def getEventPoint(self, event):
        x = int(event.pos().x())
        y = int(event.pos().y())

        col = x // self.appState.activeGrid.cellSize.width()
        row = y // self.appState.activeGrid.cellSize.height()

        return Point(row, col)

    def fitImageInView(self):
        try:
            rect = self.source_image_item.boundingRect()
            print("fitImageInView: source_image_item.boundingRect() =", rect)
            ratioX = self.contentsRect().width() / rect.width() if rect.width() > 0 else 1
            ratioY = self.contentsRect().height() / rect.height() if rect.height() > 0 else 1
            self.resetTransform()
            ratio = min(ratioX, ratioY)
            self.scale(ratio, ratio)
            print("fitImageInView: Scale applied with ratio", ratio)
        except Exception as e:
            print("Exception in fitImageInView():", e)
    def mousePressOnGrid(self, event: QMouseEvent):
        print("mousePressOnGrid() called")
        if not self.isGridSet():
            print("mousePressOnGrid: Grid not set")
            return

        if (event.buttons() ^ Qt.MouseButton.LeftButton) != Qt.MouseButton.NoButton:
            self.mousePressed = False
            print("mousePressOnGrid: Left button not pressed exclusively")
            return

        eventPoint = self.getEventPoint(event)
        self.lastTouchedPoint = eventPoint

        if self.appState.activeGrid.table.isCellInsideGrid(eventPoint.row, eventPoint.col):
            if self.appState.activeTool == Tool.SELECT_AREA_TOOL:
                self.selectArea.setFirstPoint(eventPoint)
                self.selectArea.setSecondPoint(eventPoint)
                print("mousePressOnGrid: Area selection started at", eventPoint.row, eventPoint.col)
            self.manageMouseTool(eventPoint)
        self.mousePressed = True

    def mouseInWidget(self, event):
        scrollOffsetX = self.verticalScrollBar().width() if self.verticalScrollBar().isVisible() else 0
        scrollOffsetY = self.horizontalScrollBar().height() if self.horizontalScrollBar().isVisible() else 0
        widgetWidth = self.geometry().size().width() - scrollOffsetX
        widgetHeight = self.geometry().size().height() - scrollOffsetY
        allowedAreaRect = QRect(self.mapToGlobal(QPoint(self.geometry().topLeft())), QSize(widgetWidth, widgetHeight))
        return allowedAreaRect.contains(self.mapToParent(event.screenPos()))

    def mouseMoveOnGrid(self, event):

        if self.mousePressed == False or not self.isGridSet() or not self.mouseInWidget(event):
            return

        eventPoint = self.getEventPoint(event)

        if self.lastTouchedPoint == eventPoint or not self.appState.activeGrid.table.isCellInsideGrid(eventPoint.row,
                                                                                                      eventPoint.col):
            return

        if self.appState.activeTool == Tool.SELECT_AREA_TOOL:
            self.selectArea.setSecondPoint(eventPoint)
        self.manageMouseTool(eventPoint)
        self.lastTouchedPoint = eventPoint

    def mouseReleaseOnGrid(self, event):
        # Если выбран режим выделения области, сразу применяем заливку
        if self.appState.activeTool == Tool.SELECT_AREA_TOOL:
            self.fillSelectedArea()
            # Если требуется, можно также сбросить выбранную область (удалить красную рамку)
            self.resetToolLayer()
        self.lastTouchedPoint = None
        self.mousePressed = False

    def manageMouseTool(self, point):
        activeTool = self.appState.activeTool
        activeClass = self.appState.activeClass
        activeGrid = self.appState.activeGrid

        if activeTool == Tool.ASSIGN_TOOL and activeClass != None:
            activeGrid.setClassToCell(point.row, point.col, activeClass)
        elif activeTool == Tool.DELETE_TOOL and activeGrid.getCellClass(point.row, point.col) != None:
            activeGrid.setClassToCell(point.row, point.col, None)
        elif activeTool == Tool.SELECT_AREA_TOOL:
            self.paintToolArea()

    def updateCellHandler(self, row, col):
        painter = QPainter()
        painter.begin(self.mask_image)

        cellClass = self.appState.activeGrid.getCellClass(row, col)

        self.eraseCell(painter, row, col)

        if cellClass != None:
            self.paintCell(painter, row, col, cellClass._color)

        painter.end()

        self.mask_image_item.setPixmap(self.mask_image)

    def setImage(self):
        self.sourceHeight = self.appState.activeImage.size().height()
        self.sourceWidth = self.appState.activeImage.size().width()
        self.source_image_item.setPixmap(self.appState.activeImage)
        self.scene().setSceneRect(self.source_image_item.boundingRect())
        self.fitImageInView()

    def resizeEvent(self, event):
        self.fitImageInView()

    def unlinkGrid(self):
        self.resetMask()
        self.resetToolLayer()
        if (self.appState.activeGrid == None):
            return

        self.appState.activeGrid.signals_emitter.updateCell.disconnect(self.updateCellHandler)
        self.appState.activeGrid.signals_emitter.updateAllCells.disconnect(self.updateAllCellsHandler)

    def linkGrid(self):
        if (self.appState.activeGrid == None):
            return

        self.appState.activeGrid.signals_emitter.updateCell.connect(self.updateCellHandler)
        self.appState.activeGrid.signals_emitter.updateAllCells.connect(self.updateAllCellsHandler)
        self.updateAllCellsHandler()

    def createBlankImage(self):
        print("Entering createBlankImage()")
        try:
            # Пытаемся получить boundingRect у source_image_item
            rect = self.source_image_item.boundingRect()
            print("createBlankImage: initial boundingRect =", rect)
            if rect.isEmpty():
                print("createBlankImage: boundingRect is empty.")
                if self.appState and self.appState.activeImage:
                    rect = self.appState.activeImage.rect()
                    print("createBlankImage: using activeImage rect =", rect)
                else:
                    rect = QRectF(0, 0, 100, 100)
                    print("createBlankImage: no activeImage; using default rect (0,0,100,100)")
            img_width = int(rect.width())
            img_height = int(rect.height())
            if img_width <= 0 or img_height <= 0:
                print("createBlankImage: width or height <= 0, setting default 100x100")
                img_width, img_height = 100, 100
            print("createBlankImage: final dimensions: width =", img_width, "height =", img_height)
            n_channels = 4
            blank_array = np.zeros((img_height, img_width, n_channels), dtype=np.uint8)
            print("createBlankImage: numpy array created, shape =", blank_array.shape)
            qimg = QImage(blank_array.data, img_width, img_height, 4 * img_width, QImage.Format_RGBA8888)
            print("createBlankImage: QImage created, size =", qimg.width(), "x", qimg.height())
            qimg = qimg.copy()
            print("createBlankImage: QImage copied, size =", qimg.width(), "x", qimg.height())
            pixmap = QPixmap.fromImage(qimg)
            print("createBlankImage: QPixmap created, size =", pixmap.width(), "x", pixmap.height())
            return pixmap
        except Exception as e:
            print("Exception in createBlankImage():", e)
            raise
    def resetMask(self):
        self.mask_image = self.createBlankImage()
        self.mask_image_item.setPixmap(self.mask_image)

    def getTransparentColor(self, color, alpha):
        transparent_color = QColor(color)
        transparent_color.setAlpha(alpha)
        return transparent_color

    def getColorBrushes(self, color: QColor):
        brushes = self.brushesLookup.get(color.name(), None)
        if brushes is None:
            brushes = {"border": QBrush(self.getTransparentColor(color, self.borderOpacity)),
                       "background": QBrush(self.getTransparentColor(color, self.backgroundOpacity))}
            self.brushesLookup[color.value()] = brushes
        return brushes

    def paintCell(self, painter: QPainter, row, col, color: QColor):
        painter.setPen(Qt.PenStyle.NoPen)
        width = self.appState.activeGrid.cellSize.width()
        height = self.appState.activeGrid.cellSize.height()
        borderOffset = self.appState.activeGrid.borderOffset
        borderTotalWidth = self.appState.activeGrid.borderWidth

        topLeftX = col * width
        topLeftY = row * height

        brushes = self.getColorBrushes(color)

        painter.setBrush(brushes["border"])
        painter.drawRect(topLeftX, topLeftY, width, height)
        if width != 1 and height != 1:
            mode = painter.compositionMode()
            painter.setCompositionMode(QPainter.CompositionMode.CompositionMode_DestinationAtop)
            painter.setBrush(brushes["background"])
            painter.drawRect(topLeftX + borderOffset, topLeftY + borderOffset, width - borderTotalWidth,
                             height - borderTotalWidth)
            painter.setCompositionMode(mode)

    def eraseCell(self, painter: QPainter, row, col):
        painter.setPen(Qt.PenStyle.NoPen)
        width = self.appState.activeGrid.cellSize.width()
        height = self.appState.activeGrid.cellSize.height()

        mode = painter.compositionMode()
        painter.setCompositionMode(QPainter.CompositionMode.CompositionMode_Clear)
        painter.setBrush(QBrush(QColor(0, 0, 0, 0)))
        painter.drawRect(QRect(col * width, row * height, width, height))
        painter.setCompositionMode(mode)

    def updateAllCellsHandler(self):

        self.resetMask()

        painter = QPainter()

        painter.begin(self.mask_image)

        activeGrid = self.appState.activeGrid

        for row in range(activeGrid.table.rows):
            for col in range(activeGrid.table.cols):
                cell = activeGrid.getCellClass(row, col)
                if cell != None:
                    self.paintCell(painter, row, col, cell._color)
                    print("!!!!!!!!!!!!!!!!:",cell._color.name())
        painter.end()

        self.mask_image_item.setPixmap(self.mask_image)

    def paintToolArea(self):
        if not self.isGridSet():
            return

        painter = QPainter()

        self.tool_image = self.createBlankImage()

        painter.begin(self.tool_image)

        if self.selectArea.firstPoint != None and self.selectArea.secondPoint != None:
            cellWidth, cellHeight = self.appState.activeGrid.cellSize.width(), self.appState.activeGrid.cellSize.height()
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
        if not self.isGridSet():
            return

        if self.selectArea.firstPoint != None and self.selectArea.secondPoint != None:
            self.appState.activeGrid.setClassToArea(self.selectArea, self.appState.activeClass)

    def fillEmptyCellsWithClass(self):
        if not self.isGridSet():
            return

        self.appState.activeGrid.fillEmptyCellsWithClass(self.appState.activeClass)

    def resetToolLayer(self):
        """
        Сбрасывает слой для инструмента (например, для выделенной области).
        Этот метод вызывается при смене инструмента из режима SELECT_AREA_TOOL.
        """
        # Сброс точек выделения и последней точки
        self.selectArea.setFirstPoint(None)
        self.selectArea.setSecondPoint(None)
        self.lastTouchedPoint = None
        # Создаем новый пустой pixmap для tool_image
        try:
            blank_pixmap = self.createBlankImage()
        except Exception as e:
            print("Exception in createBlankImage during resetToolLayer:", e)
            # Если ошибка, создаем pixmap по умолчанию
            blank_pixmap = QtGui.QPixmap(100, 100)
            blank_pixmap.fill(QtCore.Qt.transparent)
        self.tool_image = blank_pixmap
        self.tool_image_item.setPixmap(self.tool_image)
