from PyQt5 import QtWidgets
from utils.theme_utils import apply_theme_to_widget

class Footer(QtWidgets.QStatusBar):
    """
    Footer 컴포넌트 (상태 표시줄)
    - 앱 테마와 동기화
    - 메시지 표시 지원
    """
    def __init__(self, parent=None):
        super().__init__(parent)
        self.current_theme = "dark"
        self.setFixedHeight(24)
        self.showMessage("Ready")
        self.update_style(self.current_theme)

    def update_style(self, theme):
        """테마에 맞춰 스타일시트 적용"""
        self.current_theme = theme

        apply_theme_to_widget(self, theme_name=theme)

        # self.setStyleSheet(style)

    def show_temp_message(self, text, timeout=3000):
        """일시적 메시지 표시"""
        self.showMessage(text, timeout)
