import sys  # sys нужен для передачи argv в QApplication
from PyQt5 import QtWidgets
from PyQt5.QtWidgets import QDialog
from PyQt5.QtGui import QPixmap
import forms.form
from ClassGridSerialization import *
from AppState import *
from forms.implemented_widgets.ChangeGridSizeDialog import ChangeGridSSizeDialog
from forms.implemented_widgets.CreateGridDialog import CreateGridDialog
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
        self.appState.events.beforeFolderSetEvent.connect(self.unlinkFolder)
        self.appState.events.afterFolderSetEvent.connect(self.linkFolder)
        self.appState.events.beforeToolChangeEvent.connect(self.graphicsViewImage.resetToolLayer)
        self.actionImageZoomIn.triggered.connect(self.graphicsViewImage.zoomIn)
        self.actionImageZoomOut.triggered.connect(self.graphicsViewImage.zoomOut)
        self.actionResetImageScale.triggered.connect(self.graphicsViewImage.fitImageInView)
        self.actionEditGridSize.triggered.connect(self.changeGridCellSize)
        self.actionCreateGrid.triggered.connect(self.createGrid)
    
    
    def test(self):
        self.appState.setActiveTool(Tool.ASSIGN_TOOL)
        self.appState.setActiveFolder(Folder(r"test_images", self.appState))
        self.appState.activeFolder.switchToNextImage()
        
                
    def linkFolder(self):
        folder = self.appState.activeFolder
        if folder == None:
            return
        self.pushButtonPreviousImage.clicked.connect(folder.switchToPreviousImage)
        self.pushButtonNextImage.clicked.connect(folder.switchToNextImage)
    
    def unlinkFolder(self):
        folder = self.appState.activeFolder
        if folder == None:
            return
        self.pushButtonPreviousImage.clicked.disconnect(folder.switchToPreviousImage)
        self.pushButtonNextImage.clicked.disconnect(folder.switchToNextImage) 
    
    
    def changeGridCellSize(self):
        dialog = ChangeGridSSizeDialog(self.appState.activeGrid.gridSize, None)
        dialog.show()
        if dialog.exec_():
            self.appState.activeGrid.changeCellSize(dialog.gridCellSize)
            if dialog.applyToAllGrids:
                self.appState.activeFolder.changeAllGridCellSizes(dialog.gridCellSize)
                
                
    def createGrid(self):
        dialog = CreateGridDialog(self.appState.activeImage.size(), None)
        dialog.show()
        if dialog.exec_():
            self.appState.setActiveGrid(ClassGrid(None, None, dialog.gridCellSize, dialog.gridSize))
            if dialog.applyToAllGrids:
                self.appState.activeFolder.createGrids(dialog.gridCellSize)
                
                
    def closeEvent(self, a0):
        self.appState.activeFolder.saveActiveGrid()
        
def main():
    app = QtWidgets.QApplication(sys.argv)  # Новый экземпляр QApplication
    window = ExampleApp()  # Создаём объект класса ExampleApp
    window.test()
    window.show()  # Показываем окно

    app.exec_()  
    
if __name__ == '__main__':  # Если мы запускаем файл напрямую, а не импортируем
    main() 