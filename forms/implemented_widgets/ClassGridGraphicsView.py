
from PyQt5.QtWidgets import QGraphicsScene, QGraphicsPixmapItem
from PyQt5.QtGui import QPixmap, QImage, QPainter, QColor, QPen, QBrush
from PyQt5.QtCore import Qt, QRect

import numpy as np

from grid.Class import Class
from grid.ClassGrid import ClassGrid
from forms.implemented_widgets.ZoomableGraphicsView import ZoomableGraphicsView

class ClassGridGraphicsView(ZoomableGraphicsView):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setScene(QGraphicsScene())
        self.source_image_item = QGraphicsPixmapItem()
        self.mask_image_item = QGraphicsPixmapItem()
        self.tool_image_item = QGraphicsPixmapItem()
        self.scene().addItem(self.source_image_item)
        self.scene().addItem(self.mask_image_item)
        self.scene().addItem(self.tool_image_item)
        self.grid : ClassGrid = ClassGrid()
        self.activeClass : Class = None
        
    def setAllEmptyCellsToActiveClass(self):
        size = self.source_image_item.pixmap().size()
        rows = size.height() // self.grid.cellSize
        cols = size.width() // self.grid.cellSize
        self.grid.fillEmptyCellsWithClass(rows, cols, self.activeClass)
        
    def setClassToCell(self, event):
        x = int(event.pos().x())
        y = int(event.pos().y())
        
        row = y // self.grid.cellSize
        col = x // self.grid.cellSize
        
        self.grid.setClassToCell(row, col, self.activeClass)
        
    def updateViewCell(self, row, col):
        painter = QPainter()
        
        painter.begin(self.mask_image)
        cellClass = self.grid.getCellClass(row, col)
        
        
        self.eraseCell(painter, row, col)
        
        if cellClass != None:
           self.paintCell(painter, row, col, cellClass._color)
        
        painter.end()
        
        self.mask_image_item.setPixmap(self.mask_image)
        
    def setImage(self, image):
        self.source_image_item.setPixmap(image)
        self.source_image_item.mousePressEvent = self.setClassToCell
        
    def setGrid(self, grid):
        self.grid = grid
        self.grid.signals_emitter.updateCell.connect(self.updateViewCell)
        self.grid.signals_emitter.updateAllCells.connect(self.paintGrid)
        
        self.grid.signals_emitter.updateAllCells.emit()

    
    def setBlankGrid(self):
        img_height, img_width = int(self.source_image_item.boundingRect().height()), int(self.source_image_item.boundingRect().width())
        n_channels = 4
        transparent_img = np.zeros((img_height, img_width, n_channels), dtype=np.uint8)
        self.mask_image = QPixmap(QImage(transparent_img.data, img_width, img_height, 4 * img_width, QImage.Format.Format_RGBA8888))
        self.mask_image_item.setPixmap(self.mask_image)
        
    def paintCell(self, painter : QPainter, row, col, color:QColor):
        transparent_color = QColor(color)
        transparent_color.setAlpha(128)
                    
        pen = QPen(color, 1)
        brush = QBrush(transparent_color)
                    
        painter.setPen(pen)
        painter.setBrush(brush)
                    
        width = self.grid.cellSize
        height = self.grid.cellSize
                                        
        rect = QRect(col * width, row * height, width, height)
        painter.drawRect(rect)

    def eraseCell(self, painter :QPainter, row, col):
        color = QColor(0,0,0,0)
        pen = QPen(color, 1)
        brush = QBrush(color)
                    
        painter.setPen(pen)
        painter.setBrush(brush)
                    
        width = self.grid.cellSize
        height = self.grid.cellSize
                                        
        rect = QRect(col * width, row * height, width, height)
        
        mode = painter.compositionMode()
        painter.setCompositionMode(QPainter.CompositionMode.CompositionMode_Clear)
        painter.drawRect(rect)
        painter.setCompositionMode(mode)
            
    def paintGrid(self):
        
        self.setBlankGrid()
        
        painter = QPainter()
        
        painter.begin(self.mask_image)

        for row, row_data in self.grid.table.items():
            for col, class_data in row_data.items():
                if class_data != None:
                    self.paintCell(painter, col, row, class_data._color)
                    
        painter.end()
                
        self.mask_image_item.setPixmap(self.mask_image)
