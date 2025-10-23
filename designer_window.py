# Description: Main window for the PyTorch NN Designer application with tabbed interface.
from PyQt5 import QtWidgets, QtCore
from layers.layer_item import LayerItem
from layers.edge_item import EdgeItem
from layers.layers_config import LAYER_TEMPLATES
from ui.canvas.canvas_view import CanvasView
from ui.palette.palette_widget import PaletteListWidget
from utils.export_utils import export_to_pytorch
from utils.save_load_utils import save_design_json, load_design_json

# tabs 모듈 임포트
from ui.tabs.design_tab import DesignTab
from ui.tabs.dataset_tab import DatasetTab
from ui.tabs.config_tab import ConfigTab 
from ui.tabs.setting_tab import SettingsTab 

# -------------------- 메인 윈도우 --------------------
class DesignerWindow(QtWidgets.QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("PyTorch NN Designer (Tabbed)")
        self.resize(1400, 800)

        self.layer_uid = 0
        self.layer_items = {}
        self.edges = []

        # 중앙 위젯: 탭 위젯
        self.tabs = QtWidgets.QTabWidget()
        self.setCentralWidget(self.tabs)

        # 1️⃣ Network Design 탭
        self.design_tab = DesignTab(self)
        self.tabs.addTab(self.design_tab, "Network Design Tab")

        # 2️⃣ Dataset 탭 (미리 자리만 만들어둠)
        self.dataset_tab = DatasetTab(self)
        self.tabs.addTab(self.dataset_tab, "Dataset Tab")

        # 3️⃣ Training Config 탭 (자리만)
        self.config_tab = ConfigTab(self)
        self.tabs.addTab(self.config_tab, "Config Tab")

        # 4 Setting 탭 (자리만)
        self.setting_tab = SettingsTab(self)
        self.tabs.addTab(self.setting_tab, "Setting Tab")
        
        # 참조를 DesignTab 내부 위젯과 연결
        self.scene = self.design_tab.scene
        self.sequence_list = self.design_tab.sequence_list
        self.palette_list = self.design_tab.palette_list
        self.view = self.design_tab.view
        
        # ---- 상태 표시줄 (Footer) ----
        self.status_bar = QtWidgets.QStatusBar()
        self.status_bar.setStyleSheet("""
            QStatusBar {
                background-color: #1e1e1e;
                color: #ffffff;
                padding: 4px;
                border-top: 1px solid #3a3a3a;
            }
        """)
        self.setStatusBar(self.status_bar)

        # ---- Footer 텍스트 업데이트 ----
        self.status_bar.showMessage("Ready")
        
        
