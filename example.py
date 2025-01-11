import sys  # sys нужен для передачи argv в QApplication
from PyQt5 import QtWidgets
from PyQt5.QtWidgets import QAction

import forms.form


class ExampleApp(QtWidgets.QMainWindow, forms.form.Ui_MainWindow):
    def __init__(self):
        # Это здесь нужно для доступа к переменным, методам
        # и т.д. в файле design.py
        super().__init__()
        self.setupUi(self)
        self.actionImageZoomIn.triggered.connect(self.graphicsViewImage.zoomIn)
        self.actionImageZoomOut.triggered.connect(self.graphicsViewImage.zoomOut)
        self.actionResetImageScale.triggered.connect(self.graphicsViewImage.resetScale)
        
def main():
    app = QtWidgets.QApplication(sys.argv)  # Новый экземпляр QApplication
    window = ExampleApp()  # Создаём объект класса ExampleApp
    window.show()  # Показываем окно
    app.exec_()  
    
if __name__ == '__main__':  # Если мы запускаем файл напрямую, а не импортируем
    main() 