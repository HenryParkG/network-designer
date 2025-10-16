from PyQt5 import QtWidgets, QtGui, QtCore

class LayerItem(QtWidgets.QGraphicsRectItem):
    WIDTH, HEIGHT = 180, 60  # 가로 길이 확장, 높이 살짝 늘림

    # 레이어 타입별 색상
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

        # 이동 가능, 선택 가능, 위치 변경 이벤트
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
        self.text_item.setPos(8, 8)  # 텍스트 패딩

    def _display_text(self):
        return f"{self.layer_type}\n{self._params_short()}"

    def _params_short(self):
        if "out_features" in self.params and "in_features" in self.params:
            return f"{self.params['in_features']}→{self.params['out_features']}"
        if "out_channels" in self.params and "in_channels" in self.params:
            return f"{self.params['in_channels']}→{self.params['out_channels']} k={self.params.get('kernel_size',3)}"
        if "p" in self.params:
            return f"p={self.params['p']}"
        return ", ".join([f"{k}={v}" for k,v in list(self.params.items())[:2]])

    # 박스 이동 시 Sequence 업데이트
    def itemChange(self, change, value):
        if change == QtWidgets.QGraphicsItem.ItemPositionChange:
            if hasattr(self.scene(), "parent_widget"):
                self.scene().parent_widget.update_sequence_from_positions()
        return super().itemChange(change, value)
