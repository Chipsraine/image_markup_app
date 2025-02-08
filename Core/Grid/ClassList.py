from PyQt5.QtCore import QObject, pyqtSignal
from Core.Grid.Class import Class

class ClassList(QObject):
    """
    Класс для управления списком разметочных классов.
    Позволяет добавлять, удалять классы и уведомлять об изменениях через сигналы.
    """

    classAdded = pyqtSignal(Class)  # Сигнал, вызываемый при добавлении нового класса
    classRemoved = pyqtSignal(Class)  # Сигнал, вызываемый при удалении класса
    classChanged = pyqtSignal()  # Сигнал, уведомляющий об изменении списка классов

    def __init__(self):
        """
        Инициализирует список классов.
        """
        super().__init__(None)
        self.classes: list[Class] = []

    def addClassToList(self, _class: Class):
        """
        Добавляет новый класс в список и вызывает соответствующий сигнал.

        :param _class: Класс, который нужно добавить.
        """
        self.classes.append(_class)
        self.classAdded.emit(_class)

    def removeClassFromList(self, _class: Class):
        """
        Удаляет класс из списка и вызывает соответствующий сигнал.

        :param _class: Класс, который нужно удалить.
        """
        if _class in self.classes:
            self.classes.remove(_class)
            self.classRemoved.emit(_class)

    def onClassChange(self):
        """
        Вызывает сигнал об изменении списка классов.
        """
        self.classChanged.emit()
