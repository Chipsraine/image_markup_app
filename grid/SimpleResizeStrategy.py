from grid.ResizeStrategy import ResizeStrategy
from grid.ClassGridTable import ClassGridTable

class SimpleResizeStrategy(ResizeStrategy):
    def __init__(self, oldCellSize, newCellSize, imageSize):
        super().__init__(oldCellSize, newCellSize, imageSize)
    
    def resize(self, table: ClassGridTable):
        rows = self.imageSize["height"] // self.newCellSize
        cols = self.imageSize["width"] // self.newCellSize
        
        newData = [[None] * cols] * rows
        
        for row in range(min(table.rows, rows)):
            for col in range(min(table.cols, cols)):
                newData[row][col] = table.data[row][col]
        
        table.data = newData
        table.rows = rows
        table.cols = cols