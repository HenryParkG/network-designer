from PyQt5 import QtWidgets, QtCore
from layers.layer_item import LayerItem
from layers.edge_item import EdgeItem
from layers.layers_config import LAYER_TEMPLATES
from canvas.canvas_view import CanvasView
from palette.palette_widget import PaletteListWidget
from utils.export_utils import export_to_pytorch
from utils.save_load_utils import save_design_json, load_design_json
from utils.validate_network import validate_network

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
        self.btn_export = QtWidgets.QPushButton("Export PyTorch Code")
        self.btn_export.clicked.connect(self.export_code)
        self.btn_save = QtWidgets.QPushButton("Save Design (.json)")
        self.btn_save.clicked.connect(self.save_design)
        self.btn_load = QtWidgets.QPushButton("Load Design (.json)")
        self.btn_load.clicked.connect(self.load_design)
        self.btn_clear = QtWidgets.QPushButton("Clear Canvas")
        self.btn_clear.clicked.connect(self.clear_canvas)
        self.btn_connect = QtWidgets.QPushButton("Connect Layers")
        self.btn_connect.clicked.connect(self.connect_layers)

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
        h.addWidget(right_box, 2)

        self.btn_export.setEnabled(False)
        self.btn_save.setEnabled(False)
        self.btn_connect.setEnabled(True)

        self.sequence_list.itemClicked.connect(self._on_sequence_item_clicked)
        
        # CanvasView 생성 및 속성으로 저장
        self.canvas = CanvasView()
        self.setCentralWidget(self.canvas)

        # Scene에서 DesignerWindow 참조 가능하게
        self.canvas.scene().parent_widget = self

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
        # Y 좌표 기준으로 정렬
        items = sorted(self.layer_items.values(), key=lambda i: i.pos().y())
        self.sequence_list.clear()
        for item in items:
            li = QtWidgets.QListWidgetItem(f"{item.layer_type} #{item.uid}")
            li.setData(QtCore.Qt.UserRole, item.uid)
            self.sequence_list.addItem(li)
        self.update_connections()  # Edge 갱신

    # ---------------- Connections ----------------
    def connect_layers(self):
            # Canvas에서 레이어 간 연결 수행
            self.create_connections_from_sequence()

            # 연결 검증
            valid, msg = validate_network(self.layer_items, self.sequence_list)
            if not valid:
                QtWidgets.QMessageBox.warning(self, "Connection Failed", msg)
                return
            
            # 연결 성공 → Save / Export 버튼 활성화
            self.btn_save.setEnabled(True)
            self.btn_export.setEnabled(True)
            QtWidgets.QMessageBox.information(self, "Connection Success", "레이어 연결이 완료되었습니다.")

    def create_connections_from_sequence(self):
        items = [self.sequence_list.item(i) for i in range(self.sequence_list.count())]
        if len(items) < 2:
            return

        # 기존 connections 초기화
        for layer in self.layer_items.values():
            layer.connections = []

        for i in range(len(items) - 1):
            src_uid = items[i].data(QtCore.Qt.UserRole)
            tgt_uid = items[i+1].data(QtCore.Qt.UserRole)
            src_item = self.layer_items[src_uid]
            tgt_item = self.layer_items[tgt_uid]

            # 연결 갱신
            src_item.connections.append(tgt_uid)

            # Canvas Edge 생성
            self.canvas.add_edge(src_item, tgt_item)
            
    def update_connections(self):
        for e in self.edges: self.scene.removeItem(e)
        self.edges = []
        for uid, item in self.layer_items.items():
            for tgt_uid in item.connections:
                if tgt_uid in self.layer_items:
                    e = EdgeItem(item, self.layer_items[tgt_uid])
                    self.scene.addItem(e)
                    self.edges.append(e)

    # ---------------- Export / Save / Load ----------------
    def export_code(self):
        export_to_pytorch(self.layer_items, self.sequence_list)

    def save_design(self):
        # Save 클릭 시 재검증
        valid, msg = validate_network(self.layer_items, self.sequence_list)
        if not valid:
            QtWidgets.QMessageBox.warning(self, "Validation Failed", msg)
            return
        save_design_json(self.layer_items, self.sequence_list)
        QtWidgets.QMessageBox.information(self, "Saved", "신경망 구조가 저장되었습니다.")


    def load_design(self):
        load_design_json(self)

    def clear_canvas(self):
        self.scene.clear()
        self.layer_items.clear()
        self.edges.clear()
        self.sequence_list.clear()


    def on_canvas_changed(self):
        """
        Canvas에서 레이어 이동/연결 변경 시 호출
        Save / Export 버튼 비활성화
        """
        self.btn_save.setEnabled(False)
        self.btn_export.setEnabled(False)
        