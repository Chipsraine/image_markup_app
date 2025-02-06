# example_app.py
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
        super(ExampleApp, self).__init__(parent)
        self.setupUi(self)

        # Настраиваем тулбар: явно устанавливаем checkable и группируем действия
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

        # Инициализируем состояние приложения
        self.appState = AppState()
        self.appState.setActiveTool(Tool.ASSIGN_TOOL)
        self.graphicsViewImage.setAppSettings(self.appState)

        # Подключаем события AppState к методам графического виджета
        self.appState.events.onImageSetEvent.connect(self.graphicsViewImage.setImage)
        self.appState.events.beforeGridSetEvent.connect(self.graphicsViewImage.unlinkGrid)
        self.appState.events.afterGridSetEvent.connect(self.graphicsViewImage.linkGrid)
        self.appState.events.beforeFolderSetEvent.connect(self.unlinkFolder)
        self.appState.events.afterFolderSetEvent.connect(self.linkFolder)
        self.appState.events.beforeToolChangeEvent.connect(self.graphicsViewImage.resetToolLayer)
        # При каждом обновлении сетки (например, после переключения изображения) обновляем список классов
        self.appState.events.afterGridSetEvent.connect(self.updateClassList)

        # Подключаем действия меню
        self.actionSelectImagesFolder.triggered.connect(self.selectImagesFolder)
        self.actionImageZoomIn.triggered.connect(self.graphicsViewImage.zoomIn)
        self.actionImageZoomOut.triggered.connect(self.graphicsViewImage.zoomOut)
        self.actionResetImageScale.triggered.connect(self.graphicsViewImage.fitImageInView)
        self.actionEditGridSize.triggered.connect(self.changeGridCellSize)
        self.actionCreateGrid.triggered.connect(self.createGrid)

        # Подключаем действия тулбара для выбора инструментов
        self.actionNoTool.triggered.connect(lambda: self.setTool(Tool.NO_TOOL))
        self.actionAssignTool.triggered.connect(lambda: self.setTool(Tool.ASSIGN_TOOL))
        self.actionDeleteTool.triggered.connect(lambda: self.setTool(Tool.DELETE_TOOL))
        self.actionSelectAreaTool.triggered.connect(lambda: self.setTool(Tool.SELECT_AREA_TOOL))

        # Настраиваем панель классов: скрываем listViewClasses, создаем новый QListWidget
        self.listViewClasses.hide()
        self.classListWidget = QtWidgets.QListWidget(self.groupBoxClasses)
        self.classListWidget.setSelectionMode(QtWidgets.QAbstractItemView.SingleSelection)
        self.verticalLayout.insertWidget(0, self.classListWidget)
        self.classListWidget.itemClicked.connect(self.onClassSelected)
        self.classListWidget.itemDoubleClicked.connect(self.onClassDoubleClicked)
        self.classListWidget.itemChanged.connect(self.onClassItemChanged)

        # Добавляем кнопки "Добавить класс" и "Удалить класс"
        self.addClassButton = QtWidgets.QPushButton("Добавить класс", self.groupBoxClasses)
        self.deleteClassButton = QtWidgets.QPushButton("Удалить класс", self.groupBoxClasses)
        btnLayout = QtWidgets.QHBoxLayout()
        btnLayout.addWidget(self.addClassButton)
        btnLayout.addWidget(self.deleteClassButton)
        self.verticalLayout.addLayout(btnLayout)
        self.addClassButton.clicked.connect(self.addClass)
        self.deleteClassButton.clicked.connect(self.deleteClass)

        # При запуске сразу открываем диалог выбора папки с изображениями
        self.selectImagesFolder()

    def selectImagesFolder(self):
        folder_path = QtWidgets.QFileDialog.getExistingDirectory(self, "Выбрать папку с изображениями")
        if folder_path:
            folder = Folder(folder_path, self.appState)
            self.appState.setActiveFolder(folder)
            folder.switchToNextImage()  # Загружается первое изображение и сетка
            if self.appState.activeGrid and self.appState.activeGrid.classes:
                self.appState.setActiveClass(self.appState.activeGrid.classes[0])
            self.updateClassList()
        else:
            QtWidgets.QMessageBox.warning(self, "Ошибка", "Папка не выбрана!")
            QtWidgets.QApplication.quit()

    def updateClassList(self):
        """Обновляет список классов в classListWidget согласно appState.activeGrid.classes."""
        self.classListWidget.blockSignals(True)
        self.classListWidget.clear()
        if self.appState.activeGrid and self.appState.activeGrid.classes:
            for cls in self.appState.activeGrid.classes:
                item = QtWidgets.QListWidgetItem(cls.name())
                pixmap = QtGui.QPixmap(20, 20)
                pixmap.fill(cls.color())
                item.setIcon(QtGui.QIcon(pixmap))
                # Разрешаем редактирование имени
                item.setFlags(
                    item.flags() | QtCore.Qt.ItemIsEditable | QtCore.Qt.ItemIsSelectable | QtCore.Qt.ItemIsEnabled)
                item.setData(QtCore.Qt.UserRole, cls)
                self.classListWidget.addItem(item)
        self.classListWidget.blockSignals(False)

    def onClassSelected(self, item):
        cls = item.data(QtCore.Qt.UserRole)
        self.appState.setActiveClass(cls)
        print("Active class set to:", cls.name())

    def onClassDoubleClicked(self, item):
        # Изменяем только цвет – не перезагружаем сетку
        cls = item.data(QtCore.Qt.UserRole)
        color = QtWidgets.QColorDialog.getColor(initial=cls.color(), parent=self, title="Выбрать цвет")
        if color.isValid():
            cls.setColor(color)
            pixmap = QtGui.QPixmap(20, 20)
            pixmap.fill(color)
            item.setIcon(QtGui.QIcon(pixmap))
            print("Class color updated:", color.name())
            # Не вызываем saveAndReloadGrid() здесь, чтобы не сбрасывать возможность изменения имени

    def onClassItemChanged(self, item):
        cls = item.data(QtCore.Qt.UserRole)
        new_name = item.text()
        if new_name != cls.name():
            cls.setName(new_name)
            print("Class name updated to:", new_name)
            # После изменения имени вызываем сохранение и перезагрузку сетки
            self.saveAndReloadGrid()

    def addClass(self):
        default_color = QtGui.QColor("red")
        new_class = Class("Новый класс", default_color)
        if self.appState.activeGrid:
            self.appState.activeGrid.classes.append(new_class)
            print("Added new class:", new_class.name())
            self.saveAndReloadGrid()
            self.updateClassList()

    def deleteClass(self):
        selected_items = self.classListWidget.selectedItems()
        if not selected_items:
            QtWidgets.QMessageBox.warning(self, "Ошибка", "Не выбран класс для удаления")
            return
        item = selected_items[0]
        cls = item.data(QtCore.Qt.UserRole)
        if self.appState.activeGrid:
            try:
                self.appState.activeGrid.classes.remove(cls)
            except ValueError:
                pass
            self.appState.activeGrid.table.removeClassFromTable(cls)
            print("Deleted class:", cls.name())
            self.saveAndReloadGrid()
            self.updateClassList()
            if self.appState.activeGrid.classes:
                self.appState.setActiveClass(self.appState.activeGrid.classes[0])
            else:
                self.appState.setActiveClass(None)

    def saveAndReloadGrid(self):
        """Сохраняет текущую сетку и перезагружает её из файла, затем обновляет список классов."""
        folder = self.appState.activeFolder
        if folder:
            print("Saving active grid...")
            folder.saveActiveGrid()
            print("Reloading grid from file...")
            new_grid = folder.getGrid(folder.getActiveFilename())
            if new_grid:
                self.appState.setActiveGrid(new_grid)
                self.updateClassList()
                print("Grid reloaded successfully.")
            else:
                print("Failed to reload grid.")

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
                self.appState.activeFolder.changeAllGridCellSizes(dialog.gridCellSize)
            self.saveAndReloadGrid()

    def createGrid(self):
        dialog = CreateGridDialog(self.appState.activeImage.size(), None)
        dialog.show()
        if dialog.exec_():
            self.appState.setActiveGrid(ClassGrid(None, None, dialog.gridCellSize, dialog.gridSize))
            if dialog.applyToAllGrids:
                self.appState.activeFolder.createGrids(dialog.gridCellSize)
            self.saveAndReloadGrid()
            self.updateClassList()

    def setTool(self, tool):
        self.appState.setActiveTool(tool)
        # print("Active tool set to:", tool.name())
        # Если переключаемся на NO_TOOL, можно принудительно обновить отображение
        if tool == Tool.NO_TOOL:
            self.graphicsViewImage.resetToolLayer()

    def closeEvent(self, event):
        if self.appState.activeFolder:
            self.appState.activeFolder.saveActiveGrid()


if __name__ == '__main__':
    # Для тестирования можно запускать этот файл напрямую
    app = QtWidgets.QApplication([])
    window = ExampleApp()
    window.show()
    app.exec_()
