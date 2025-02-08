from PyQt5.QtWidgets import QGraphicsView

class ZoomableGraphicsView(QGraphicsView):
    """
    Виджет для отображения графической сцены с поддержкой масштабирования.
    Позволяет увеличивать, уменьшать и сбрасывать масштаб изображения.
    """

    def __init__(self, parent=None):
        """
        Инициализирует объект графического представления с возможностью масштабирования.

        :param parent: Родительский объект.
        """
        super().__init__(parent)

    def zoomIn(self):
        """
        Увеличивает масштаб графической сцены.
        """
        self.scale(1.25, 1.25)

    def zoomOut(self):
        """
        Уменьшает масштаб графической сцены.
        """
        self.scale(0.8, 0.8)

    def resetScale(self, ratioX, ratioY):
        """
        Сбрасывает масштаб изображения и устанавливает новый коэффициент.

        :param ratioX: Коэффициент масштабирования по X.
        :param ratioY: Коэффициент масштабирования по Y.
        """
        self.resetTransform()
        ratio = min(ratioX, ratioY)
        self.scale(ratio, ratio)
