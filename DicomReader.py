# MAIN PROGRAM
import sys
import matplotlib
import signal

from PySide6.QtWidgets import QApplication
from App.mainwindow import MainWindow

matplotlib.use('Qt5Agg')

if __name__ == "__main__":
    signal.signal(signal.SIGINT, signal.SIG_DFL)
    app = QApplication(sys.argv)
    window = MainWindow()
    sys.exit(app.exec())
