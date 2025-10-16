from PyQt5 import QtWidgets, QtGui

class EdgeItem(QtWidgets.QGraphicsLineItem):
    def __init__(self, source_item, target_item):
        super().__init__()
        self.source_item = source_item
        self.target_item = target_item
        self.setPen(QtGui.QPen(QtGui.QColor("black"), 2))
        
        self.setZValue(-1)

        self.update_position()

    def update_position(self):
        src_center = self.source_item.sceneBoundingRect().center()
        tgt_center = self.target_item.sceneBoundingRect().center()
        self.setLine(src_center.x(), src_center.y(), tgt_center.x(), tgt_center.y())

