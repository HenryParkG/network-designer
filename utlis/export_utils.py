from PyQt5 import QtWidgets
import torch.nn as nn
import torch

def export_to_pytorch(layer_items, sequence_list):
    code_lines = ["import torch","import torch.nn as nn","\nclass Net(nn.Module):",
                  "    def __init__(self):","        super(Net,self).__init__()"]
    for uid, item in layer_items.items():
        cls = item.layer_type
        params = item.params
        kv = [f"{k}={repr(v)}" for k,v in params.items()]
        code_lines.append(f"        self.l{uid} = nn.{cls}({', '.join(kv)})")

    code_lines.append("\n    def forward(self, x):")
    for i in range(sequence_list.count()):
        uid = sequence_list.item(i).data(QtCore.Qt.UserRole)
        code_lines.append(f"        x = self.l{uid}(x)")
    code_lines.append("        return x\n")
    code_lines.append("if __name__=='__main__':\n    model=Net()\n    y=model(torch.randn(1,128))\n    print(y.shape)")

    dlg = QtWidgets.QDialog()
    dlg.setWindowTitle("Exported PyTorch Code")
    dlg.resize(700,500)
    layout = QtWidgets.QVBoxLayout(dlg)
    te = QtWidgets.QPlainTextEdit()
    te.setPlainText("\n".join(code_lines))
    layout.addWidget(te)

    btns = QtWidgets.QDialogButtonBox(QtWidgets.QDialogButtonBox.Save|QtWidgets.QDialogButtonBox.Close)
    layout.addWidget(btns)
    def save_code():
        path,_ = QtWidgets.QFileDialog.getSaveFileName(None,"Save PyTorch code","model.py","Python files (*.py)")
        if path:
            with open(path,"w",encoding="utf-8") as f: f.write(te.toPlainText())
            QtWidgets.QMessageBox.information(None,"Saved",f"Saved to {path}")
    btns.accepted.connect(save_code)
    btns.rejected.connect(dlg.reject)
    dlg.exec_()
