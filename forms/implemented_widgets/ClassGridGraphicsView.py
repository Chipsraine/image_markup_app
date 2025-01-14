
from PyQt5.QtWidgets import QGraphicsScene, QGraphicsPixmapItem
from PyQt5.QtGui import QPixmap, QImage, QPainter, QColor, QPen, QBrush
from PyQt5.QtCore import Qt, QRect

import numpy as np
from grid.area.Area import Area
from grid.area.Point import Point
from forms.implemented_widgets.ZoomableGraphicsView import ZoomableGraphicsView
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
        
        self.mousePressed = False
        self.lastTouchedPoint = None
    
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
        
        col = x // self.appState.activeGrid.cellSize["width"]
        row = y // self.appState.activeGrid.cellSize["height"]
        
        return Point(row, col)
        

    def mousePressOnGrid(self, event):
        eventPoint = self.getEventPoint(event)      
        self.lastTouchedPoint = eventPoint
        
        if self.isInteractable() and self.appState.activeGrid.table.isCellInsideGrid(eventPoint.row, eventPoint.col):
            self.selectArea.setFirstPoint(eventPoint)
            self.selectArea.setSecondPoint(eventPoint)
            self.manageMouseTool(eventPoint)
            
        self.mousePressed = True
            
    def mouseMoveOnGrid(self, event):
        if self.mousePressed == False or not self.isGridSet():
            return
        
        eventPoint = self.getEventPoint(event)
        
        if self.lastTouchedPoint == eventPoint or not self.appState.activeGrid.table.isCellInsideGrid(eventPoint.row, eventPoint.col):
            return
        
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
        
    def paintCell(self, painter : QPainter, row, col, color:QColor):
        transparent_color = QColor(color)
        transparent_color.setAlpha(128)            
        pen = QPen(color, 1)
        
        brush = QBrush(transparent_color)
                    
        painter.setPen(pen)
        painter.setBrush(brush)
                    
        width = self.appState.activeGrid.cellSize["width"]
        height = self.appState.activeGrid.cellSize["height"]
                                        
        rect = QRect(col * width, row * height, width, height)
        painter.drawRect(rect)
        

    def eraseCell(self, painter :QPainter, row, col):
        color = QColor(0,0,0,0)
        pen = QPen(color, 1)
        brush = QBrush(color)
                    
        painter.setPen(pen)
        painter.setBrush(brush)
                    
        width = self.appState.activeGrid.cellSize["width"]
        height = self.appState.activeGrid.cellSize["height"]
                                        
        rect = QRect(col * width, row * height, width, height)
        
        mode = painter.compositionMode()
        painter.setCompositionMode(QPainter.CompositionMode.CompositionMode_Clear)
        painter.drawRect(rect)
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
            cellWidth, cellHeight = self.appState.activeGrid.cellSize["width"], self.appState.activeGrid.cellSize["height"]
            x, y = self.selectArea.firstPoint.col * cellWidth, self.selectArea.firstPoint.row * cellHeight
            offsetCol = 1 if self.selectArea.secondPoint.col >= self.selectArea.firstPoint.col else 0
            offsetRow = 1 if self.selectArea.secondPoint.row >= self.selectArea.firstPoint.row else 0
            areaWidth = (self.selectArea.secondPoint.col - self.selectArea.firstPoint.col + offsetCol) * cellWidth
            areaHeight = (self.selectArea.secondPoint.row - self.selectArea.firstPoint.row + offsetRow) * cellWidth

            paintingRect = QRect(x, y, areaWidth, areaHeight)
            pen = QPen(Qt.GlobalColor.red, 2)
            painter.setPen(pen)
            painter.setBackground(QColor(0, 0, 0, 0))
            
            painter.drawRect(paintingRect)
            
        painter.end()
        self.tool_image_item.setPixmap(self.tool_image)
        
    def fillSelectedArea(self):
        if not self.isGridSet():
            return
        
        if self.selectArea.firstPoint != None and self.selectArea.secondPoint != None:
            self.appState.activeGrid.setClassToArea(self.selectArea, self.appState.activeClass)