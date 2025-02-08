class Point:
    """
    Класс для представления точки в двумерной системе координат (строка, колонка).
    Используется для обозначения позиций в сетке.
    """

    def __init__(self, row: int, col: int):
        """
        Инициализирует точку с заданными координатами.

        :param row: Номер строки.
        :param col: Номер колонки.
        """
        self.row = row
        self.col = col

    def __eq__(self, value):
        """
        Определяет сравнение двух точек по их координатам.

        :param value: Другая точка для сравнения.
        :return: True, если точки равны, иначе False.
        """
        if value is None:
            return False
        return self.row == value.row and self.col == value.col
