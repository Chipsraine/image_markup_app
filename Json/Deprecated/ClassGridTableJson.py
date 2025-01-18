from grid.ClassGridTable import ClassGridTable
from PyQt5.QtCore import QSize

class ClassGridTableJson:
    @staticmethod
    def fromJson(jsonObject, classes, cellSize :QSize, imageSize :QSize):
        rows = imageSize.height() // cellSize.height()
        cols = imageSize.width() // cellSize.width()
        table : ClassGridTable = ClassGridTable(rows, cols)
        for entry in jsonObject["data"]:
            row = entry["row"]
            col = entry["col"]
            cellClass = classes[entry["class"]]
            try:
                table.setClassToCell(row, col, cellClass)
            except IndexError:
                print(f"Ячейка [{row}, {col}] выходит за пределы сетки")
        return table
    
    @staticmethod
    def toJson(table : ClassGridTable):
        jsonObject = {}
        data = []
        for row in range(table.rows):
            for col in range(table.cols):

                _class = table.getCellClass(row, col)
                if _class != None:
                    data.append({"row": row, "col": col, "class": _class._name})
        jsonObject["data"] = data
        
        return jsonObject