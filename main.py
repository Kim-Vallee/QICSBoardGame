import sys

from PyQt5 import QtWidgets

from src.QICS_BG.ui_advanced import UiMainWindow

if __name__ == '__main__':
    app = QtWidgets.QApplication(sys.argv)
    win = UiMainWindow()
    win.show()
    sys.exit(app.exec_())
