from forms.implemented_widgets.ChangeGridSizeDialog import ChangeGridSSizeDialog
from PyQt5.QtCore import QSize
from PyQt5 import QtCore

class CreateGridDialog(ChangeGridSSizeDialog):
    """
    Диалоговое окно для создания новой сетки разметки.
    Позволяет пользователю задать размер ячеек и применить изменения ко всем изображениям.
    """

    def __init__(self, gridSize: QSize, parent=None):
        """
        Инициализирует диалоговое окно создания сетки.

        :param gridSize: Размер всей сетки.
        :param parent: Родительский объект.
        """
        super().__init__(gridSize, parent)
        _translate = QtCore.QCoreApplication.translate

        # Устанавливаем заголовок окна
        self.setWindowTitle(_translate("CreateGridDialog", "Создать сетку для изображения"))

        # Настраиваем текст чекбокса для применения ко всем изображениям
        self.checkBoxApplyToAll.setText(_translate("CreateGridDialog", "Применить ко всем изображениям"))
