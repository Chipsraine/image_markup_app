from PyQt5.QtGui import QColor

class Class:
    def __init__(self, name : str, color : QColor):
        self._name : str = name
        self._color : QColor = color
    
    @staticmethod
    def fromJson(dict):
        return Class(dict["name"], QColor(dict["color"]))
    
    @staticmethod
    def dictFromJson(dict):
        classes = {}
        for _class in dict:
            _class = Class.fromJson(_class)
            classes[_class._name] = _class
        return classes