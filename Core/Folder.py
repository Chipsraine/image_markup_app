from PyQt5.QtGui import QImage, QPixmap
from PyQt5.QtCore import pyqtSignal,  QSize, QObject
from Core.Grid.ClassGrid import ClassGrid
from PIL import Image
from ClassGridSerialization import ClassGridSerializer, ClassGridDeserializer
import os
class Folder (QObject):
    imageChangeEvent = pyqtSignal(int, QPixmap, ClassGrid)
    changingProgressEvent = pyqtSignal(int)
    gridsFolderName = "grids"
    def __init__(self, folderPath):
        super().__init__(None)
        self.folderPath = folderPath
        self.imageFilenames = self.getImageFilenames(self.folderPath)
        self.activeFileIndex = 0
        self.totalFiles = len(self.imageFilenames)

    
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
        return QPixmap(imagePath)
    
    def getImageGrid(self, filename):
        imagePath = self.getImagePath(filename)
        gridPath = self.getGridPath(filename)
        grid = None
        width, height = 0, 0
        
        if not os.path.exists(imagePath) or not os.path.exists(gridPath):
            return None
        
        with Image.open(imagePath) as imageInfo:
            width, height = imageInfo.size    
        
        with open(gridPath, 'r', encoding='utf-8') as fileRead:
            grid = ClassGridDeserializer.fromTxt(fileRead, QSize(width, height))
        
        return grid
    
    def changeAllGridCellSizes(self, cellSize):
        for fileIndex, filename in enumerate(self.imageFilenames):
            if (fileIndex == self.activeFileIndex):
                continue
            
            grid : ClassGrid = self.getImageGrid(filename)
            if grid is None:
                print(f"Для картинки {filename} нет разметки.")
                continue
            
            if not grid.canCellSizeFitInGrid(cellSize):
                print(F"Заданная размерность клетки не позволяет поместить её в сетку.")
                continue
            
            if grid.hasSameCellSize(cellSize):
                print(f"Разметки картинки {filename} уже имеет нужную размерность.")
                continue
            
                
            grid.applyResizeStrategy(cellSize)
            print(f"Разметка картинки {filename} успешно изменена.")
            self.changingProgressEvent.emit(fileIndex + 1, self.totalFiles)
            
    def getActiveFilename(self):
        return self.imageFilenames[self.activeFileIndex]
    
    def prevImage(self):
        self.activeFileIndex = (self.totalFiles + self.activeFileIndex - 1) % self.totalFiles
        self.sendActiveImage()
        
    def setToFirstImage(self):
        self.activeFileIndex = 0
        self.sendActiveImage()
        
    def nextImage(self):
        self.activeFileIndex = (self.totalFiles + self.activeFileIndex + 1) % self.totalFiles
        self.sendActiveImage()
        
    def sendActiveImage(self):
        imageFilename = self.getActiveFilename()
        image = self.getImage(imageFilename)
        grid = self.getImageGrid(imageFilename)
        self.imageChangeEvent.emit(self.activeFileIndex + 1, image, grid)