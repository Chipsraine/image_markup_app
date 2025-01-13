from grid.ClassGridTable import ClassGridTable

class ClassGridTableJson:
    @staticmethod
    def fromJson(jsonObject, classes):
        table : ClassGridTable = ClassGridTable(jsonObject["rows"], jsonObject["cols"])
        for entry in jsonObject["data"]:
            row = entry["row"]
            col = entry["col"]
            cellClass = classes[entry["class"]]
            table.setClassToCell(row, col, cellClass)
        return table
    
    @staticmethod
    def toJson(table : ClassGridTable):
        jsonObject = {}
        jsonObject["rows"] = table.rows
        jsonObject["cols"] = table.cols
        data = []
        for row in range(table.rows):
            for col in range(table.cols):
                className = table.getCellClass(row, col)._name
                data.append({"row": row, "col": col, "class": className})
        jsonObject["data"] = data
        
        return jsonObject