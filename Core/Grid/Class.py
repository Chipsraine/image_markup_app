from PyQt5.QtGui import QColor
from PyQt5.QtCore import pyqtSignal, QObject

class Class(QObject):
    """
    Класс, представляющий категорию разметки.
    Позволяет задавать имя и цвет, а также генерировать сигналы при их изменении.
    """

    colorChanged = pyqtSignal(QColor)  # Сигнал при изменении цвета класса
    nameChanged = pyqtSignal(str)  # Сигнал при изменении имени класса

    def __init__(self, name: str, color: QColor):
        """
        Инициализирует объект класса с заданным именем и цветом.

        :param name: Название класса.
        :param color: Цвет класса.
        """
        super().__init__(None)
        self._name: str = name
        self._color: QColor = color

    @staticmethod
    def default():
        """
        Создает и возвращает объект класса с настройками по умолчанию.

        :return: Экземпляр класса с предустановленным именем и цветом.
        """
        return Class("Default class", QColor("#999999"))

    def color(self) -> QColor:
        """
        Возвращает цвет класса.

        :return: QColor объекта.
        """
        return self._color

    def name(self) -> str:
        """
        Возвращает имя класса.

        :return: Название класса.
        """
        return self._name

    def setColor(self, color: QColor):
        """
        Устанавливает новый цвет класса и вызывает соответствующий сигнал.

        :param color: Новый цвет.
        """
        self._color = color
        self.colorChanged.emit(color)

    def setName(self, name: str):
        """
        Устанавливает новое имя класса и вызывает соответствующий сигнал.

        :param name: Новое имя.
        """
        self._name = name
        self.nameChanged.emit(name)
