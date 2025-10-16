from PyQt5 import QtWidgets
from designer_window import DesignerWindow



def apply_theme(self, theme_name="dark"):
    qss_file = {
        "dark": "themes/dark_theme.qss",
        "light": "themes/light_theme.qss",
        "gray": "themes/gray_theme.qss"
    }.get(theme_name, "themes/dark_theme.qss")

    with open(qss_file, "r", encoding="utf-8") as f:
        self.setStyleSheet(f.read())

def main():
    app = QtWidgets.QApplication([])
    
    apply_theme(app, "dark")  # Apply the desired theme here

    win = DesignerWindow()
    win.show()
    app.exec_()

if __name__ == "__main__":
    main()
