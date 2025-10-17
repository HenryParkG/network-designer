from PyQt5 import QtWidgets, QtCore

class ConfigTab(QtWidgets.QWidget):
    """모델 설정/하이퍼파라미터 탭"""
    def __init__(self):
        super().__init__()
        layout = QtWidgets.QVBoxLayout(self)
        layout.setContentsMargins(8, 8, 8, 8)

        # 더미 레이블
        label = QtWidgets.QLabel("Configuration / Hyperparameters")
        label.setAlignment(QtCore.Qt.AlignCenter)
        layout.addWidget(label)

        # 예: 학습률 입력
        lr_layout = QtWidgets.QHBoxLayout()
        lr_layout.addWidget(QtWidgets.QLabel("Learning Rate:"))
        self.input_lr = QtWidgets.QLineEdit("0.001")
        lr_layout.addWidget(self.input_lr)
        layout.addLayout(lr_layout)

        # 예: Epochs 입력
        epoch_layout = QtWidgets.QHBoxLayout()
        epoch_layout.addWidget(QtWidgets.QLabel("Epochs:"))
        self.input_epochs = QtWidgets.QLineEdit("10")
        epoch_layout.addWidget(self.input_epochs)
        layout.addLayout(epoch_layout)

        # 예: 저장 버튼
        self.btn_save_config = QtWidgets.QPushButton("Save Config")
        layout.addWidget(self.btn_save_config)
        self.btn_save_config.clicked.connect(self.save_config)

        # 예: 상태 표시
        self.status = QtWidgets.QLabel("")
        layout.addWidget(self.status)

    def save_config(self):
        lr = self.input_lr.text()
        epochs = self.input_epochs.text()
        self.status.setText(f"Config saved: lr={lr}, epochs={epochs}")
