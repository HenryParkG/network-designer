from PyQt5 import QtWidgets, QtGui, QtCore

class LayerItem(QtWidgets.QGraphicsRectItem):
    WIDTH, HEIGHT = 140, 50
    def __init__(self, layer_type, params, uid):
        super().__init__(0, 0, self.WIDTH, self.HEIGHT)
        self.layer_type = layer_type
        self.params = dict(params)
        self.uid = uid
        self.setFlags(QtWidgets.QGraphicsItem.ItemIsMovable|
                      QtWidgets.QGraphicsItem.ItemIsSelectable|
                      QtWidgets.QGraphicsItem.ItemSendsScenePositionChanges)
        self.setAcceptHoverEvents(True)
        self.text_item = QtWidgets.QGraphicsSimpleTextItem(self._display_text(), self)
        self.text_item.setPos(8, 8)
        self.connections = []

    def _display_text(self):
        return f"{self.layer_type}\n{self._params_short()}"

    def _params_short(self):
        if "out_features" in self.params and "in_features" in self.params:
            return f"{self.params['in_features']}→{self.params['out_features']}"
        if "out_channels" in self.params and "in_channels" in self.params:
            return f"{self.params['in_channels']}→{self.params['out_channels']} k={self.params.get('kernel_size',3)}"
        if "p" in self.params: return f"p={self.params['p']}"
        return ", ".join([f"{k}={v}" for k,v in list(self.params.items())[:2]])

    def itemChange(self, change, value):
        if change == QtWidgets.QGraphicsItem.ItemPositionChange:
            if hasattr(self.scene(), "parent_widget"):
                self.scene().parent_widget.update_sequence_from_positions()
        return super().itemChange(change, value)
