# tabs/design_tab.py
from PyQt5 import QtWidgets, QtCore
from palette.palette_widget import PaletteListWidget
from canvas.canvas_view import CanvasView
from layers.layer_item import LayerItem
from layers.edge_item import EdgeItem
from layers.layers_config import LAYER_TEMPLATES
from utils.export_utils import export_to_pytorch
from utils.save_load_utils import save_design_json, load_design_json
from utils.validate_network import validate_network


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

        # ---------------- Palette ----------------
        palette_box = QtWidgets.QGroupBox("Layer Palette")
        palette_layout = QtWidgets.QVBoxLayout(palette_box)
        self.palette_list = PaletteListWidget()
        palette_layout.addWidget(self.palette_list)
        palette_layout.addStretch()
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
        self.btn_connect.clicked.connect(self.connect_layers_dialog)
        self.btn_clear.clicked.connect(self.clear_canvas)
        self.btn_save.clicked.connect(self.save_design)
        self.btn_load.clicked.connect(self.load_design)
        self.btn_export.clicked.connect(self.export_code)

    # ---------------- Layer Add/Edit ----------------
    def add_layer(self, layer_type, pos):
        """팔레트에서 드롭될 때 호출되는 레이어 추가 함수"""
        # validate template
        if layer_type not in LAYER_TEMPLATES:
            QtWidgets.QMessageBox.warning(self, "Add Layer", f"Unknown layer type: {layer_type}")
            return

        self.layer_uid += 1
        uid = self.layer_uid
        params = LAYER_TEMPLATES[layer_type].get("params", {})
        item = LayerItem(layer_type, params, uid)
        item.setPos(pos)
        # make sure item has connections attr
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

        self.update_connections()
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

        # 연결 갱신
        self.update_connections()


    # unified handler for various model signals (drag/drop, layout change 등)
    def on_sequence_reordered(self, *args):
        """
        rowsMoved / rowsInserted / rowsRemoved / layoutChanged 등에서 호출됩니다.
        *args를 받도록 해서 시그널 시그니처 차이를 무시합니다.
        """
        # ensure sequence list order becomes authoritative
        uids = []
        for i in range(self.sequence_list.count()):
            data = self.sequence_list.item(i).data(QtCore.Qt.UserRole)
            try:
                uids.append(int(data))
            except Exception:
                uids.append(data)

        # reset connections and rebuild according to list order
        for layer in self.layer_items.values():
            layer.connections = []

        for i in range(len(uids) - 1):
            if uids[i] in self.layer_items and uids[i+1] in self.layer_items:
                self.layer_items[uids[i]].connections = [uids[i+1]]

        # rebuild edges
        self.update_connections()

    # ---------------- Export / Save / Load ----------------
    def export_code(self):
        export_to_pytorch(self.layer_items, self.sequence_list)

    def save_design(self):
        save_design_json(self.layer_items, self.sequence_list)

    def load_design(self):
        load_design_json(self)

    def clear_canvas(self):
        # remove scene items
        self.scene.clear()
        self.layer_items.clear()
        self.edges.clear()
        self.sequence_list.clear()
