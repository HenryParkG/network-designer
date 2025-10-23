# Description: Main application file to run the PyQt5 GUI with theming support.
from PyQt5 import QtWidgets
from designer_window import DesignerWindow

# 테마 적용 함수
def apply_theme(self, theme_name="dark"):
    qss_file = {
        "dark": "data/themes/dark_theme.qss",
        "light": "data/themes/light_theme.qss",
        "gray": "data/themes/gray_theme.qss"
    }.get(theme_name, "themes/dark_theme.qss")

    with open(qss_file, "r", encoding="utf-8") as f:
        self.setStyleSheet(f.read())

# -------------------- 메인 애플리케이션 --------------------
def main():
    app = QtWidgets.QApplication([])
    
    apply_theme(app, "dark")  # Apply the desired theme here

    win = DesignerWindow()
    win.show()
    app.exec_()

if __name__ == "__main__":
    main()
