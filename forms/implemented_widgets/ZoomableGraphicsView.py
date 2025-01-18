
from PyQt5.QtWidgets import QGraphicsView

class ZoomableGraphicsView(QGraphicsView):
    def __init__(self, parent=None):
        super().__init__(parent)
        
    def zoomIn(self):
        self.scale(1.25, 1.25)

    def zoomOut(self):
        self.scale(0.8, 0.8)

    def resetScale(self, ratioX, ratioY):
        self.resetTransform()
        ratio = min(ratioX, ratioY)
        self.scale(ratio, ratio)
        
        