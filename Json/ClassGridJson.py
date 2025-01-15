from grid.ClassGrid import ClassGrid
from Json.ClassGridTableJson import ClassGridTableJson
from Json.ClassJson import ClassJson


class ClassGridJson:
    @staticmethod
    def fromJson(jsonObject, imageSize): 
        classes = ClassJson.fromJsonArray(jsonObject["classes"])
        cellSize = jsonObject["cell_size"]
        table = ClassGridTableJson.fromJson(jsonObject["table"], classes, cellSize, imageSize)

        return ClassGrid(table, classes, cellSize, imageSize)
    
    @staticmethod
    def toJson(grid : ClassGrid):
        jsonObject = {}
        jsonObject["cell_size"] = grid.cellSize
        jsonObject["classes"] = ClassJson.toJsonArray(grid.classes)
        jsonObject["table"] = ClassGridTableJson.toJson(grid.table)
        return jsonObject
        