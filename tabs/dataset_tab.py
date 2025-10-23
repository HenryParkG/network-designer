from PyQt5 import QtWidgets, QtCore

class DatasetTab(QtWidgets.QWidget):
    """데이터셋 관리 탭"""
    def __init__(self, parent_window=None):
        super().__init__()
        layout = QtWidgets.QVBoxLayout(self)
        layout.setContentsMargins(8, 8, 8, 8)

        # 더미 레이블
        label = QtWidgets.QLabel("Dataset Management")
        label.setAlignment(QtCore.Qt.AlignCenter)
        layout.addWidget(label)

        # 예: 데이터셋 파일 로드 버튼
        self.btn_load_dataset = QtWidgets.QPushButton("Load Dataset")
        layout.addWidget(self.btn_load_dataset)

        # 예: 데이터셋 정보 표시
        self.dataset_info = QtWidgets.QTextEdit()
        self.dataset_info.setReadOnly(True)
        layout.addWidget(self.dataset_info)

        # 버튼 클릭 더미
        self.btn_load_dataset.clicked.connect(self.load_dataset)

    def load_dataset(self):
        # 실제 로직은 나중에 구현
        self.dataset_info.append("Dataset loaded (dummy)")
