import sys
from PyQt5.QtWidgets import QApplication, QMainWindow, QGraphicsView, QGraphicsScene, QGraphicsPixmapItem, QShortcut
from PyQt5.QtGui import QPixmap,QKeySequence, QImage, QPainter, QBrush, QColor
from PyQt5.QtCore import Qt, QPointF
import cv2
import numpy as np


class ZoomableGraphicsView(QGraphicsView):
    def __init__(self, parent=None):
        super().__init__(parent)
        self._zoom = 1
        self._empty = True

    def zoomIn(self):
        self._zoom *= 1.25
        self.scale(1.25, 1.25)
        self.centerOn(self.sceneRect().center())

    def zoomOut(self):
        self._zoom *= 0.8
        self.scale(0.8, 0.8)
        self.centerOn(self.sceneRect().center())

    def resetTransform(self):
        super().resetTransform()
        self._zoom = 1

class ImageViewer(QMainWindow):
    def __init__(self):
        super().__init__()
        
        self.scene = QGraphicsScene()
        self.view = ZoomableGraphicsView(self.scene)
        self.setCentralWidget(self.view)
        
        self.source_image_item = QGraphicsPixmapItem()
        self.mask_image_item = QGraphicsPixmapItem()
        self.tool_image_item = QGraphicsPixmapItem()
        
        self.scene.addItem(self.source_image_item)
        self.scene.addItem(self.mask_image_item)
        self.scene.addItem(self.tool_image_item) 
        
        self.init_source_layer()
        self.init_mask_layer()

        self.zoom_in_shortcut = QShortcut(QKeySequence("Ctrl++"), self)
        self.zoom_out_shortcut = QShortcut(QKeySequence("Ctrl+-"), self)
        
        self.zoom_in_shortcut.activated.connect(self.view.zoomIn)
        self.zoom_out_shortcut.activated.connect(self.view.zoomOut)

    def init_source_layer(self):
        self.image_path = r"C:\\Users\\WormixGame\\Downloads\\photo_2024-12-31_18-52-09.jpg"
        self.source_image_item.setPixmap(QPixmap(self.image_path))
        self.source_image_item.mousePressEvent = self.simple
        self.view.setSceneRect(0, 0, self.source_image_item.boundingRect().width(), self.source_image_item.boundingRect().height())

    def init_mask_layer(self):
        img_height, img_width = int(self.source_image_item.boundingRect().height()), int(self.source_image_item.boundingRect().width())
        n_channels = 4
        transparent_img = np.zeros((img_height, img_width, n_channels), dtype=np.uint8)
        self.mask_image = QPixmap(QImage(transparent_img.data, img_width, img_height, 4 * img_width, QImage.Format.Format_RGBA8888))
        self.mask_image_item.setPixmap(self.mask_image)
        
    
    def simple(self, event):
        painter = QPainter()
        
        painter.begin(self.mask_image)
        painter.fillRect(int(event.pos().x()) // 14 * 14, int(event.pos().y()) // 14 * 14, 14, 14, Qt.GlobalColor.black)
        painter.end()
        
        self.mask_image_item.setPixmap(self.mask_image)
        
        
if __name__ == "__main__":
    app = QApplication(sys.argv)
    viewer = ImageViewer()
    viewer.show()
    sys.exit(app.exec_())