
from PyQt5.QtWidgets import QGraphicsView, QGraphicsScene, QGraphicsPixmapItem
from PyQt5.QtGui import QPixmap

class ZoomableGraphicsView(QGraphicsView):
    def __init__(self, parent=None):
        super().__init__(parent)
        
    def zoomIn(self):
        self.scale(1.25, 1.25)
        self.centerOn(self.sceneRect().center())

    def zoomOut(self):
        self.scale(0.8, 0.8)
        self.centerOn(self.sceneRect().center())

    def resetScale(self):
        self.resetTransform()
        self.centerOn(self.sceneRect().center())