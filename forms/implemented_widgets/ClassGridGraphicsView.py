
from PyQt5.QtWidgets import QGraphicsScene, QGraphicsPixmapItem
from PyQt5.QtGui import QPixmap

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
        self.set_image(None)
        
    def get_coordinates(self, event):
        print(event.pos())
        
    def set_image(self, image=None):
        image = QPixmap(r"C:\\Users\\WormixGame\\Downloads\\photo_2024-12-31_18-52-09.jpg")
        self.source_image_item.setPixmap(image)
        self.source_image_item.mousePressEvent = self.get_coordinates
        
    def set_grid(self, grid):
        print("жопа")
