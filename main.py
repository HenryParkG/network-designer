from PyQt5 import QtWidgets
from designer_window import DesignerWindow

def main():
    app = QtWidgets.QApplication([])
    win = DesignerWindow()
    win.show()
    app.exec_()

if __name__ == "__main__":
    main()
