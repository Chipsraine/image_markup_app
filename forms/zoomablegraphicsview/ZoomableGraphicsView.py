
from PyQt5.QtWidgets import QGraphicsView, QGraphicsScene, QGraphicsPixmapItem
from PyQt5.QtGui import QPixmap

class ZoomableGraphicsView(QGraphicsView):
    def __init__(self, parent=None):
        super().__init__(parent)
        self._zoom = 1
        self._empty = True
        self.setScene(QGraphicsScene())
        self.scene().addItem(QGraphicsPixmapItem(QPixmap(r"C:\\Users\\WormixGame\\Downloads\\photo_2024-12-31_18-52-09.jpg")))


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