from PyQt5 import QtWidgets, QtCore
from PyQt5 import QtWidgets, QtCore, QtGui

class CanvasView(QtWidgets.QGraphicsView):
    def __init__(self, scene, parent_window):
        super().__init__(scene)
        self.parent_window = parent_window
        self.setRenderHints(QtGui.QPainter.Antialiasing | QtGui.QPainter.TextAntialiasing)
        self.setAcceptDrops(True)
        self.setSceneRect(0, 0, 1600, 1000)
        self.setDragMode(QtWidgets.QGraphicsView.RubberBandDrag)

    def dragEnterEvent(self, e):
        if e.mimeData().hasText(): e.acceptProposedAction()
        else: super().dragEnterEvent(e)

    def dragMoveEvent(self, e):
        if e.mimeData().hasText(): e.acceptProposedAction()
        else: super().dragMoveEvent(e)

    def dropEvent(self, e):
        if e.mimeData().hasText():
            name = e.mimeData().text()
            pos = self.mapToScene(e.pos())
            self.parent_window.add_layer(name, pos)
            e.acceptProposedAction()
        else: super().dropEvent(e)
