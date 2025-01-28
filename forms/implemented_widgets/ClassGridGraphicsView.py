
from PyQt5.QtWidgets import QGraphicsScene, QGraphicsPixmapItem
from PyQt5.QtGui import QPixmap, QImage, QPainter, QColor, QPen, QBrush, QMouseEvent
from PyQt5.QtCore import Qt, QRect, QPoint, QSize

import numpy as np
from forms.implemented_widgets.ZoomableGraphicsView import ZoomableGraphicsView
from Core.Area.Area import Area
from Core.Area.Point import Point
from AppState import *


class ClassGridGraphicsView(ZoomableGraphicsView):
    def __init__(self, parent=None):
        super().__init__(parent)
        
        self.setScene(QGraphicsScene())
        
        self.source_image_item = QGraphicsPixmapItem()
        self.mask_image_item = QGraphicsPixmapItem()
        self.tool_image_item = QGraphicsPixmapItem()
        
        self.source_image = None
        self.mask_image = None
        self.tool_image = None
        
        self.scene().addItem(self.source_image_item)
        self.scene().addItem(self.mask_image_item)
        self.scene().addItem(self.tool_image_item)
        
        self.source_image_item.mousePressEvent = self.mousePressOnGrid
        self.source_image_item.mouseMoveEvent = self.mouseMoveOnGrid
        self.source_image_item.mouseReleaseEvent = self.mouseReleaseOnGrid
        
        self.appState : AppState = None
        self.selectArea : Area = Area()
        
        self.mouseInside = False
        self.mousePressed = False
        self.lastTouchedPoint = None
        
        self.borderOpacity = 196
        self.backgroundOpacity = 128
        self.brushesLookup : dict[int, dict] = {}
    
    def isGridSet(self):
        return self.appState.activeGrid != None and self.appState.activeImage != None
    
    def isInteractable(self):
        return self.appState.activeClass != None and self.isGridSet()
    
    def setAppSettings(self, settings : AppState):
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
        self.resetScale(self.contentsRect().width() / self.source_image_item.boundingRect().width(), self.contentsRect().height() / self.source_image_item.boundingRect().height())

    def mousePressOnGrid(self, event:QMouseEvent):
        if (event.buttons() ^ Qt.MouseButton.LeftButton) != Qt.MouseButton.NoButton:
            self.mousePressed = False
            return
        
        eventPoint = self.getEventPoint(event)      
        self.lastTouchedPoint = eventPoint
        
        if self.isInteractable() and self.appState.activeGrid.table.isCellInsideGrid(eventPoint.row, eventPoint.col):
            if self.appState.activeTool == Tool.SELECT_AREA_TOOL:
                self.selectArea.setFirstPoint(eventPoint)
                self.selectArea.setSecondPoint(eventPoint)
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
        
        if self.lastTouchedPoint == eventPoint or not self.appState.activeGrid.table.isCellInsideGrid(eventPoint.row, eventPoint.col):
            return
        
        if self.appState.activeTool == Tool.SELECT_AREA_TOOL:
            self.selectArea.setSecondPoint(eventPoint)
        self.manageMouseTool(eventPoint)
        self.lastTouchedPoint = eventPoint
        
        
    def mouseReleaseOnGrid(self, event):
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
        self.appState.activeGrid.signals_emitter.updateCell.disconnect(self.updateCellHandler)
        self.appState.activeGrid.signals_emitter.updateAllCells.disconnect(self.updateAllCellsHandler)
        
    def linkGrid(self):
        self.appState.activeGrid.signals_emitter.updateCell.connect(self.updateCellHandler)
        self.appState.activeGrid.signals_emitter.updateAllCells.connect(self.updateAllCellsHandler)
        self.updateAllCellsHandler()

    def createBlankImage(self):
        img_height, img_width = int(self.source_image_item.boundingRect().height()), int(self.source_image_item.boundingRect().width())
        n_channels = 4
        blank_array = np.zeros((img_height, img_width, n_channels), dtype=np.uint8)
        return QPixmap(QImage(blank_array.data, img_width, img_height, 4 * img_width, QImage.Format.Format_RGBA8888))
    
    def resetMask(self):
        self.mask_image = self.createBlankImage()
        self.mask_image_item.setPixmap(self.mask_image)

        
        
    def getTransparentColor(self, color, alpha):
        transparent_color = QColor(color)
        transparent_color.setAlpha(alpha)
        return transparent_color
        
    def getColorBrushes(self, color:QColor):
        brushes = self.brushesLookup.get(color.value(), None)
        if brushes is None:
            brushes = {"border": QBrush(self.getTransparentColor(color, self.borderOpacity)), "background" : QBrush(self.getTransparentColor(color, self.backgroundOpacity))}
            self.brushesLookup[color.value()] = brushes
        return brushes
        
        
    def paintCell(self, painter : QPainter, row, col, color:QColor):
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
            painter.drawRect(topLeftX + borderOffset, topLeftY + borderOffset, width - borderTotalWidth, height - borderTotalWidth)
            painter.setCompositionMode(mode)     

    def eraseCell(self, painter : QPainter, row, col):
        painter.setPen(Qt.PenStyle.NoPen)
        width = self.appState.activeGrid.cellSize.width()
        height = self.appState.activeGrid.cellSize.height()
        
        
        mode = painter.compositionMode()
        painter.setCompositionMode(QPainter.CompositionMode.CompositionMode_Clear)
        painter.setBrush(QBrush(QColor(0,0,0,0)))
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
            x, y = self.selectArea.firstPoint.col * cellWidth, self.selectArea.firstPoint.row * cellHeight
            offsetCol = 1 if self.selectArea.secondPoint.col >= self.selectArea.firstPoint.col else 0
            offsetRow = 1 if self.selectArea.secondPoint.row >= self.selectArea.firstPoint.row else 0
            areaWidth = (self.selectArea.secondPoint.col - self.selectArea.firstPoint.col + offsetCol) * cellWidth
            areaHeight = (self.selectArea.secondPoint.row - self.selectArea.firstPoint.row + offsetRow) * cellHeight

            paintingRect = QRect(x, y, areaWidth, areaHeight)
            painter.setPen(QPen(Qt.GlobalColor.red, 2, Qt.PenStyle.SolidLine, Qt.PenCapStyle.FlatCap, Qt.PenJoinStyle.MiterJoin))
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