# theme_utils.py
from PyQt5 import QtWidgets

def apply_theme(app: QtWidgets.QApplication, theme_name="dark"):
    qss_file = {
        "dark": "data/themes/dark_theme.qss",
        "light": "data/themes/light_theme.qss",
        "gray": "data/themes/gray_theme.qss"
    }.get(theme_name, "data/themes/dark_theme.qss")

    with open(qss_file, "r", encoding="utf-8") as f:
        app.setStyleSheet(f.read())