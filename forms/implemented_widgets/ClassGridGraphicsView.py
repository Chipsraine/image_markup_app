
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
        
        self.source_image_item.mousePressEvent = self.touchGrid
        
        self.appSettings : AppState = None
        self.areaRect : Area = Area()
    
    def isGridSet(self):
        return self.appSettings.activeGrid != None and self.appSettings.activeImage != None
    
    def isInteractable(self):
        return self.appSettings.activeClass != None and self.isGridSet()
    
    def setAppSettings(self, settings : AppState):
        self.appSettings = settings
        
    def setAllEmptyCellsToActiveClass(self):
        if self.isInteractable():
            self.appSettings.activeGrid.fillEmptyCellsWithClass(self.appSettings.activeClass)
    
    def selectArea(self, row, col):
        touchPoint = Point(row, col)
        
        if self.areaRect.firstPoint != None and self.areaRect.secondPoint != None:
            self.areaRect.firstPoint = None
            self.areaRect.secondPoint = None
        elif self.areaRect.firstPoint == None:
            self.areaRect.setFirstPoint(touchPoint)
        elif self.areaRect.secondPoint == None:
            self.areaRect.setSecondPoint(touchPoint)
            
            
        self.paintToolArea()

    def touchGrid(self, event):
        if not self.isInteractable() or self.appSettings.activeTool == Tool.NO_TOOL:
            return
        
        activeGrid = self.appSettings.activeGrid
        activeTool = self.appSettings.activeTool

        x = int(event.pos().x())
        y = int(event.pos().y())
        
        row = y // activeGrid.cellSize["height"]
        col = x // activeGrid.cellSize["width"]
        
        if not activeGrid.table.isCellInsideGrid(row, col):
            return
        
        if activeTool == Tool.AREA_TOOL:
            self.selectArea(row, col)
            return
        
        activeClass = self.appSettings.activeClass
        
        if activeClass == None:
            return
        
        if activeTool == Tool.DELETE_TOOL:
            activeGrid.setClassToCell(row, col, None)
        elif activeTool == Tool.ASSIGN_TOOL:
            activeGrid.setClassToCell(row, col, activeClass)
            
        
    def updateCellHandler(self, row, col):
        painter = QPainter()
        painter.begin(self.mask_image)
        
        cellClass = self.appSettings.activeGrid.getCellClass(row, col)
        
        
        self.eraseCell(painter, row, col)
        
        if cellClass != None:
           self.paintCell(painter, row, col, cellClass._color)
        
        painter.end()
        
        self.mask_image_item.setPixmap(self.mask_image)
        
    def setImage(self):
        self.sourceHeight = self.appSettings.activeImage.size().height()
        self.sourceWidth = self.appSettings.activeImage.size().width()
        self.source_image_item.setPixmap(self.appSettings.activeImage)

    def unlinkGrid(self):
        self.appSettings.activeGrid.signals_emitter.updateCell.disconnect(self.updateCellHandler)
        self.appSettings.activeGrid.signals_emitter.updateAllCells.disconnect(self.paintGrid)
        
    def linkGrid(self):
        self.appSettings.activeGrid.signals_emitter.updateCell.connect(self.updateCellHandler)
        self.appSettings.activeGrid.signals_emitter.updateAllCells.connect(self.paintGrid)
        self.paintGrid()

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
                    
        width = self.appSettings.activeGrid.cellSize["width"]
        height = self.appSettings.activeGrid.cellSize["height"]
                                        
        rect = QRect(col * width, row * height, width, height)
        painter.drawRect(rect)
        

    def eraseCell(self, painter :QPainter, row, col):
        color = QColor(0,0,0,0)
        pen = QPen(color, 1)
        brush = QBrush(color)
                    
        painter.setPen(pen)
        painter.setBrush(brush)
                    
        width = self.appSettings.activeGrid.cellSize["width"]
        height = self.appSettings.activeGrid.cellSize["height"]
                                        
        rect = QRect(col * width, row * height, width, height)
        
        mode = painter.compositionMode()
        painter.setCompositionMode(QPainter.CompositionMode.CompositionMode_Clear)
        painter.drawRect(rect)
        painter.setCompositionMode(mode)
            
    def paintGrid(self):
        
        self.resetMask()
        
        painter = QPainter()
        
        painter.begin(self.mask_image)

        activeGrid = self.appSettings.activeGrid

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
        
        if self.areaRect.firstPoint != None:
            cellWidth, cellHeight = self.appSettings.activeGrid.cellSize["width"], self.appSettings.activeGrid.cellSize["height"]
            x, y = self.areaRect.firstPoint.col * cellWidth, self.areaRect.firstPoint.row * cellHeight
            if self.areaRect.secondPoint != None:
                areaWidth, areaHeight = (self.areaRect.secondPoint.col - self.areaRect.firstPoint.col + 1) * cellWidth, (self.areaRect.secondPoint.row - self.areaRect.firstPoint.row + 1) * cellWidth
            else:
                areaWidth, areaHeight = cellWidth, cellWidth

            
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
        
        if self.areaRect.firstPoint != None and self.areaRect.secondPoint != None:
            self.appSettings.activeGrid.setClassToArea(self.areaRect, self.appSettings.activeClass)