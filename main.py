# Description: Main application file to run the PyQt5 GUI with theming support.
from PyQt5 import QtWidgets
from designer_window import DesignerWindow

from utils.theme_utils import apply_theme

# -------------------- 메인 애플리케이션 --------------------
def main():
    app = QtWidgets.QApplication([])
    
    apply_theme(app, "dark")  # Apply the desired theme here

    win = DesignerWindow()
    win.show()
    app.exec_()

if __name__ == "__main__":
    main()
