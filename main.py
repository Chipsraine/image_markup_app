import sys  # sys нужен для передачи argv в QApplication
from PyQt5 import QtWidgets
from PyQt5.QtWidgets import QAction
from PyQt5.QtGui import QPixmap, QColor
import json
import forms.form
from ClassGridSerialization import *
from AppState import *

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
        self.pushButtonPreviousImage.clicked.connect(self.graphicsViewImage.fillEmptyCellsWithClass)
        self.pushButtonNextImage.clicked.connect(self.test2)
        
        
    def test(self):
        self.appState.activeTool = Tool.ASSIGN_TOOL
        image = QPixmap(r"example.jpg")
        imageSize = image.size()
        self.appState.setActiveImage(image)
        with open('example.txt', 'r', encoding='utf-8') as fileRead:
            self.appState.setActiveGrid(ClassGridSerializer.fromTxt(fileRead, imageSize))
            
        
        self.appState.activeClass = self.appState.activeGrid.classes[0]
    
    def test2(self):
        width, height = 40, 40
        self.appState.activeGrid.changeCellSize(QSize(width,height))
    
    # def mousePressEvent(self, a0):
    #     self.appState.activeClass.setColor(QColor("#c482e5"))
        
    def closeEvent(self, a0):
        with open('example.txt', 'w', encoding='utf-8') as fileWrite:
            ClassGridDeserializer.toTxt(fileWrite, self.appState.activeGrid)
        
def main():
    app = QtWidgets.QApplication(sys.argv)  # Новый экземпляр QApplication
    window = ExampleApp()  # Создаём объект класса ExampleApp
    window.test()
    window.show()  # Показываем окно

    app.exec_()  
    
if __name__ == '__main__':  # Если мы запускаем файл напрямую, а не импортируем
    main() 