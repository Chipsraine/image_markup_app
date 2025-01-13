from grid.Class import Class
from grid.ClassGrid import ClassGrid
from enum import Enum
from PyQt5.QtCore import QObject, pyqtSignal
from PyQt5.QtGui import QPixmap

class Tool(Enum):
    NO_TOOL = 1
    ASSIGN_TOOL = 2
    DELETE_TOOL = 3
    AREA_TOOL = 4
    
    
# class Image:
#     def __init__(self, image, filename):
#         self.image = image
#         self.filename = filename

class AppEvents(QObject):
    beforeGridSetEvent = pyqtSignal()
    afterGridSetEvent = pyqtSignal()
    onImageSetEvent = pyqtSignal()


    
class AppState:
    def __init__(self):
        self.events = AppEvents()
        self.activeClass : Class = None
        self.activeTool : Tool = Tool.NO_TOOL
        self.activeGrid : ClassGrid = None
        self.activeImage : QPixmap = None
        
    def setActiveGrid(self, grid : ClassGrid):
        if self.activeGrid != None:
            self.events.beforeGridSetEvent.emit()
        self.activeGrid = grid
        self.activeClass = None
        self.events.afterGridSetEvent.emit()
        
    def setActiveImage(self, image: QPixmap):
        self.activeImage = image
        self.events.onImageSetEvent.emit()
        
    def setActiveImageAndGrid(self, image : QPixmap, grid : ClassGrid):
        self.activeImage = image
        self.events.onImageSetEvent.emit()
        self.setActiveGrid(grid)