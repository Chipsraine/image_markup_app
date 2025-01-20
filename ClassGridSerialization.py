from Core.Grid.Class import Class
from Core.Grid.ClassGridTable import ClassGridTable
from Core.Grid.ClassGrid import ClassGrid
from io import TextIOWrapper
from PyQt5.QtGui import QColor
from PyQt5.QtCore import QSize

class ClassGridDeserializer:
    @staticmethod
    def fromTxt(file :TextIOWrapper, imageSize :QSize):        
        cellSize = QSize(*map(int, file.readline().split()))
        classes : list[Class] = []
                
        for item in file.readline().strip().split(';'):
            class_name, color = item.strip().split("~")
            classes.append(Class(class_name, QColor(color)))


        table = ClassGridTable(imageSize.height() // cellSize.height(), imageSize.width() // cellSize.width())
        for row in range(table.rows):
            cells = list(map(int, file.readline().split()))
            for col in range(table.cols):
                classIndex = cells[col]
                if classIndex != 0:
                    table.setClassToCell(row, col, classes[classIndex - 1])

        return ClassGrid(table, classes, cellSize, imageSize)
    
    


class ClassGridSerializer:
    @staticmethod
    def toTxt(file : TextIOWrapper, grid: ClassGrid):
        file.write(f"{grid.cellSize.width()} {grid.cellSize.height()}\n")
        classes = []
        for _class in grid.classes:
            classes.append(f'{_class._name}~{_class._color.name()}')
        file.write(f"{';'.join(classes)}\n")
        
        for row in range(grid.table.rows):
            cells = [0 for _ in range(grid.table.cols)]           
            for col in range(grid.table.cols):
                _class = grid.table.getCellClass(row, col)
                if (_class != None):
                    cells[col] = grid.classes.index(_class) + 1
            file.write(f"{' '.join(list(map(str, cells)))}\n")