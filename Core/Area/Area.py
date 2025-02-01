from Core.Area import Point

class Area:
    def __init__(self):
        self.firstPoint : Point = None
        self.secondPoint : Point = None
        
    def setFirstPoint(self, point):
        self.secondPoint = None
        self.firstPoint = point
    
    def setSecondPoint(self, point : Point):
        self.secondPoint = point
