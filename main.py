# Version: v1.6
# BlueFalcon OpenVPN Config Manager - Entry Point

import sys
import platform
from PyQt6.QtWidgets import QApplication, QMessageBox
from gui import MainWindow

def verify_windows_os():
    if platform.system() != "Windows":
        app = QApplication(sys.argv)
        QMessageBox.critical(None, "Incompatible OS", "This application requires a Windows operating system.")
        sys.exit(1)

if __name__ == "__main__":
    verify_windows_os()
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())