from PyQt5 import QtWidgets, QtCore, QtGui
from AppState import AppState, Tool
from forms.form import Ui_MainWindow
from forms.implemented_widgets.ChangeGridSizeDialog import ChangeGridSSizeDialog
from forms.implemented_widgets.CreateGridDialog import CreateGridDialog
from Core.Folder import Folder
from Core.Grid.ClassGrid import ClassGrid
from Core.Grid.Class import Class


class ExampleApp(QtWidgets.QMainWindow, Ui_MainWindow):
    def __init__(self, parent=None):
        # Вызов конструктора родительских классов; не ставьте брейкпоинты на super().__init__()
        super(ExampleApp, self).__init__(parent)
        print(">> super().__init__() выполнен")
        self.setupUi(self)
        print(">> setupUi() выполнен")

        # Настраиваем тулбар – действия инструментов становятся checkable и объединяются в группу
        self.actionNoTool.setCheckable(True)
        self.actionAssignTool.setCheckable(True)
        self.actionDeleteTool.setCheckable(True)
        self.actionSelectAreaTool.setCheckable(True)
        self.toolActionGroup = QtWidgets.QActionGroup(self)
        self.toolActionGroup.setExclusive(True)
        self.toolActionGroup.addAction(self.actionNoTool)
        self.toolActionGroup.addAction(self.actionAssignTool)
        self.toolActionGroup.addAction(self.actionDeleteTool)
        self.toolActionGroup.addAction(self.actionSelectAreaTool)
        print(">> Тулбар настроен: действия объединены в QActionGroup")

        # Инициализируем состояние приложения
        self.appState = AppState()
        self.appState.setActiveTool(Tool.NO_TOOL)
        print(">> AppState создан, activeTool = NO_TOOL")
        self.graphicsViewImage.setAppSettings(self.appState)

        # Подключаем события AppState к методам графического виджета
        self.appState.events.onImageSetEvent.connect(self.graphicsViewImage.setImage)
        self.appState.events.beforeGridSetEvent.connect(self.graphicsViewImage.unlinkGrid)
        self.appState.events.afterGridSetEvent.connect(self.graphicsViewImage.linkGrid)
        self.appState.events.beforeFolderSetEvent.connect(self.unlinkFolder)
        self.appState.events.afterFolderSetEvent.connect(self.linkFolder)
        self.appState.events.beforeToolChangeEvent.connect(self.graphicsViewImage.resetToolLayer)
        # При обновлении сетки обновляем список классов
        self.appState.events.afterGridSetEvent.connect(self.updateClassList)
        print(">> События AppState подключены")

        # Подключаем действия меню
        self.actionSelectImagesFolder.triggered.connect(self.selectImagesFolder)
        self.actionImageZoomIn.triggered.connect(self.graphicsViewImage.zoomIn)
        self.actionImageZoomOut.triggered.connect(self.graphicsViewImage.zoomOut)
        self.actionResetImageScale.triggered.connect(self.graphicsViewImage.fitImageInView)
        self.actionEditGridSize.triggered.connect(self.changeGridCellSize)
        self.actionCreateGrid.triggered.connect(self.createGrid)
        print(">> Действия меню подключены")

        # Подключаем действия тулбара для инструментов
        self.actionNoTool.triggered.connect(lambda: self.setTool(Tool.NO_TOOL))
        self.actionAssignTool.triggered.connect(lambda: self.setTool(Tool.ASSIGN_TOOL))
        self.actionDeleteTool.triggered.connect(lambda: self.setTool(Tool.DELETE_TOOL))
        self.actionSelectAreaTool.triggered.connect(lambda: self.setTool(Tool.SELECT_AREA_TOOL))
        print(">> Действия тулбара для инструментов подключены")

        # Настраиваем панель классов: скрываем listViewClasses, создаём новый QListWidget
        self.listViewClasses.hide()
        self.classListWidget = QtWidgets.QListWidget(self.groupBoxClasses)
        self.classListWidget.setSelectionMode(QtWidgets.QAbstractItemView.SingleSelection)
        self.verticalLayout.insertWidget(0, self.classListWidget)
        self.classListWidget.itemClicked.connect(self.onClassSelected)
        self.classListWidget.itemDoubleClicked.connect(self.onClassDoubleClicked)
        self.classListWidget.itemChanged.connect(self.onClassItemChanged)
        print(">> Панель классов настроена (QListWidget создан)")

        # Добавляем кнопки для управления классами: "Добавить", "Удалить" и "Изменить название"
        self.addClassButton = QtWidgets.QPushButton("Добавить класс", self.groupBoxClasses)
        self.deleteClassButton = QtWidgets.QPushButton("Удалить класс", self.groupBoxClasses)
        self.changeNameButton = QtWidgets.QPushButton("Изменить название", self.groupBoxClasses)
        btnLayout = QtWidgets.QHBoxLayout()
        btnLayout.addWidget(self.addClassButton)
        btnLayout.addWidget(self.deleteClassButton)
        btnLayout.addWidget(self.changeNameButton)
        self.verticalLayout.addLayout(btnLayout)
        self.addClassButton.clicked.connect(self.addClass)
        self.deleteClassButton.clicked.connect(self.deleteClass)
        self.changeNameButton.clicked.connect(self.changeClassName)
        print(">> Кнопки управления классами подключены")

        # Добавляем счётчик изображений под областью изображения
        self.imageCounterLabel = QtWidgets.QLabel(self.groupBoxImage)
        self.imageCounterLabel.setAlignment(QtCore.Qt.AlignCenter)
        self.gridLayout.addWidget(self.imageCounterLabel, 3, 0, 1, 2)
        self.imageCounterLabel.setText("0/0")
        print(">> Счётчик изображений добавлен")

        # При запуске открываем диалог выбора папки
        self.selectImagesFolder()
        print(">> Инициализация ExampleApp завершена")

    def selectImagesFolder(self):
        folder_path = QtWidgets.QFileDialog.getExistingDirectory(self, "Выбрать папку с изображениями")
        if folder_path:
            folder = Folder(folder_path, self.appState)
            self.appState.setActiveFolder(folder)
            # Подключаем сигнал обновления счётчика
            folder.counterUpdateEvent.connect(self.updateImageCounter)
            folder.switchToNextImage()  # Загружается первое изображение и сетка
            if self.appState.activeGrid and self.appState.activeGrid.classes:
                self.appState.setActiveClass(self.appState.activeGrid.classes[0])
            self.updateClassList()
            print(">> Папка выбрана, сетка загружена")
        else:
            QtWidgets.QMessageBox.warning(self, "Ошибка", "Папка не выбрана!")
            QtWidgets.QApplication.quit()

    def updateImageCounter(self, current, total):
        self.imageCounterLabel.setText(f"{current}/{total}")
        print(">> Счётчик обновлён:", current, "/", total)

    def updateClassList(self):
        self.classListWidget.blockSignals(True)
        self.classListWidget.clear()
        if self.appState.activeGrid and self.appState.activeGrid.classes:
            for cls in self.appState.activeGrid.classes:
                item = QtWidgets.QListWidgetItem(cls.name())
                pixmap = QtGui.QPixmap(20, 20)
                pixmap.fill(cls.color())
                item.setIcon(QtGui.QIcon(pixmap))
                item.setFlags(
                    item.flags() | QtCore.Qt.ItemIsEditable | QtCore.Qt.ItemIsSelectable | QtCore.Qt.ItemIsEnabled)
                item.setData(QtCore.Qt.UserRole, cls)
                self.classListWidget.addItem(item)
        self.classListWidget.blockSignals(False)
        print(">> Список классов обновлён")

    def onClassSelected(self, item):
        cls = item.data(QtCore.Qt.UserRole)
        self.appState.setActiveClass(cls)
        print(">> Active class set to:", cls.name())

    def onClassDoubleClicked(self, item):
        cls = item.data(QtCore.Qt.UserRole)
        # Открываем диалог выбора цвета; после закрытия сразу обновляем сетку
        color = QtWidgets.QColorDialog.getColor(initial=cls.color(), parent=self, title="Выбрать цвет")
        if color.isValid():
            cls.setColor(color)
            pixmap = QtGui.QPixmap(20, 20)
            pixmap.fill(color)
            item.setIcon(QtGui.QIcon(pixmap))
            print(">> Class color updated:", color.name())
            # Обновляем сетку, чтобы сразу увидеть изменения
            self.saveAndReloadGrid()
            self.updateClassList()

    def onClassItemChanged(self, item):
        # Если изменяется имя класса через редактирование в списке, обновляем сетку
        cls = item.data(QtCore.Qt.UserRole)
        new_name = item.text()
        if new_name != cls.name():
            cls.setName(new_name)
            print(">> Class name updated to:", new_name)
            self.saveAndReloadGrid()
            self.updateClassList()

    def changeClassName(self):
        # Отдельная кнопка для изменения названия класса
        selected_items = self.classListWidget.selectedItems()
        if not selected_items:
            QtWidgets.QMessageBox.warning(self, "Ошибка", "Не выбран класс для изменения имени")
            return
        item = selected_items[0]
        cls = item.data(QtCore.Qt.UserRole)
        new_name, ok = QtWidgets.QInputDialog.getText(self, "Изменить название", "Новое название:", text=cls.name())
        if ok and new_name and new_name != cls.name():
            cls.setName(new_name)
            print(">> Class name updated via button to:", new_name)
            self.saveAndReloadGrid()
            self.updateClassList()

    def addClass(self):
        default_color = QtGui.QColor("red")
        new_class = Class("Новый класс", default_color)
        if self.appState.activeGrid:
            self.appState.activeGrid.classes.append(new_class)
            print(">> Added new class:", new_class.name())
            self.saveAndReloadGrid()
            self.updateClassList()

    def deleteClass(self):
        selected_items = self.classListWidget.selectedItems()
        if not selected_items:
            QtWidgets.QMessageBox.warning(self, "Ошибка", "Не выбран класс для удаления")
            return
        if len(self.appState.activeGrid.classes) <= 1:
            QtWidgets.QMessageBox.warning(self, "Ошибка", "Нельзя удалить последний класс")
            return
        item = selected_items[0]
        cls = item.data(QtCore.Qt.UserRole)
        if self.appState.activeGrid:
            try:
                self.appState.activeGrid.classes.remove(cls)
            except ValueError:
                pass
            self.appState.activeGrid.table.removeClassFromTable(cls)
            print(">> Deleted class:", cls.name())
            self.saveAndReloadGrid()
            self.updateClassList()
            if self.appState.activeGrid.classes:
                self.appState.setActiveClass(self.appState.activeGrid.classes[0])
            else:
                self.appState.setActiveClass(None)

    def saveAndReloadGrid(self):
        folder = self.appState.activeFolder
        if folder:
            print(">> Saving active grid...")
            folder.saveActiveGrid()
            print(">> Reloading grid from file...")
            new_grid = folder.getGrid(folder.getActiveFilename())
            if new_grid:
                self.appState.setActiveGrid(new_grid)
                self.updateClassList()
                print(">> Grid reloaded successfully.")
            else:
                print(">> Failed to reload grid.")

    def unlinkFolder(self):
        folder = self.appState.activeFolder
        if folder is None:
            return
        try:
            self.pushButtonPreviousImage.clicked.disconnect(folder.switchToPreviousImage)
            self.pushButtonNextImage.clicked.disconnect(folder.switchToNextImage)
        except Exception:
            pass

    def linkFolder(self):
        folder = self.appState.activeFolder
        if folder is None:
            return
        self.pushButtonPreviousImage.clicked.connect(folder.switchToPreviousImage)
        self.pushButtonNextImage.clicked.connect(folder.switchToNextImage)

    def changeGridCellSize(self):
        dialog = ChangeGridSSizeDialog(self.appState.activeGrid.gridSize, None)
        dialog.show()
        if dialog.exec_():
            self.appState.activeGrid.changeCellSize(dialog.gridCellSize)
            if dialog.applyToAllGrids:
                progressDialog = QtWidgets.QProgressDialog("Изменение размера сеток...", "", 0,
                                                           self.appState.activeFolder.totalFilesCount, self)
                progressDialog.setWindowModality(QtCore.Qt.WindowModal)
                progressDialog.setMinimumDuration(0)
                progressDialog.setValue(0)
                progressDialog.setCancelButton(None)  # Полностью убираем кнопку отмены
                self.appState.activeFolder.sizeChangeProgressEvent.connect(
                    lambda current, total: progressDialog.setValue(current))
                self.appState.activeFolder.changeAllGridCellSizes(dialog.gridCellSize)
                progressDialog.close()
            self.saveAndReloadGrid()

    def createGrid(self):
        dialog = CreateGridDialog(self.appState.activeImage.size(), None)
        dialog.show()
        if dialog.exec_():
            self.appState.setActiveGrid(ClassGrid(None, None, dialog.gridCellSize, dialog.gridSize))
            if dialog.applyToAllGrids:
                progressDialog = QtWidgets.QProgressDialog("Создание сеток...", "", 0,
                                                           self.appState.activeFolder.totalFilesCount, self)
                progressDialog.setWindowModality(QtCore.Qt.WindowModal)
                progressDialog.setMinimumDuration(0)
                progressDialog.setValue(0)
                progressDialog.setCancelButton(None)  # Полностью убираем кнопку отмены
                self.appState.activeFolder.sizeChangeProgressEvent.connect(
                    lambda current, total: progressDialog.setValue(current))
                self.appState.activeFolder.createGrids(dialog.gridCellSize)
                progressDialog.close()
            self.saveAndReloadGrid()
            self.updateClassList()

    def setTool(self, tool):
        self.appState.setActiveTool(tool)
        #print(">> Active tool set to:", tool.name()) сука пидр ебаный
        if tool == Tool.NO_TOOL:
            self.graphicsViewImage.resetToolLayer()

    def closeEvent(self, event):
        if self.appState.activeFolder:
            self.appState.activeFolder.saveActiveGrid()


if __name__ == '__main__':
    # Этот файл можно запускать напрямую для тестирования business-логики
    app = QtWidgets.QApplication([])
    window = ExampleApp()
    window.show()
    app.exec_()
