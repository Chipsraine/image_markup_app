from grid.Class import Class
from PyQt5.QtGui import QColor

class ClassJson:
    @staticmethod
    def fromJson(jsonObject):
        return Class(jsonObject["name"], QColor(jsonObject["color"]))
    
    @staticmethod
    def fromJsonArray(jsonObject):
        classes : dict[str, Class] = {}
        for _class in jsonObject:
            _class = ClassJson.fromJson(_class)
            classes[_class._name] = _class
        return classes
    
    @staticmethod
    def toJson(_class: Class):
        return { "name" : _class._name, "color": _class._color.name()}
    
    @staticmethod
    def toJsonArray(classes : dict[str, Class]):
        jsonList :list[dict]= []
        for entry in classes.values():
            jsonList.append(ClassJson.toJson(entry))
        return jsonList
    
    