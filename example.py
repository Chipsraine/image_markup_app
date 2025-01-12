import sys  # sys нужен для передачи argv в QApplication
from PyQt5 import QtWidgets
from PyQt5.QtWidgets import QAction
from PyQt5.QtGui import QPixmap

import forms.form
from grid.ClassGrid import ClassGrid


class ExampleApp(QtWidgets.QMainWindow, forms.form.Ui_MainWindow):
    def __init__(self):
        # Это здесь нужно для доступа к переменным, методам
        # и т.д. в файле design.py
        super().__init__()
        self.setupUi(self)
        self.actionImageZoomIn.triggered.connect(self.graphicsViewImage.zoomIn)
        self.actionImageZoomOut.triggered.connect(self.graphicsViewImage.zoomOut)
        self.actionResetImageScale.triggered.connect(self.graphicsViewImage.resetScale)
        self.pushButtonPreviousImage.clicked.connect(self.graphicsViewImage.setAllEmptyCellsToActiveClass)
        
        
    def test(self):
        self.graphicsViewImage.setImage(QPixmap(r"C:\\Users\\WormixGame\\Downloads\\photo_2024-12-31_18-52-09.jpg"))
        self.graphicsViewImage.setGrid(ClassGrid.fromJson({"cell_size": 40, "classes": [{"name":"Кот", "color":"#c8f542"}, {"name" : "Силли", "color": "#4833d4"}], "table" : [{"row": 0, "col": 0, "class": "Кот"}, {"row": 2, "col": 2, "class": "Кот"}]}))
        self.graphicsViewImage.activeClass = self.graphicsViewImage.grid.classes["Силли"]
        
def main():
    app = QtWidgets.QApplication(sys.argv)  # Новый экземпляр QApplication
    window = ExampleApp()  # Создаём объект класса ExampleApp
    window.test()
    window.show()  # Показываем окно

    app.exec_()  
    
if __name__ == '__main__':  # Если мы запускаем файл напрямую, а не импортируем
    main() 