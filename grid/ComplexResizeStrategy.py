from grid.ResizeStrategy import ResizeStrategy

class ComplexResizeStrategy(ResizeStrategy):
    def __init__(self, oldCellSize, newCellSize, imageSize):
        super().__init__(oldCellSize, newCellSize, imageSize)
    
    def resize(self, table):
        pass