from forms.change_grid_size_dialog import Ui_ChangeGridCellSizeDialog
from PyQt5.QtWidgets import QDialog, QMessageBox
from PyQt5.QtCore import QSize
from PyQt5.QtGui import QIntValidator


class ChangeGridSSizeDialog(QDialog, Ui_ChangeGridCellSizeDialog):
    """
    Диалоговое окно для изменения размера ячеек сетки.
    Позволяет пользователю задать новый размер и применить его ко всем изображениям или только к текущему.
    """

    def __init__(self, gridSize: QSize, parent=None):
        """
        Инициализирует диалоговое окно изменения размера ячеек.

        :param gridSize: Размер всей сетки.
        :param parent: Родительский объект.
        """
        QDialog.__init__(self, parent)
        self.setupUi(self)
        self.gridSize = gridSize
        self.gridCellSize: QSize = None  # Новый размер ячеек, устанавливается при подтверждении
        self.applyToAllGrids: bool = False  # Флаг применения ко всем разметкам

        # Устанавливаем валидатор для ввода только положительных целых чисел
        validator = QIntValidator(self)
        validator.setBottom(1)

        self.inputHeight.setValidator(validator)
        self.inputWidth.setValidator(validator)

        # Отображаем текущий размер сетки
        self.labelGridSize.setText(f"{self.gridSize.width()}x{self.gridSize.height()}")
        self.checkBoxApplyToAll.setCheckState(False)

        # Подключаем кнопки к соответствующим обработчикам
        self.pushButtonCancel.clicked.connect(self.close)
        self.pushButtonOk.clicked.connect(self.processApply)

    def showWarning(self, title, text):
        """
        Показывает всплывающее окно с предупреждением.

        :param title: Заголовок окна.
        :param text: Сообщение предупреждения.
        """
        messageBox = QMessageBox(QMessageBox.Icon.Warning, title, text)
        messageBox.exec_()

    def processApply(self):
        """
        Обрабатывает нажатие кнопки "ОК". Проверяет корректность введенных данных и применяет изменения.
        """
        self.applyToAllGrids = self.checkBoxApplyToAll.isChecked()

        # Проверка на корректный ввод данных
        if not self.inputWidth.hasAcceptableInput() or not self.inputHeight.hasAcceptableInput():
            self.showWarning("Некорректные значения", "Размер ячейки должен быть целым числом больше 0!")
            return

        width = int(self.inputWidth.text())
        height = int(self.inputHeight.text())

        # Проверяем, чтобы размер ячейки не превышал размер сетки (если изменение только для текущего изображения)
        if not self.applyToAllGrids and (width > self.gridSize.width() or height > self.gridSize.height()):
            self.showWarning("Некорректные значения", "Размер ячейки не должен превышать размера сетки!")
            return

        # Сохраняем новый размер ячеек
        self.gridCellSize = QSize(width, height)
        self.accept()
