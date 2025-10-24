# tabs/settings_tab.py
from PyQt5 import QtWidgets, QtCore
from utils.theme_utils import apply_theme_to_window

class SettingsTab(QtWidgets.QWidget):
    theme_changed = QtCore.pyqtSignal(str, str)

    def __init__(self, parent=None):
        super().__init__(parent)
        self._init_settings()
        self._build_ui()
        self._load_saved_settings()

    def _init_settings(self):
        self.qsettings = QtCore.QSettings("MyCompany", "NetworkDesigner")

        # theme names only; styles are handled by apply_theme_to_window via .qss files
        self.themes = ["Light", "Dark", "Gray"]
        self.default_theme = "Dark"

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
        self.theme_combo.addItems(self.themes)
        self.theme_combo.currentTextChanged.connect(self.on_theme_selected)
        row.addWidget(QtWidgets.QLabel("Select theme:"))
        row.addWidget(self.theme_combo)
        theme_layout.addLayout(row)

        # Preview label
        self.preview_label = QtWidgets.QLabel(
            "Preview area — This text will show theme preview.\nButtons, inputs and lists are rendered here."
        )
        self.preview_label.setAlignment(QtCore.Qt.AlignCenter)
        self.preview_label.setMinimumHeight(120)
        self.preview_label.setFrameShape(QtWidgets.QFrame.Box)
        theme_layout.addWidget(self.preview_label)

        # Sample controls for preview
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

        info = QtWidgets.QLabel(
            "Theme changes affect widgets that accept stylesheet updates.\nIf parts of your app don't update, connect to the theme_changed signal to reapply styles."
        )
        info.setWordWrap(True)
        main_layout.addWidget(info)

    # -------------------- Slots / Actions --------------------
    def on_theme_selected(self, theme_name):
        """Preview only"""
        # apply preview to sample widgets via .qss
        apply_theme_to_window(self, theme_name)
        apply_theme_to_window(self.preview_label, theme_name)
        apply_theme_to_window(self.sample_btn, theme_name)
        apply_theme_to_window(self.sample_lineedit, theme_name)
        apply_theme_to_window(self.sample_list, theme_name)

    def on_apply(self):
        theme_name = self.theme_combo.currentText().lower()
        # apply to whole app
        apply_theme_to_window(self, theme_name)
        apply_theme_to_window(QtWidgets.QApplication.instance(), theme_name)

        # Footer update
        main_window = self.window()
        if hasattr(main_window, "status_bar"):
            main_window.status_bar.update_style(theme_name)

        # persist
        self.qsettings.setValue("theme/name", theme_name)
        QtWidgets.QMessageBox.information(self, "Theme Applied", f"Theme '{theme_name}' has been applied.")

    def on_save_and_close(self):
        self.on_apply()
        w = self.window()
        if isinstance(w, QtWidgets.QDialog):
            w.accept()
        else:
            self.hide()

    def on_reset(self):
        self.theme_combo.setCurrentText(self.default_theme)
        self.on_theme_selected(self.default_theme)

        main_window = self.window()
        if hasattr(main_window, "status_bar"):
            main_window.status_bar.update_style(self.default_theme)

        QtWidgets.QMessageBox.information(self, "Reset", f"Theme reset to '{self.default_theme}'.")

    # -------------------- Persistence --------------------
    def _load_saved_settings(self):
        name = self.qsettings.value("theme/name", self.default_theme)
        if name not in self.themes:
            name = self.default_theme

        idx = self.theme_combo.findText(name)
        if idx >= 0:
            self.theme_combo.setCurrentIndex(idx)
            self.on_theme_selected(name)

        # Apply whole app + Footer
        apply_theme_to_window(self, name)
        apply_theme_to_window(QtWidgets.QApplication.instance(), name)
        main_window = self.window()
        if hasattr(main_window, "status_bar"):
            main_window.status_bar.update_style(name)
