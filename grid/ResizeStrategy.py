from abc import ABC, abstractmethod

class ResizeStrategy(ABC):
    def __init__(self, oldCellSize, newCellSize, imageSize):
        self.oldCellSize = oldCellSize
        self.newCellSize =  newCellSize
        self.imageSize = imageSize
        
    @abstractmethod
    def resize(self, table):
        pass