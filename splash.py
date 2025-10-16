import sys
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QLabel, QWidget, QVBoxLayout, QProgressBar
)
from PyQt5.QtCore import Qt, QTimer, pyqtSignal
from PyQt5.QtGui import QFont
from PyQt5.QtWidgets import QListWidget, QStackedWidget, QHBoxLayout, QWidget, QLabel, QVBoxLayout


class SplashScreen(QWidget):
    finished = pyqtSignal()

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Initializing")
        self._init_ui()
        self.showFullScreen()

        # Demo timer to fill progress; replace with real init logic if needed
        self._demo_val = 0
        self._timer = QTimer(self)
        self._timer.timeout.connect(self._tick)
        self._timer.start(50)  # adjust speed as needed

    def _init_ui(self):
        layout = QVBoxLayout(self)
        title = QLabel("Initializing...")
        title.setAlignment(Qt.AlignCenter)
        font = QFont()
        font.setPointSize(48)
        font.setBold(True)
        title.setFont(font)
        layout.addWidget(title)

        self.progress = QProgressBar()
        self.progress.setRange(0, 100)
        self.progress.setValue(0)
        self.progress.setFixedHeight(28)
        layout.addWidget(self.progress)

    def _tick(self):
        self._demo_val += 1
        self.progress.setValue(self._demo_val)
        if self._demo_val >= 100:
            self._timer.stop()
            # If you have real initialization work, do it here
            self.finished.emit()