import sys  # sys нужен для передачи argv в QApplication
from PyQt5 import QtWidgets
from PyQt5.QtWidgets import QDialog
from PyQt5.QtGui import QPixmap
import forms.form
from ClassGridSerialization import *
from AppState import *
from forms.implemented_widgets.ChangeGridSizeDialog import ChangeGridSSizeDialog
from Core.Folder import Folder


class ExampleApp(QtWidgets.QMainWindow, forms.form.Ui_MainWindow):
    
    def __init__(self):
        # Это здесь нужно для доступа к переменным, методам
        # и т.д. в файле design.py
        super().__init__()
        self.setupUi(self)
        self.appState : AppState = AppState()
        self.graphicsViewImage.setAppSettings(self.appState)
        self.appState.events.onImageSetEvent.connect(self.graphicsViewImage.setImage)
        self.appState.events.beforeGridSetEvent.connect(self.graphicsViewImage.unlinkGrid)
        self.appState.events.afterGridSetEvent.connect(self.graphicsViewImage.linkGrid)
        self.actionImageZoomIn.triggered.connect(self.graphicsViewImage.zoomIn)
        self.actionImageZoomOut.triggered.connect(self.graphicsViewImage.zoomOut)
        self.actionResetImageScale.triggered.connect(self.graphicsViewImage.fitImageInView)
        self.actionEditGridSize.triggered.connect(self.changeGridCellSize)
        
        
    def test(self):
        self.appState.activeTool = Tool.ASSIGN_TOOL
        self.appState.activeFolder = Folder(r"test_images")
        self.appState.activeFolder.imageChangeEvent.connect(self.imageUpdated)
        self.appState.activeFolder.setToFirstImage()
        
        self.linkFolder()
        
    def linkFolder(self):
        folder = self.appState.activeFolder
        self.pushButtonPreviousImage.clicked.connect(folder.prevImage)
        self.pushButtonNextImage.clicked.connect(folder.nextImage)
    
    
    def imageUpdated(self, index, image, grid):
        self.appState.setActiveImageAndGrid(image, grid)
        self.appState.activeClass = self.appState.activeGrid.classes[0]

        
    def changeGridCellSize(self):
        dialog = ChangeGridSSizeDialog(self.appState.activeGrid.gridSize, None)
        dialog.show()
        if dialog.exec_():
            if dialog.applyToAllGrids:
                self.appState.activeFolder.changeAllGridCellSizes(dialog.gridCellSize)
            else: 
                self.appState.activeGrid.changeCellSize(dialog.gridCellSize)
        
def main():
    app = QtWidgets.QApplication(sys.argv)  # Новый экземпляр QApplication
    window = ExampleApp()  # Создаём объект класса ExampleApp
    window.test()
    window.show()  # Показываем окно

    app.exec_()  
    
if __name__ == '__main__':  # Если мы запускаем файл напрямую, а не импортируем
    main() 