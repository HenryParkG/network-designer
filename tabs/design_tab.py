import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), "..", "data"))

from PyQt5 import QtWidgets, QtCore
from palette.palette_widget import PaletteListWidget
from canvas.canvas_view import CanvasView
from layers.layer_item import LayerItem
from layers.edge_item import EdgeItem
from layers.layers_config import LAYER_TEMPLATES
from utils.export_utils import export_to_pytorch
from utils.save_load_utils import save_design_json, load_design_json
from utils.validate_network import validate_network
from data.predefined_model import PREDEFINED_MODELS

class DesignTab(QtWidgets.QWidget):
    """네트워크 설계 탭"""
    def __init__(self, parent_window=None):
        super().__init__()
        self.parent_window = parent_window

        self.layer_uid = 0
        self.layer_items = {}
        self.edges = []

        layout = QtWidgets.QHBoxLayout(self)
        layout.setContentsMargins(8, 8, 8, 8)

        # ---------------- Palette (위) + Predefined Models (아래) ----------------
        palette_box = QtWidgets.QGroupBox("Layer Palette")
        palette_layout = QtWidgets.QVBoxLayout(palette_box)

        # Palette List (상단, 높이 비율 3)
        self.palette_list = PaletteListWidget()
        palette_layout.addWidget(self.palette_list, 3)

        # Predefined Models (하단, 높이 비율 2)
        predefined_box = QtWidgets.QGroupBox("Predefined Models")
        predefined_layout = QtWidgets.QVBoxLayout(predefined_box)

        self.predefined_list = QtWidgets.QListWidget()
        self.predefined_list.setDragDropMode(QtWidgets.QAbstractItemView.NoDragDrop)
        self.predefined_list.setSelectionMode(QtWidgets.QAbstractItemView.SingleSelection)

        # 미리 정의된 모델 템플릿
        self.PREDEFINED_MODELS = PREDEFINED_MODELS

        # 리스트에 모델 이름 추가
        for model_name in self.PREDEFINED_MODELS.keys():
            item = QtWidgets.QListWidgetItem(model_name)
            self.predefined_list.addItem(item)

        predefined_layout.addWidget(self.predefined_list)
        predefined_layout.addStretch()
        predefined_box.setLayout(predefined_layout)

        # Palette 레이아웃 안에 Predefined Models를 추가 (Palette 밑에 위치)
        palette_layout.addWidget(predefined_box, 2)
        palette_layout.addStretch()
        palette_box.setLayout(palette_layout)

        # 외부 레이아웃에는 palette_box 하나만 추가
        layout.addWidget(palette_box, 1)

        # ---------------- Canvas ----------------
        canvas_box = QtWidgets.QGroupBox("Canvas")
        canvas_layout = QtWidgets.QVBoxLayout(canvas_box)
        self.scene = QtWidgets.QGraphicsScene()
        # pass DesignTab as parent so LayerItem/EdgeItem can reference this tab if needed
        self.scene.parent_tab = self  # Canvas에서 LayerItem 이동 시 참조

        self.view = CanvasView(self.scene, self)
        canvas_layout.addWidget(self.view)
        layout.addWidget(canvas_box, 3)

        # ---------------- Sequence & Controls ----------------
        right_box = QtWidgets.QGroupBox("Sequence & Controls")
        right_layout = QtWidgets.QVBoxLayout(right_box)
        self.sequence_list = QtWidgets.QListWidget()
        self.sequence_list.setDragDropMode(QtWidgets.QAbstractItemView.InternalMove)

        # Connect model signals (use a single handler that accepts *args)
        model = self.sequence_list.model()
        self.sequence_list.model().rowsMoved.connect(self.on_sequence_reordered)
        self.sequence_list.model().rowsMoved.connect(self.update_sequence_from_positions)

        model.rowsMoved.connect(self.on_sequence_reordered)
        model.rowsInserted.connect(self.on_sequence_reordered)
        model.rowsRemoved.connect(self.on_sequence_reordered)
        model.layoutChanged.connect(self.on_sequence_reordered)

        right_layout.addWidget(QtWidgets.QLabel("Ordered Layers"))
        right_layout.addWidget(self.sequence_list, 1)

        # Buttons
        self.btn_export = QtWidgets.QPushButton("Export PyTorch Code")
        self.btn_save = QtWidgets.QPushButton("Save Design (.json)")
        self.btn_load = QtWidgets.QPushButton("Load Design (.json)")
        self.btn_clear = QtWidgets.QPushButton("Clear Canvas")
        self.btn_connect = QtWidgets.QPushButton("Connect Layers")

        row1 = QtWidgets.QHBoxLayout()
        row1.addWidget(self.btn_export)
        row1.addWidget(self.btn_save)
        row2 = QtWidgets.QHBoxLayout()
        row2.addWidget(self.btn_load)
        row2.addWidget(self.btn_clear)
        row3 = QtWidgets.QHBoxLayout()
        row3.addWidget(self.btn_connect)

        right_layout.addLayout(row1)
        right_layout.addLayout(row2)
        right_layout.addLayout(row3)
        right_layout.addStretch()
        layout.addWidget(right_box, 2)

        # 시그널 연결
        self.sequence_list.itemClicked.connect(self._on_sequence_item_clicked)
        self.predefined_list.itemDoubleClicked.connect(self.add_predefined_model_to_canvas)
        self.btn_connect.clicked.connect(self.connect_layers_dialog)
        self.btn_clear.clicked.connect(self.clear_canvas)
        self.btn_save.clicked.connect(self.save_design)
        self.btn_load.clicked.connect(self.load_design)
        self.btn_export.clicked.connect(self.export_code)

    # ---------------- Layer Add/Edit ----------------
    def add_layer(self, layer_type, pos, params=None):
        if params is None:
            params = LAYER_TEMPLATES.get(layer_type, {}).get("params", {})
        self.layer_uid += 1
        uid = self.layer_uid
        item = LayerItem(layer_type, params, uid)
        item.setPos(pos)
        if not hasattr(item, "connections"):
            item.connections = []
        self.scene.addItem(item)
        self.layer_items[uid] = item

        li = QtWidgets.QListWidgetItem(f"{layer_type} #{uid}")
        li.setData(QtCore.Qt.UserRole, uid)
        self.sequence_list.addItem(li)

        self.auto_layout()
        self.update_connections()


    def _on_sequence_item_clicked(self, list_item):
        uid = list_item.data(QtCore.Qt.UserRole)
        if uid in self.layer_items:
            it = self.layer_items[uid]
            self.scene.clearSelection()
            it.setSelected(True)
            self.view.centerOn(it)

    # ---------------- Auto Layout ----------------
    def auto_layout(self):
        x_offset = 50; y_offset = 50; y_gap = 100
        for idx in range(self.sequence_list.count()):
            uid = self.sequence_list.item(idx).data(QtCore.Qt.UserRole)
            if uid in self.layer_items:
                self.layer_items[uid].setPos(x_offset, y_offset + idx * y_gap)

    # ---------------- Connections ----------------
    def connect_layers_dialog(self):
        items = [self.sequence_list.item(i) for i in range(self.sequence_list.count())]
        if len(items) < 2:
            QtWidgets.QMessageBox.warning(self, "Connection Failed", "레이어가 2개 이상이어야 합니다.")
            return

        # clear existing connections
        for layer in self.layer_items.values():
            layer.connections = []

        uids = [it.data(QtCore.Qt.UserRole) for it in items]
        for i in range(len(uids) - 1):
            src = self.layer_items[uids[i]]
            tgt = self.layer_items[uids[i + 1]]
            if tgt.uid not in src.connections:
                src.connections.append(tgt.uid)

        valid, msg = validate_network(self.layer_items, self.sequence_list)
        if not valid:
            QtWidgets.QMessageBox.warning(self, "Connection Failed", msg)
            return

        self.update_sequence_from_positions()
        self.btn_save.setEnabled(True)
        self.btn_export.setEnabled(True)
        QtWidgets.QMessageBox.information(self, "Connection Success", "레이어 연결이 완료되었습니다.")

    def update_connections(self):
        """현재 connections 정보를 바탕으로 Scene의 EdgeItem을 완전히 재생성"""
        # remove existing edges from scene
        for e in list(self.edges):
            try:
                self.scene.removeItem(e)
            except Exception:
                pass
        self.edges = []

        # create new edges based on connections
        for uid, item in self.layer_items.items():
            for tgt_uid in getattr(item, "connections", []) or []:
                if tgt_uid in self.layer_items:
                    tgt_item = self.layer_items[tgt_uid]
                    e = EdgeItem(item, tgt_item)
                    self.scene.addItem(e)
                    self.edges.append(e)

    def update_sequence_from_positions(self):
        # y좌표 기준으로 정렬 후 SequenceList 갱신
        items = sorted(self.layer_items.values(), key=lambda i: i.pos().y())
        self.sequence_list.clear()
        for item in items:
            li = QtWidgets.QListWidgetItem(f"{item.layer_type} #{item.uid}")
            li.setData(QtCore.Qt.UserRole, item.uid)
            self.sequence_list.addItem(li)
            
        uids = [self.sequence_list.item(i).data(QtCore.Qt.UserRole) for i in range(self.sequence_list.count())]
        print("Updated sequence:", uids)
        
        # 연결 갱신
        self.update_connections()
        self.layer_sequence = uids
        self.layer_sequence = [self.sequence_list.item(i).data(QtCore.Qt.UserRole) 
                            for i in range(self.sequence_list.count())]
        
    def update_sequence_connections_only(self):
        """SequenceList 순서를 기준으로 connections만 갱신 (Edge는 그대로)"""
        uids = [self.sequence_list.item(i).data(QtCore.Qt.UserRole) for i in range(self.sequence_list.count())]

        for layer in self.layer_items.values():
            layer.connections = []

        for i in range(len(uids) - 1):
            self.layer_items[uids[i]].connections = [uids[i + 1]]


    # unified handler for various model signals (drag/drop, layout change 등)
    def on_sequence_reordered(self, *args):
        uids = [self.sequence_list.item(i).data(QtCore.Qt.UserRole) for i in range(self.sequence_list.count())]

        # reset connections and rebuild according to list order
        for layer in self.layer_items.values():
            layer.connections = []

        for i in range(len(uids) - 1):
            self.layer_items[uids[i]].connections = [uids[i+1]]

        # rebuild edges
        self.update_connections()


    # ---------------- Export / Save / Load ----------------
    def export_code(self):
        QtWidgets.QApplication.processEvents()
        self.update_sequence_connections_only()  # 최신 connections 반영
        self.update_sequence_from_positions()     # this sets self.layer_sequence

        export_to_pytorch(self.layer_items, self.layer_sequence)

    def save_design(self):
        QtWidgets.QApplication.processEvents()
        self.update_sequence_connections_only()
        self.update_sequence_from_positions()
        save_design_json(self.layer_items, self.layer_sequence)

    def load_design(self):
        load_design_json(self)

    def clear_canvas(self):
        # remove scene items
        self.scene.clear()
        self.layer_items.clear()
        self.edges.clear()
        self.sequence_list.clear()

    # ---------------- Predefined 모델 추가 함수 ----------------
    def _expand_placeholder(self, layer_def):
        """플레이스홀더 모듈(ResidualBlock, Inception 등)을 표준 레이어 시퀀스로 전개해서 반환한다.
        전개할 수 없는 경우에는 원래 정의를 리스트로 감싸서 반환.
        """
        t = layer_def.get("type")
        params = layer_def.get("params", {})

        if t == "Inception":
            # Inception 모듈을 단일 시퀀스로 근사 (브랜치 병합은 지원하지 않으므로 순차적으로 배치)
            in_ch = params.get("in_channels", 192)
            return [
                {"type": "Conv2d", "params": {"in_channels": in_ch, "out_channels": params.get("out_1x1", 64), "kernel_size": 1}},
                {"type": "ReLU", "params": {}},

                {"type": "Conv2d", "params": {"in_channels": in_ch, "out_channels": params.get("out_3x3_reduce", 96), "kernel_size": 1}},
                {"type": "ReLU", "params": {}},
                {"type": "Conv2d", "params": {"in_channels": params.get("out_3x3_reduce", 96), "out_channels": params.get("out_3x3", 128), "kernel_size": 3, "padding": 1}},
                {"type": "ReLU", "params": {}},

                {"type": "Conv2d", "params": {"in_channels": in_ch, "out_channels": params.get("out_5x5_reduce", 16), "kernel_size": 1}},
                {"type": "ReLU", "params": {}},
                {"type": "Conv2d", "params": {"in_channels": params.get("out_5x5_reduce", 16), "out_channels": params.get("out_5x5", 32), "kernel_size": 5, "padding": 2}},
                {"type": "ReLU", "params": {}},

                {"type": "MaxPool2d", "params": {"kernel_size": 3, "stride": 1, "padding": 1}},
                {"type": "Conv2d", "params": {"in_channels": in_ch, "out_channels": params.get("out_pool_proj", 32), "kernel_size": 1}},
                {"type": "ReLU", "params": {}},
            ]

        if t == "ResidualBlock":
            # Residual block을 두 개의 conv-block 시퀀스로 전개 (skip-connection은 export 단계에서 처리 권장)
            in_ch = params.get("in_channels", 64)
            out_ch = params.get("out_channels", 64)
            stride = params.get("stride", 1)
            repeats = params.get("repeats", 1)
            seq = []
            for r in range(repeats):
                seq.extend([
                    {"type": "Conv2d", "params": {"in_channels": in_ch, "out_channels": out_ch, "kernel_size": 3, "stride": stride, "padding": 1}},
                    {"type": "BatchNorm2d", "params": {"num_features": out_ch}},
                    {"type": "ReLU", "params": {}},
                    {"type": "Conv2d", "params": {"in_channels": out_ch, "out_channels": out_ch, "kernel_size": 3, "stride": 1, "padding": 1}},
                    {"type": "BatchNorm2d", "params": {"num_features": out_ch}},
                    {"type": "ReLU", "params": {}},
                ])
                in_ch = out_ch
                stride = 1
            return seq

        # 기본: 변경 없음
        return [layer_def]

    def add_predefined_model_to_canvas(self, list_item):
        model_name = list_item.text()
        layers = self.PREDEFINED_MODELS.get(model_name, [])
        if not layers:
            QtWidgets.QMessageBox.warning(self, "Predefined Model", f"No template for {model_name}")
            return

        x_offset = 50
        y_offset = 50 + self.sequence_list.count() * 100

        # 각 정의를 전개(expand)하여 실제 레이어 시퀀스를 만든다
        expanded_layers = []
        for layer_def in layers:
            expanded = self._expand_placeholder(layer_def)
            expanded_layers.extend(expanded)

        for layer_def in expanded_layers:
            layer_type = layer_def.get("type")
            params = layer_def.get("params", {})

            # 만약 LAYER_TEMPLATES에 타입이 없다면, 기본 템플릿으로 빈 params 사용
            if layer_type not in LAYER_TEMPLATES:
                # 일부 레이어(Flatten, Dropout 등)는 템플릿에 없을 수 있으니 허용
                # LAYER_TEMPLATES가 필요로 하는 키가 있다면 export 시 에러가 날 수 있음
                pass

            self.layer_uid += 1
            uid = self.layer_uid
            item = LayerItem(layer_type, params, uid)
            item.setPos(x_offset, y_offset)
            if not hasattr(item, "connections"):
                item.connections = []
            self.scene.addItem(item)
            self.layer_items[uid] = item

            li = QtWidgets.QListWidgetItem(f"{layer_type} #{uid}")
            li.setData(QtCore.Qt.UserRole, uid)
            self.sequence_list.addItem(li)

            y_offset += 100  # 다음 레이어 아래로

        self.auto_layout()
        self.update_connections()