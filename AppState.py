from Core.Grid.Class import Class
from Core.Grid.ClassGrid import ClassGrid
from enum import Enum
from PyQt5.QtCore import QObject, pyqtSignal
from PyQt5.QtGui import QPixmap
from Core.Folder import Folder
from typing import Optional


class Tool(Enum):
    NO_TOOL = 1
    ASSIGN_TOOL = 2
    DELETE_TOOL = 3
    SELECT_AREA_TOOL = 4
    
    
# class Image:
#     def __init__(self, image, filename):
#         self.image = image
#         self.filename = filename

class AppEvents(QObject):
    beforeGridSetEvent = pyqtSignal()
    afterGridSetEvent = pyqtSignal()
    onImageSetEvent = pyqtSignal()
    beforeToolChangeEvent = pyqtSignal()
    
    beforeFolderSetEvent = pyqtSignal()
    afterFolderSetEvent = pyqtSignal()


    
class AppState:
    def __init__(self):
        self.events = AppEvents()
        self.activeClass : Class = None
        self.activeTool : Tool = Tool.NO_TOOL
        self.activeGrid : ClassGrid = None
        self.activeImage : QPixmap = None
        self.activeFolder : Folder = None
        
    def setActiveGrid(self, grid : ClassGrid):
        if self.activeGrid != None:
            self.events.beforeGridSetEvent.emit()
        self.activeGrid = grid
        if self.activeGrid != None:
            self.setActiveClass(self.activeGrid.classes[0])
        self.events.afterGridSetEvent.emit()
        
    def setActiveImage(self, image: QPixmap):
        self.activeImage = image
        self.events.onImageSetEvent.emit()
        
    def setActiveImageAndGrid(self, image : QPixmap, grid : Optional[ClassGrid]):
        self.setActiveImage(image)
        self.setActiveGrid(grid)

         
        
    def setActiveTool(self, tool : Tool):
        if self.activeTool == Tool.SELECT_AREA_TOOL:
            self.events.beforeToolChangeEvent.emit()
        self.activeTool = tool
        
    def setActiveClass(self, _class):
        self.activeClass = _class
        
    def setActiveFolder(self, folder):
        if self.activeFolder != None:
            self.events.beforeFolderSetEvent.emit()
        self.activeFolder = folder
        self.events.afterFolderSetEvent.emit()