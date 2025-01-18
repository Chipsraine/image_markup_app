from forms.change_grid_size_dialog import Ui_ChangeGridCellSizeDialog
from PyQt5.QtWidgets import QDialog, QMessageBox
from PyQt5.QtCore import QSize
from PyQt5.QtGui import QIntValidator


class ChangeGridSSizeDialog(QDialog, Ui_ChangeGridCellSizeDialog):
    def __init__(self, gridSize :QSize, parent = None):
        QDialog.__init__(self, parent)
        self.setupUi(self)
        self.gridSize = gridSize
        self.gridCellSize :QSize = None
        self.applyToAllGrids : bool = False
        
        validator = QIntValidator(self)
        validator.setBottom(1)
                
        self.inputHeight.setValidator(validator)
        self.inputWidth.setValidator(validator)
        
        self.labelGridSize.setText(f"{self.gridSize.width()}x{self.gridSize.height()}")
        self.checkBoxApplyToAll.setCheckState(False)
        
        self.pushButtonCancel.clicked.connect(self.close)
        self.pushButtonOk.clicked.connect(self.processApply)
        
    def showWarning(self, title, text):
        messageBox =  QMessageBox(QMessageBox.Icon.Warning, title, text)
        messageBox.show()
        messageBox.exec_()
                
    def processApply(self):
        width, height = 0, 0
        self.applyToAllGrids = self.checkBoxApplyToAll.checkState()
        
        if not self.inputWidth.hasAcceptableInput() or not self.inputHeight.hasAcceptableInput():
            self.showWarning("Некорректные значения", "Размер ячейки должен быть целым числом больше 0!")
            return
        
        width = int(self.inputWidth.text())
        height = int(self.inputHeight.text())
        
        if not self.applyToAllGrids and (width > self.gridSize.width() or height > self.gridSize.height()):
            self.showWarning("Некорректные значения", "Размер ячейки не должен превышать размера сетки!")
            return
        
        self.gridCellSize = QSize(width, height)
        
        self.accept()