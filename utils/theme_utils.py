# theme_utils.py
from PyQt5 import QtWidgets

def apply_theme_to_window(window, theme_name="dark"):
    """QMainWindow 같은 윈도우 전체에 테마 적용"""
    qss_file = {
        "dark": "data/themes/dark_theme.qss",
        "light": "data/themes/light_theme.qss",
        "gray": "data/themes/gray_theme.qss"
    }.get(theme_name, "data/themes/dark_theme.qss")

    try:
        with open(qss_file, "r", encoding="utf-8") as f:
            window.setStyleSheet(f.read())
    except FileNotFoundError:
        print(f"[apply_theme_to_window] QSS 파일 '{qss_file}' 없음")

    # Footer가 존재하면 스타일 동기화
    if hasattr(window, "status_bar") and window.status_bar is not None:
        window.status_bar.update_style(theme_name)


def apply_theme_to_widget(widget, theme_name="dark"):
    """개별 QWidget에 테마 적용"""
    qss_file = {
        "dark": "data/themes/dark_theme.qss",
        "light": "data/themes/light_theme.qss",
        "gray": "data/themes/gray_theme.qss"
    }.get(theme_name, "data/themes/dark_theme.qss")

    try:
        with open(qss_file, "r", encoding="utf-8") as f:
            widget.setStyleSheet(f.read())
    except FileNotFoundError:
        print(f"[apply_theme_to_widget] QSS 파일 '{qss_file}' 없음")
