from PyQt5 import QtWidgets, QtCore
import torch.nn as nn
import torch

def export_to_pytorch(layer_items, sequence):
    """
    Export PyTorch code using the user-visible order.
    - layer_items: dict {uid: LayerItem}
    - sequence: either a QListWidget (UI) OR a Python list of uids (preferred)
    """
    # --- normalize sequence to a plain list of uids ---
    if isinstance(sequence, QtWidgets.QListWidget):
        seq = [sequence.item(i).data(QtCore.Qt.UserRole) for i in range(sequence.count())]
    elif isinstance(sequence, list):
        seq = list(sequence)
    else:
        # try to coerce an iterable
        try:
            seq = list(sequence)
        except Exception:
            QtWidgets.QMessageBox.warning(None, "Export Error", "Invalid sequence argument for export.")
            return

    if not seq:
        QtWidgets.QMessageBox.warning(None, "Export Error", "레이어 시퀀스가 비어있습니다. 먼저 레이어를 추가하세요.")
        return

    # --- header / imports ---
    code_lines = [
        "import torch",
        "import torch.nn as nn",
        "",
        "# NOTE: If you use custom modules (ResidualBlock, Inception, ...),",
        "# make sure to import them here, e.g.:",
        "# from layers.custom_modules import ResidualBlock, Inception",
        "",
        "class Net(nn.Module):",
        "    def __init__(self):",
        "        super(Net, self).__init__()",
    ]

    # --- create layer attributes in the same order as seq (important) ---
    for uid in seq:
        if uid not in layer_items:
            # skip missing uids but warn in comment
            code_lines.append(f"        # WARNING: layer uid {uid} not found (skipped)")
            continue
        item = layer_items[uid]
        cls = item.layer_type
        params = item.params or {}
        # represent parameters safely
        kv = [f"{k}={repr(v)}" for k, v in params.items()]
        code_lines.append(f"        self.l{uid} = nn.{cls}({', '.join(kv)})")

    # --- forward ---
    code_lines.append("")
    code_lines.append("    def forward(self, x):")
    for uid in seq:
        if uid not in layer_items:
            code_lines.append(f"        # skipped missing layer {uid}")
            continue
        code_lines.append(f"        x = self.l{uid}(x)")
    code_lines.append("        return x")
    code_lines.append("")

    # --- simple runtime test (estimate input shape from first layer) ---
    # Try to build a sensible input tensor for a quick smoke test
    first_item = layer_items.get(seq[0], None)
    if first_item:
        if "in_channels" in (first_item.params or {}):
            c = first_item.params.get("in_channels", 3)
            # common default image size
            test_shape = f"(1, {c}, 224, 224)"
            test_call = f"y = model(torch.randn{test_shape})"
        elif "in_features" in (first_item.params or {}):
            f = first_item.params.get("in_features", 128)
            test_shape = f"(1, {f})"
            test_call = f"y = model(torch.randn{test_shape})"
        else:
            test_call = "y = model(torch.randn(1, 128))"
    else:
        test_call = "y = model(torch.randn(1, 128))"

    code_lines.append("if __name__ == '__main__':")
    code_lines.append("    model = Net()")
    code_lines.append(f"    {test_call}")
    code_lines.append("    print(y.shape)")

    # --- dialog to show & save code ---
    dlg = QtWidgets.QDialog()
    dlg.setWindowTitle("Exported PyTorch Code")
    dlg.resize(800, 600)
    layout = QtWidgets.QVBoxLayout(dlg)
    te = QtWidgets.QPlainTextEdit()
    te.setPlainText("\n".join(code_lines))
    layout.addWidget(te)

    btns = QtWidgets.QDialogButtonBox(QtWidgets.QDialogButtonBox.Save | QtWidgets.QDialogButtonBox.Close)
    layout.addWidget(btns)

    def save_code():
        path, _ = QtWidgets.QFileDialog.getSaveFileName(None, "Save PyTorch code", "model.py", "Python files (*.py)")
        if path:
            with open(path, "w", encoding="utf-8") as f:
                f.write(te.toPlainText())
            QtWidgets.QMessageBox.information(None, "Saved", f"Saved to {path}")

    btns.accepted.connect(save_code)
    btns.rejected.connect(dlg.reject)
    dlg.exec_()
