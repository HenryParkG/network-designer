from PyQt5 import QtWidgets, QtGui

class EdgeItem(QtWidgets.QGraphicsLineItem):
    def __init__(self, source, target):
        super().__init__()
        self.source = source
        self.target = target
        pen = QtGui.QPen(QtGui.QColor("#555555"))
        pen.setWidth(2)
        self.setPen(pen)
        self.setZValue(-1)
        self.update_position()

    def update_position(self):
        s = self.source.sceneBoundingRect()
        t = self.target.sceneBoundingRect()
        self.setLine(s.center().x(), s.center().y(), t.center().x(), t.center().y())
