from PyQt5 import QtWidgets, QtGui, QtCore

class LayerItem(QtWidgets.QGraphicsRectItem):
    WIDTH, HEIGHT = 180, 60
    COLOR_MAP = {
        "Linear": "#FFD966",
        "Conv2d": "#6FA8DC",
        "ReLU": "#93C47D",
        "Flatten": "#B4A7D6",
        "Dropout": "#F4CCCC",
        "BatchNorm2d": "#D9D2E9",
        "MaxPool2d": "#FFE599",
        "AvgPool2d": "#9FC5E8",
        "LSTM": "#EA9999"
    }

    def __init__(self, layer_type, params, uid):
        super().__init__(0, 0, self.WIDTH, self.HEIGHT)
        self.layer_type = layer_type
        self.params = dict(params)
        self.uid = uid
        self.connections = []

        self.setFlags(QtWidgets.QGraphicsItem.ItemIsMovable |
                      QtWidgets.QGraphicsItem.ItemIsSelectable |
                      QtWidgets.QGraphicsItem.ItemSendsScenePositionChanges)
        self.setAcceptHoverEvents(True)

        # 색상 적용
        color = self.COLOR_MAP.get(layer_type, "#CCCCCC")
        self.setBrush(QtGui.QBrush(QtGui.QColor(color)))
        self.setPen(QtGui.QPen(QtGui.QColor("#555555"), 2))

        # 텍스트 표시
        self.text_item = QtWidgets.QGraphicsSimpleTextItem(self._display_text(), self)
        self.text_item.setPos(8, 8)

    def _display_text(self):
        return f"{self.layer_type}\n{self._params_short()}"

    def _params_short(self):
        if "out_features" in self.params and "in_features" in self.params:
            return f"{self.params['in_features']}→{self.params['out_features']}"
        if "out_channels" in self.params and "in_channels" in self.params:
            return f"{self.params['in_channels']}→{self.params['out_channels']} k={self.params.get('kernel_size',3)}"
        if "p" in self.params: return f"p={self.params['p']}"
        return ", ".join([f"{k}={v}" for k,v in list(self.params.items())[:2]])

    # ---------------- Context Menu ----------------
    def contextMenuEvent(self, event):
        menu = QtWidgets.QMenu()
        edit_action = menu.addAction("Edit Parameters")
        action = menu.exec_(event.screenPos())
        if action == edit_action:
            self.edit_parameters()

    def edit_parameters(self):
        """파라미터 편집 다이얼로그"""
        from PyQt5.QtWidgets import QInputDialog

        new_params = {}
        for k, v in self.params.items():
            val, ok = QInputDialog.getText(None, f"Edit {self.layer_type}", f"{k}:", text=str(v))
            if ok:
                # 숫자형이면 자동 변환
                try:
                    val = int(val)
                except:
                    try:
                        val = float(val)
                    except:
                        pass
                new_params[k] = val
            else:
                new_params[k] = v

        self.params = new_params
        self.text_item.setText(self._display_text())
