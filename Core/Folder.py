from PyQt5.QtGui import QImage, QPixmap
from PyQt5.QtCore import pyqtSignal,  QSize, QObject
from Core.Grid.ClassGrid import ClassGrid
from PIL import Image
from ClassGridSerialization import ClassGridSerializer, ClassGridDeserializer
import os
from AppState import *

class Folder (QObject):

    sizeChangeProgressEvent = pyqtSignal(int, int)
    counterUpdateEvent = pyqtSignal(int, int)
    
    gridsFolderName = "grids"
    def __init__(self, folderPath, appState):
        super().__init__(None)
        self.folderPath = folderPath
        self.appState : AppState = appState
        self.imageFilenames = None
        self.activeFileIndex = -1
        self.totalFilesCount = 0
        
        self.loadDirectory()
        
    def loadDirectory(self):
        self.imageFilenames = self.getImageFilenames(self.folderPath)
        self.totalFilesCount = len(self.imageFilenames)           
            
    
    @staticmethod
    def getImageFilenames(path):
        image_extensions = ['.jpg', '.png']
        imageFilenames = []
        for filename in os.listdir(path):
            if not os.path.splitext(filename)[1].lower() in image_extensions:
                continue
            
            filepath = os.path.join(path, filename)
            
            if not os.path.isfile(filepath):
                continue
            
            imageFilenames.append(filename)
            
        return imageFilenames
    
    
    def getImagePath(self, filename):
        return os.path.join(self.folderPath, filename)
        
    def getGridPath(self, filename):
        return  os.path.join(self.folderPath, self.gridsFolderName, filename + ".txt")
    
    def getImage(self, filename):
        
        imagePath = self.getImagePath(filename)
        if not os.path.exists(imagePath):
            return None
        
        return QPixmap(imagePath)
    
    def getGrid(self, filename):
        imagePath = self.getImagePath(filename)
        gridPath = self.getGridPath(filename)
        grid = None
        width, height = 0, 0
        
        if not self.imageExists(filename) or not os.path.exists(gridPath):
            return None
        
        with Image.open(imagePath) as imageInfo:
            width, height = imageInfo.size    
        
        with open(gridPath, 'r', encoding='utf-8') as fileRead:
            grid = ClassGridDeserializer.fromTxt(fileRead, QSize(width, height))
        
        return grid
    
    def changeAllGridCellSizes(self, cellSize):
        print("===Начало изменения размера разметки===")
        for fileIndex, filename in enumerate(self.imageFilenames):
            if (fileIndex == self.activeFileIndex):
                continue
            
            grid : ClassGrid = self.getGrid(filename)
            if grid is None:
                print(f"Для картинки {filename} нет разметки.")
                continue
            
            if not grid.canCellSizeFitInGrid(cellSize):
                print(F"Заданная размерность клетки не позволяет поместить её в сетку.")
                continue
            
            if grid.hasSameCellSize(cellSize):
                print(f"Разметка картинки {filename} уже имеет нужную размерность.")
                continue
            
            oldCellSize = grid.cellSize
            newCellSize = cellSize 
                
            grid.applyResizeStrategy(cellSize)
            gridPath = self.getGridPath(filename)
            with open(gridPath, 'w', encoding='utf-8') as fileWrite:
                ClassGridSerializer.toTxt(fileWrite, grid)
            print(f"Разметка картинки {filename} успешно изменена c ({oldCellSize.width()}, {oldCellSize.height()}) на ({newCellSize.width()}, {newCellSize.height()}).")
            self.sizeChangeProgressEvent.emit(fileIndex + 1, self.totalFilesCount)
        print("===Конец изменения размера разметки===")
        
    def createGrids(self, cellSize):
        print("===Начало создания сеток===")
        for fileIndex, filename in enumerate(self.imageFilenames):
            if (fileIndex == self.activeFileIndex):
                continue
            
            if not self.imageExists(filename) or  not self.getGrid(filename) is None:
                continue
            
            
            with Image.open(self.getImagePath(filename)) as imageInfo:
                gridSize = imageInfo.size    

            
            if  not(cellSize.width() <= gridSize.width() and cellSize.height() <= gridSize.height()):
                print(f"Заданная размерность клетки не позволяет поместить её в сетку.")
                continue
            
            gridPath = self.getGridPath(filename)
            with open(gridPath, 'w', encoding='utf-8') as fileWrite:
                ClassGridSerializer.toTxt(fileWrite, ClassGrid(None, None, cellSize, gridSize))
            self.sizeChangeProgressEvent.emit(fileIndex + 1, self.totalFilesCount)
        print("===Конец создания сеток===")
            
    def getActiveFilename(self):
        return self.imageFilenames[self.activeFileIndex]
    
    def saveActiveGrid(self):
        if self.appState.activeGrid == None:
            return
        
        gridPath = self.getGridPath(self.getActiveFilename())
        with open(gridPath, 'w', encoding='utf-8') as fileWrite:
            ClassGridSerializer.toTxt(fileWrite, self.appState.activeGrid)
        
    def setActiveImage(self):
        imageFilename = self.getActiveFilename()
        self.appState.setActiveImageAndGrid(self.getImage(imageFilename), self.getGrid(imageFilename))
        self.updateCounter()
    
    def imageExists(self, filename):
        image_path = self.getImagePath(filename)
        return os.path.exists(image_path)


    def switchToPreviousImage(self):
        if  0 <= self.activeFileIndex and self.activeFileIndex < self.totalFilesCount:
            self.saveActiveGrid()
        
        self.activeFileIndex -= 1
        
        while self.activeFileIndex >= 0 and not self.imageExists(self.getActiveFilename()):
            self.activeFileIndex -= 1
    
        if 0 <= self.activeFileIndex and self.activeFileIndex < self.totalFilesCount:
            self.setActiveImage()
            return
        
        self.loadDirectory()
        if self.totalFilesCount != 0:
            self.activeFileIndex = self.totalFilesCount
            self.switchToPreviousImage()
        

    def switchToNextImage(self):
        if  0 <= self.activeFileIndex and self.activeFileIndex < self.totalFilesCount:
            self.saveActiveGrid()
        
        self.activeFileIndex += 1
        
        while self.activeFileIndex < self.totalFilesCount and not self.imageExists(self.getActiveFilename()):
            self.activeFileIndex += 1
    
        if 0 <= self.activeFileIndex and self.activeFileIndex < self.totalFilesCount:
            self.setActiveImage()
            return
        
        self.loadDirectory()
        if self.totalFilesCount != 0:
            self.activeFileIndex = -1
            self.switchToNextImage()        
        
    

    def updateCounter(self):
        self.counterUpdateEvent.emit(self.activeFileIndex + 1, self.totalFilesCount)