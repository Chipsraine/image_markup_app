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
        # startRow = min(point.row, self.firstPoint.row)
        # endRow = max(point.row, self.firstPoint.row)
        # startCol = min(point.col, self.firstPoint.col)
        # endCol = max(point.col, self.firstPoint.col)
        
        # self.firstPoint = Point(startRow, startCol)
        # self.secondPoint = Point(endRow, endCol)