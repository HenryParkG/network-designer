from PyQt5 import QtWidgets, QtGui, QtCore
from layers.layers_config import LAYER_TEMPLATES

class PaletteListWidget(QtWidgets.QListWidget):
    def __init__(self):
        super().__init__()
        self.setDragEnabled(True)
        for name in LAYER_TEMPLATES.keys():
            it = QtWidgets.QListWidgetItem(name)
            it.setToolTip(LAYER_TEMPLATES[name]["friendly"])
            self.addItem(it)

    def startDrag(self, supportedActions):
        item = self.currentItem()
        if item:
            mime = QtCore.QMimeData()
            mime.setText(item.text())
            drag = QtGui.QDrag(self)
            drag.setMimeData(mime)
            pix = QtGui.QPixmap(140, 40)
            pix.fill(QtGui.QColor("#E8F0FF"))
            p = QtGui.QPainter(pix)
            p.drawText(8, 24, item.text())
            p.end()
            drag.setPixmap(pix)
            drag.exec_(QtCore.Qt.CopyAction)
