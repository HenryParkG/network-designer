# tabs/settings_tab.py
from PyQt5 import QtWidgets, QtCore, QtGui
from utils.theme_utils import apply_theme

class SettingsTab(QtWidgets.QWidget):
    """
    Settings tab for the application.
    - Provides theme selection (Light / Dark / Solarized)
    - Emits theme_changed(theme_name: str, stylesheet: str) when Apply is pressed
    - Persists last chosen theme using QSettings
    """

    theme_changed = QtCore.pyqtSignal(str, str)

    def __init__(self, parent=None):
        super().__init__(parent)
        self._init_settings()
        self._build_ui()
        self._load_saved_settings()

    def _init_settings(self):
        # QSettings (organization, application) - adjust names if desired
        self.qsettings = QtCore.QSettings("MyCompany", "NetworkDesigner")

        # Predefined themes (simple stylesheets). You can extend these or load from files.
        self.themes = {
            "Light": self._light_stylesheet(),
            "Dark": self._dark_stylesheet(),
            "Solarized": self._solarized_stylesheet(),
        }
        # default theme name
        self.default_theme = "Light"

    def _build_ui(self):
        main_layout = QtWidgets.QVBoxLayout(self)

        header = QtWidgets.QLabel("<b>Application Settings</b>")
        header.setAlignment(QtCore.Qt.AlignLeft)
        main_layout.addWidget(header)

        # Theme selection group
        theme_group = QtWidgets.QGroupBox("Theme")
        theme_layout = QtWidgets.QVBoxLayout(theme_group)

        row = QtWidgets.QHBoxLayout()
        self.theme_combo = QtWidgets.QComboBox()
        self.theme_combo.addItems(list(self.themes.keys()))
        self.theme_combo.currentTextChanged.connect(self.on_theme_selected)
        row.addWidget(QtWidgets.QLabel("Select theme:"))
        row.addWidget(self.theme_combo)
        theme_layout.addLayout(row)

        # Preview widget
        self.preview_label = QtWidgets.QLabel("Preview area — This text will show theme preview.\nButtons, inputs and lists are rendered here.")
        self.preview_label.setAlignment(QtCore.Qt.AlignCenter)
        self.preview_label.setMinimumHeight(120)
        self.preview_label.setFrameShape(QtWidgets.QFrame.Box)
        theme_layout.addWidget(self.preview_label)

        # sample controls on the right to show more preview elements
        preview_controls = QtWidgets.QWidget()
        pc_layout = QtWidgets.QHBoxLayout(preview_controls)
        self.sample_btn = QtWidgets.QPushButton("Button")
        self.sample_lineedit = QtWidgets.QLineEdit("Text input")
        self.sample_list = QtWidgets.QListWidget()
        for v in ("Item A", "Item B", "Item C"):
            self.sample_list.addItem(v)
        pc_layout.addWidget(self.sample_btn)
        pc_layout.addWidget(self.sample_lineedit)
        pc_layout.addWidget(self.sample_list)
        theme_layout.addWidget(preview_controls)

        # Buttons: Apply / Reset / Save
        btn_row = QtWidgets.QHBoxLayout()
        self.btn_apply = QtWidgets.QPushButton("Apply")
        self.btn_save = QtWidgets.QPushButton("Save & Close")
        self.btn_reset = QtWidgets.QPushButton("Reset to Default")
        btn_row.addWidget(self.btn_apply)
        btn_row.addWidget(self.btn_save)
        btn_row.addWidget(self.btn_reset)
        theme_layout.addLayout(btn_row)

        # Connect buttons
        self.btn_apply.clicked.connect(self.on_apply)
        self.btn_save.clicked.connect(self.on_save_and_close)
        self.btn_reset.clicked.connect(self.on_reset)

        main_layout.addWidget(theme_group)
        main_layout.addStretch()

        # status/info
        info = QtWidgets.QLabel("Theme changes affect widgets that accept stylesheet updates.\nIf parts of your app don't update, connect to the theme_changed signal to reapply styles.")
        info.setWordWrap(True)
        main_layout.addWidget(info)

    # -------------------- Stylesheets --------------------
    def _light_stylesheet(self):
        return """
/* Light theme */
QWidget {
    background: #F7F7F7;
    color: #222222;
    font-family: Arial, Helvetica, sans-serif;
    font-size: 11pt;
}
QPushButton {
    background: #E0E0E0;
    border: 1px solid #BDBDBD;
    padding: 6px;
}
QPushButton:hover { background: #D6D6D6; }
QLineEdit, QTextEdit, QPlainTextEdit {
    background: #FFFFFF;
    border: 1px solid #CFCFCF;
    padding: 4px;
}
QListWidget {
    background: #FFFFFF;
    border: 1px solid #CFCFCF;
}
QGroupBox {
    border: 1px solid #DADADA;
    margin-top: 6px;
}
"""

    def _dark_stylesheet(self):
        return """
/* Dark theme */
QWidget {
    background: #2B2B2B;
    color: #EAEAEA;
    font-family: Arial, Helvetica, sans-serif;
    font-size: 11pt;
}
QPushButton {
    background: #3A3A3A;
    border: 1px solid #555555;
    padding: 6px;
}
QPushButton:hover { background: #4A4A4A; }
QLineEdit, QTextEdit, QPlainTextEdit {
    background: #333333;
    border: 1px solid #4A4A4A;
    padding: 4px;
}
QListWidget {
    background: #333333;
    border: 1px solid #4A4A4A;
}
QGroupBox {
    border: 1px solid #444444;
    margin-top: 6px;
}
"""

    def _solarized_stylesheet(self):
        # a light solarized-like palette
        return """
/* Solarized-ish */
QWidget {
    background: #FDF6E3;
    color: #073642;
    font-family: "Segoe UI", Arial, sans-serif;
    font-size: 11pt;
}
QPushButton {
    background: #EEE8D5;
    border: 1px solid #93A1A1;
    padding: 6px;
}
QPushButton:hover { background: #E6DDC8; }
QLineEdit, QTextEdit, QPlainTextEdit {
    background: #FFFDF6;
    border: 1px solid #93A1A1;
    padding: 4px;
}
QListWidget {
    background: #FFFDF6;
    border: 1px solid #93A1A1;
}
QGroupBox {
    border: 1px solid #93A1A1;
    margin-top: 6px;
}
"""

    # -------------------- Slots / Actions --------------------
    def on_theme_selected(self, theme_name):
        """When user selects a theme from combo -> update preview only"""
        ss = self.themes.get(theme_name, "")
        # apply stylesheet to preview widgets (not whole app)
        self.preview_label.setStyleSheet(ss)
        self.sample_btn.setStyleSheet(ss)
        self.sample_lineedit.setStyleSheet(ss)
        self.sample_list.setStyleSheet(ss)

    # settings_tab.py 내부
    def on_apply(self):
        theme_name = self.theme_combo.currentText().lower()  # "dark", "light", "gray"
        
        # 앱 전체에 적용
        apply_theme(QtWidgets.QApplication.instance(), theme_name)

        # QSettings 저장
        self.qsettings.setValue("theme/name", theme_name)
        QtWidgets.QMessageBox.information(self, "Theme Applied", f"Theme '{theme_name}' has been applied.")
        
        
    def on_save_and_close(self):
        """Apply and close parent settings tab/dialog if possible"""
        self.on_apply()
        # try to close parent dialog or widget that contains this tab
        w = self.window()
        # if it's a QDialog, accept; otherwise just close the window if it's a dialog-like
        if isinstance(w, QtWidgets.QDialog):
            w.accept()
        else:
            # hide or emit a signal — we'll just hide for safety
            self.hide()

    def on_reset(self):
        """Reset to default theme (does not close)"""
        self.theme_combo.setCurrentText(self.default_theme)
        self.on_theme_selected(self.default_theme)
        QtWidgets.QMessageBox.information(self, "Reset", f"Theme reset to '{self.default_theme}'.")

    # -------------------- Persistence --------------------
    def _load_saved_settings(self):
        name = self.qsettings.value("theme/name", self.default_theme)
        if name not in self.themes:
            name = self.default_theme
        # set combo silently then apply preview
        idx = self.theme_combo.findText(name)
        if idx >= 0:
            self.theme_combo.setCurrentIndex(idx)
            self.on_theme_selected(name)

    # convenience: apply stylesheet immediately to whole app (helper)
    def apply_theme_to_app(self, theme_name):
        """
        Convenience helper -- apply saved theme to qApp.
        Usage: settings_tab.apply_theme_to_app(name)
        """
        ss = self.themes.get(theme_name, "")
        QtWidgets.QApplication.instance().setStyleSheet(ss)
        # persist
        self.qsettings.setValue("theme/name", theme_name)

