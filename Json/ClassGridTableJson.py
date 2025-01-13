from grid.ClassGridTable import ClassGridTable

class ClassGridTableJson:
    @staticmethod
    def fromJson(jsonObject, classes, cellSize, imageSize):
        rows = imageSize["height"] // cellSize["height"]
        cols = imageSize["width"] // cellSize["width"]
        table : ClassGridTable = ClassGridTable(rows, cols)
        for entry in jsonObject["data"]:
            row = entry["row"]
            col = entry["col"]
            cellClass = classes[entry["class"]]
            table.setClassToCell(row, col, cellClass)
        return table
    
    @staticmethod
    def toJson(table : ClassGridTable):
        jsonObject = {}
        data = []
        for row in range(table.rows):
            for col in range(table.cols):
                className = table.getCellClass(row, col)._name
                data.append({"row": row, "col": col, "class": className})
        jsonObject["data"] = data
        
        return jsonObject