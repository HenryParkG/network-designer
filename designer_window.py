from PyQt5 import QtWidgets, QtCore
from layers.layer_item import LayerItem
from layers.edge_item import EdgeItem
from layers.layers_config import LAYER_TEMPLATES
from canvas.canvas_view import CanvasView
from palette.palette_widget import PaletteListWidget
from utils.export_utils import export_to_pytorch
from utils.save_load_utils import save_design_json, load_design_json

class DesignerWindow(QtWidgets.QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("PyTorch NN Designer")
        self.resize(1300,700)
        self.layer_uid = 0
        self.layer_items = {}   # uid -> LayerItem
        self.edges = []

        central = QtWidgets.QWidget()
        self.setCentralWidget(central)
        h = QtWidgets.QHBoxLayout(central)
        h.setContentsMargins(8,8,8,8)

        # ---------------- Palette ----------------
        palette_box = QtWidgets.QGroupBox("Layer Palette")
        palette_layout = QtWidgets.QVBoxLayout(palette_box)
        self.palette_list = PaletteListWidget()
        palette_layout.addWidget(self.palette_list)
        palette_layout.addStretch()
        h.addWidget(palette_box, 1)

        # ---------------- Canvas ----------------
        canvas_box = QtWidgets.QGroupBox("Canvas")
        canvas_layout = QtWidgets.QVBoxLayout(canvas_box)
        self.scene = QtWidgets.QGraphicsScene()
        self.scene.parent_widget = self
        self.view = CanvasView(self.scene, self)
        canvas_layout.addWidget(self.view)
        h.addWidget(canvas_box, 3)

        # ---------------- Sequence & Controls ----------------
        right_box = QtWidgets.QGroupBox("Sequence & Controls")
        right_layout = QtWidgets.QVBoxLayout(right_box)
        self.sequence_list = QtWidgets.QListWidget()
        self.sequence_list.setDragDropMode(QtWidgets.QAbstractItemView.InternalMove)
        right_layout.addWidget(QtWidgets.QLabel("Ordered Layers"))
        right_layout.addWidget(self.sequence_list, 1)

        # Buttons
        btn_export = QtWidgets.QPushButton("Export PyTorch Code")
        btn_export.clicked.connect(self.export_code)
        btn_save = QtWidgets.QPushButton("Save Design (.json)")
        btn_save.clicked.connect(self.save_design)
        btn_load = QtWidgets.QPushButton("Load Design (.json)")
        btn_load.clicked.connect(self.load_design)
        btn_clear = QtWidgets.QPushButton("Clear Canvas")
        btn_clear.clicked.connect(self.clear_canvas)
        btn_connect = QtWidgets.QPushButton("Connect Layers")
        btn_connect.clicked.connect(self.connect_layers_dialog)

        row1 = QtWidgets.QHBoxLayout()
        row1.addWidget(btn_export)
        row1.addWidget(btn_save)
        row2 = QtWidgets.QHBoxLayout()
        row2.addWidget(btn_load)
        row2.addWidget(btn_clear)
        row3 = QtWidgets.QHBoxLayout()
        row3.addWidget(btn_connect)
        right_layout.addLayout(row1)
        right_layout.addLayout(row2)
        right_layout.addLayout(row3)
        right_layout.addStretch()
        h.addWidget(right_box, 2)

        self.sequence_list.itemClicked.connect(self._on_sequence_item_clicked)

    # ---------------- Layer Add/Edit ----------------
    def add_layer(self, layer_type, pos):
        self.layer_uid += 1
        uid = self.layer_uid
        params = LAYER_TEMPLATES[layer_type]["params"]
        item = LayerItem(layer_type, params, uid)
        item.setPos(pos)
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

    def update_sequence_from_positions(self):
        # Y 좌표 기준으로 시퀀스 갱신
        items = sorted(self.layer_items.values(), key=lambda i: i.pos().y())
        self.sequence_list.clear()
        for item in items:
            li = QtWidgets.QListWidgetItem(f"{item.layer_type} #{item.uid}")
            li.setData(QtCore.Qt.UserRole, item.uid)
            self.sequence_list.addItem(li)
        self.update_connections()

    # ---------------- Connections ----------------
    def connect_layers_dialog(self):
        items = [self.sequence_list.item(i) for i in range(self.sequence_list.count())]
        if len(items) < 2:
            return

        # 1. 기존 connections 초기화
        for layer in self.layer_items.values():
            layer.connections = []

        # 2. sequence_list 순서대로 connections 생성
        uids = [it.data(QtCore.Qt.UserRole) for it in items]
        for i in range(len(uids) - 1):
            src = self.layer_items[uids[i]]
            tgt = self.layer_items[uids[i + 1]]
            if tgt.uid not in src.connections:
                src.connections.append(tgt.uid)

        # 3. Edge 갱신
        self.update_connections()

    def update_connections(self):
    # 1. 기존 EdgeItem 제거
        for e in self.edges:
            self.scene.removeItem(e)
        self.edges = []

        # 2. LayerItem connections 기준으로 새 EdgeItem 생성
        for uid, item in self.layer_items.items():
            # connections 초기화 필요 시 uncomment
            # item.connections = []
            for tgt_uid in item.connections:
                if tgt_uid in self.layer_items:
                    e = EdgeItem(item, self.layer_items[tgt_uid])
                    self.scene.addItem(e)
                    self.edges.append(e)

    # ---------------- Export / Save / Load ----------------
    def export_code(self):
        export_to_pytorch(self.layer_items, self.sequence_list)

    def save_design(self):
        save_design_json(self.layer_items, self.sequence_list)

    def load_design(self):
        load_design_json(self)

    def clear_canvas(self):
        self.scene.clear()
        self.layer_items.clear()
        self.edges.clear()
        self.sequence_list.clear()
