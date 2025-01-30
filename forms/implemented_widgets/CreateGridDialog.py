from forms.implemented_widgets.ChangeGridSizeDialog import ChangeGridSSizeDialog
from PyQt5.QtCore import QSize
from PyQt5 import QtCore

class CreateGridDialog(ChangeGridSSizeDialog):
    def __init__(self, gridSize :QSize, parent = None):
        super().__init__(gridSize, parent)
        _translate = QtCore.QCoreApplication.translate
        self.setWindowTitle(_translate("ChangeGridCellSizeDialog", "Создать сетку для изображения"))
        self.checkBoxApplyToAll.setText(_translate("ChangeGridCellSizeDialog", "Применить Ко всем изображениям"))