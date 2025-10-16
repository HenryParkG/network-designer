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


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Neural Network Designer")
        self._init_ui()
        # open main window full screen
        self.showFullScreen()

    def _init_ui(self):
        central = QWidget()
        layout = QVBoxLayout(central)
        title = QLabel("Neural Network Designer")
        title.setAlignment(Qt.AlignCenter)
        font = QFont()
        font.setPointSize(48)
        font.setBold(True)
        title.setFont(font)
        layout.addWidget(title)
        layout.addStretch()
        self.setCentralWidget(central)

    def keyPressEvent(self, event):
        if event.key() == Qt.Key_Escape:
            self.close()
        else:
            super().keyPressEvent(event)


if __name__ == "__main__":
    app = QApplication(sys.argv)

    splash = SplashScreen()

    # Keep reference to main window to avoid GC
    def open_main():
        app.main_window = MainWindow()
        # show how you want the main window; example: normal window
        app.main_window.show()
        # or full screen: app.main_window.showFullScreen()
        splash.close()

    splash.finished.connect(open_main)

    # add a second slot to finish setup (will run after open_main since it was connected earlier)
    def _setup_left_nav():

        mw = app.main_window
        if mw is None:
            return

        old_central = mw.centralWidget()

        # Stacked pages: keep existing central as first page
        stacked = QStackedWidget()
        stacked.addWidget(old_central)

        # Additional placeholder pages
        def make_page(text):
            p = QWidget()
            v = QVBoxLayout(p)
            lbl = QLabel(text)
            lbl.setAlignment(Qt.AlignCenter)
            v.addWidget(lbl)
            v.addStretch()
            return p

        stacked.addWidget(make_page("Load Datasets"))
        stacked.addWidget(make_page("Training"))
        stacked.addWidget(make_page("Settings"))

        # Left navigation list
        nav = QListWidget()
        nav.addItems(["Neural Network Creation", "Load Datasets", "Training", "Settings"])
        nav.setFixedWidth(220)
        nav.setCurrentRow(0)
        nav.currentRowChanged.connect(stacked.setCurrentIndex)

        # Combine nav + stacked into a new central widget
        container = QWidget()
        h = QHBoxLayout(container)
        h.setContentsMargins(0, 0, 0, 0)
        h.addWidget(nav)
        h.addWidget(stacked, 1)

        mw.setCentralWidget(container)

    splash.finished.connect(_setup_left_nav)

    sys.exit(app.exec_())