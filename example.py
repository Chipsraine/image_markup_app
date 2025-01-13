import sys  # sys нужен для передачи argv в QApplication
from PyQt5 import QtWidgets
from PyQt5.QtWidgets import QAction
from PyQt5.QtGui import QPixmap
import json
import forms.form
from Json.ClassGridJson import ClassGridJson
from AppState import *

class ExampleApp(QtWidgets.QMainWindow, forms.form.Ui_MainWindow):
    
    def __init__(self):
        # Это здесь нужно для доступа к переменным, методам
        # и т.д. в файле design.py
        super().__init__()
        self.setupUi(self)
        self.appSettings : AppState = AppState()
        self.graphicsViewImage.setAppSettings(self.appSettings)
        self.appSettings.events.onImageSetEvent.connect(self.graphicsViewImage.setImage)
        self.appSettings.events.beforeGridSetEvent.connect(self.graphicsViewImage.unlinkGrid)
        self.appSettings.events.afterGridSetEvent.connect(self.graphicsViewImage.linkGrid)
        self.actionImageZoomIn.triggered.connect(self.graphicsViewImage.zoomIn)
        self.actionImageZoomOut.triggered.connect(self.graphicsViewImage.zoomOut)
        self.actionResetImageScale.triggered.connect(self.graphicsViewImage.resetScale)
        self.pushButtonPreviousImage.clicked.connect(self.graphicsViewImage.fillSelectedArea)
        
        
    def test(self):
        self.appSettings.activeTool = Tool.ASSIGN_TOOL
        image = QPixmap(r"C:\\Users\\WormixGame\\Downloads\\photo_2024-12-31_18-52-09.jpg")
        imageSize = {"height": image.size().height(), "width": image.size().width()}
        self.appSettings.setActiveImage(image)
        data = json.load(open(r'G:\\Projects\\ImageClassificator\\image_markup_app\\example.json', encoding="utf-8"))
        self.appSettings.setActiveGrid(ClassGridJson.fromJson(data, imageSize))
        with open('complex_data.json', 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=4, sort_keys=True, ensure_ascii=False)
        self.appSettings.activeClass = self.appSettings.activeGrid.classes["Силли"]
        
def main():
    app = QtWidgets.QApplication(sys.argv)  # Новый экземпляр QApplication
    window = ExampleApp()  # Создаём объект класса ExampleApp
    window.test()
    window.show()  # Показываем окно

    app.exec_()  
    
if __name__ == '__main__':  # Если мы запускаем файл напрямую, а не импортируем
    main() 