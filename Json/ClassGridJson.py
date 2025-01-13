from grid.ClassGrid import ClassGrid
from Json.ClassGridTableJson import ClassGridTableJson
from Json.ClassJson import ClassJson


class ClassGridJson:
    @staticmethod
    def fromJson(jsonObject): 
        classes = ClassJson.fromJsonArray(jsonObject["classes"])
        table = ClassGridTableJson.fromJson(jsonObject["table"], classes)
        cellSize = jsonObject["cell_size"]
        gridSize = jsonObject["grid_size"]
        return ClassGrid(table, classes, cellSize, gridSize)
    
    @staticmethod
    def toJson(grid : ClassGrid):
        jsonObject = {}
        jsonObject["cell_size"] = grid.cellSize
        jsonObject["grid_size"] = grid.imageSize
        jsonObject["classes"] = ClassJson.toJsonArray(grid.classes)
        jsonObject["table"] = ClassGridTableJson.toJson(grid.table)
        return jsonObject
        