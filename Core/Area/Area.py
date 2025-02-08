from Core.Area import Point


class Area:
    """
    Класс для представления области, определяемой двумя точками.
    Используется для выделения прямоугольной области в сетке.
    """

    def __init__(self):
        """
        Инициализирует область с двумя точками, которые изначально пусты.
        """
        self.firstPoint: Point = None
        self.secondPoint: Point = None

    def setFirstPoint(self, point: Point):
        """
        Устанавливает первую точку области. При этом вторая точка сбрасывается.

        :param point: Координаты первой точки.
        """
        self.secondPoint = None
        self.firstPoint = point

    def setSecondPoint(self, point: Point):
        """
        Устанавливает вторую точку области.

        :param point: Координаты второй точки.
        """
        self.secondPoint = point
