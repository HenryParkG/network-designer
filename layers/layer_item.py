from PyQt5 import QtWidgets, QtGui, QtCore

class LayerItem(QtWidgets.QGraphicsRectItem):
    WIDTH, HEIGHT = 180, 60  # 가로 길이 확장, 높이도 살짝 늘림

    # 레이어 타입별 색상 지정
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
        self.setFlags(QtWidgets.QGraphicsItem.ItemIsMovable |
                      QtWidgets.QGraphicsItem.ItemIsSelectable |
                      QtWidgets.QGraphicsItem.ItemSendsScenePositionChanges)
        self.setAcceptHoverEvents(True)

        # 색상 설정
        color = self.COLOR_MAP.get(layer_type, "#CCCCCC")
        self.setBrush(QtGui.QBrush(QtGui.QColor(color)))
        self.setPen(QtGui.QPen(QtGui.QColor("#555555"), 2))

        # 텍스트 표시
        self.text_item = QtWidgets.QGraphicsSimpleTextItem(self._display_text(), self)
        self.text_item.setPos(8, 8)

        self.connections = []

    def _display_text(self):
        return f"{self.layer_type}\n{self._params_short()}"

    def _params_short(self):
        # 주요 파라미터 간단히 표시
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

    def contextMenuEvent(self, event):
        """우클릭 메뉴 생성"""
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
                # 숫자형이면 변환
                try: val = int(val)
                except: 
                    try: val = float(val)
                    except: pass
                new_params[k] = val
            else:
                new_params[k] = v
        self.params = new_params
        self.text_item.setText(self._display_text())
        
    def mouseReleaseEvent(self, event):
        super().mouseReleaseEvent(event)
        items = self.scene().items(event.scenePos())
        for target in items:
            if isinstance(target, LayerItem) and target != self:
                if target.uid not in self.connections:
                    self.connections.append(target.uid)
                    self.scene().parent_widget.update_connections()
