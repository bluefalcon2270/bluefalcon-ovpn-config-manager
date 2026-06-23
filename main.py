# Version: v2.0
# BlueFalcon OpenVPN Config Manager - Entry Point

import sys
import platform
import ctypes
from PyQt6.QtWidgets import QApplication, QMessageBox
from gui import MainWindow

def verify_windows_os():
    if platform.system() != "Windows":
        app = QApplication(sys.argv)
        QMessageBox.critical(None, "Incompatible OS", "This application requires a Windows operating system.")
        sys.exit(1)
        
    # Fix for Windows Taskbar Icon grouping
    try:
        app_id = 'bluefalcon.vpnmanager.2.0'
        ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID(app_id)
    except Exception:
        pass

if __name__ == "__main__":
    verify_windows_os()
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())