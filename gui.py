# Version: v2.0
# BlueFalcon OpenVPN Config Manager - GUI Frontend

import logging
from logging.handlers import RotatingFileHandler
from pathlib import Path
from PyQt6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
    QLineEdit, QPushButton, QTextEdit, QMessageBox, QGridLayout, 
    QTableWidget, QTableWidgetItem, QHeaderView, QAbstractItemView, 
    QDialog, QStyle, QStyleOptionButton
)
from PyQt6.QtGui import QIcon
from PyQt6.QtCore import Qt, pyqtSignal, QObject, QRect
from core import ScannerWorker, ActionWorker, is_admin, check_network

LOG_FILE = Path(__file__).parent / "bluefalcon-app.log"

class GUILogHandler(logging.Handler, QObject):
    log_signal = pyqtSignal(str)
    
    def __init__(self):
        logging.Handler.__init__(self)
        QObject.__init__(self)

    def emit(self, record):
        msg = self.format(record)
        self.log_signal.emit(msg)

logger = logging.getLogger("BlueFalcon")
logger.setLevel(logging.INFO)
formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s', datefmt='%Y-%m-%d %H:%M:%S')

file_handler = RotatingFileHandler(LOG_FILE, maxBytes=1024*1024*5, backupCount=2, encoding='utf-8')
file_handler.setFormatter(formatter)
logger.addHandler(file_handler)

gui_handler = GUILogHandler()
gui_handler.setFormatter(formatter)
logger.addHandler(gui_handler)

class CheckBoxHeader(QHeaderView):
    stateChanged = pyqtSignal(Qt.CheckState)

    def __init__(self, orientation=Qt.Orientation.Horizontal, parent=None):
        super().__init__(orientation, parent)
        self._is_on = True

    def paintSection(self, painter, rect, logicalIndex):
        painter.save()
        super().paintSection(painter, rect, logicalIndex)
        painter.restore()

        if logicalIndex == 0:
            option = QStyleOptionButton()
            option.rect = QRect(rect.x() + 4, rect.y() + rect.height() // 2 - 9, 18, 18)
            option.state = QStyle.StateFlag.State_Enabled | QStyle.StateFlag.State_Active
            if self._is_on:
                option.state |= QStyle.StateFlag.State_On
            else:
                option.state |= QStyle.StateFlag.State_Off
            self.style().drawControl(QStyle.ControlElement.CE_CheckBox, option, painter)

    def mousePressEvent(self, event):
        logicalIndex = self.logicalIndexAt(event.pos())
        if logicalIndex == 0:
            self._is_on = not self._is_on
            state = Qt.CheckState.Checked if self._is_on else Qt.CheckState.Unchecked
            self.stateChanged.emit(state)
            self.viewport().update()
        super().mousePressEvent(event)

class AboutDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("About")
        self.setFixedSize(350, 200)
        self.setStyleSheet("""
            QDialog { background-color: #2B2D31; color: white; border-radius: 8px; }
            QLabel { font-size: 14px; }
            QPushButton { background-color: #A8C7FA; border: none; padding: 6px 12px; border-radius: 4px; color: #062E6F; font-family: 'Segoe UI', Arial, sans-serif; font-weight: bold; font-size: 14px; }
            QPushButton:hover { background-color: #D3E3FD; }
            a { color: #A8C7FA; text-decoration: none; }
            a:hover { text-decoration: underline; }
        """)
        
        layout = QVBoxLayout(self)
        title = QLabel(
            "<b>BlueFalcon Config Manager</b><br>v2.0<br><br>"
            "Created by BlueFalcon<br><br>"
            "<a href='https://github.com/bluefalcon2270/bluefalcon-ovpn-config-manager'>GitHub Repository</a>"
        )
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title.setOpenExternalLinks(True)
        
        btn_close = QPushButton("Close")
        btn_close.clicked.connect(self.accept)
        
        layout.addWidget(title)
        layout.addWidget(btn_close, alignment=Qt.AlignmentFlag.AlignCenter)

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("BlueFalcon OpenVPN Config Manager")
        self.setMinimumSize(1000, 700)
        
        icon_path = Path(__file__).parent / "icon.ico"
        if icon_path.exists():
            self.setWindowIcon(QIcon(str(icon_path)))

        self.target_directory = Path.cwd()
        self.scanner_worker = None
        self.action_worker = None
        self.current_file_paths = {}

        self._apply_dark_theme()
        self._init_ui()
        self._run_silent_preflight()
        
        self._refresh_table()

    def _apply_dark_theme(self):
        self.setStyleSheet("""
            QMainWindow { background-color: #1E1F22; }
            QWidget { color: #E3E3E3; font-family: 'Segoe UI', Arial, sans-serif; font-size: 14px; }
            QLineEdit { background-color: #2B2D31; border: 1px solid #44474A; padding: 0px 10px; border-radius: 6px; color: #FFFFFF; font-size: 13px; }
            QLineEdit:focus { border: 1px solid #A8C7FA; }
            QPushButton { background-color: #A8C7FA; border: none; border-radius: 6px; color: #062E6F; font-family: 'Segoe UI', Arial, sans-serif; font-weight: bold; font-size: 14px; padding: 4px; }
            QPushButton:hover { background-color: #D3E3FD; }
            QPushButton:disabled { background-color: #44474A; color: #8E918F; }
            QPushButton#danger { background-color: #F2B8B5; color: #601410; }
            QPushButton#danger:hover { background-color: #F9DEDC; }
            QPushButton#overlay_btn { background-color: #2B2D31; border: 1px solid #44474A; border-radius: 6px; font-size: 16px; font-weight: bold; color: #A8C7FA; }
            QPushButton#overlay_btn:hover { background-color: #383A40; color: #D3E3FD; }
            QTextEdit { background-color: #1E1F22; border: 1px solid #44474A; color: #A0A0A0; padding: 10px; border-radius: 6px; font-family: Consolas, monospace; font-size: 12px; }
            QTableWidget { background-color: #1E1F22; alternate-background-color: #242528; border: 1px solid #44474A; border-radius: 6px; color: #E3E3E3; gridline-color: transparent; }
            QHeaderView::section { background-color: #1E1F22; color: #A8C7FA; padding: 4px; border: none; border-bottom: 1px solid #44474A; font-weight: bold; font-size: 13px; }
            QTableWidget::item { padding: 4px; border-bottom: 1px solid #2B2D31; }
            QTableWidget::item:selected { background-color: #35383D; }
        """)

    def _init_ui(self):
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QVBoxLayout(central_widget)
        main_layout.setContentsMargins(20, 20, 20, 20)
        main_layout.setSpacing(15)

        top_bar = QHBoxLayout()
        top_bar.setSpacing(10)
        
        self.entry_user = QLineEdit()
        self.entry_user.setPlaceholderText("Username")
        self.entry_user.setFixedSize(160, 36)
        top_bar.addWidget(self.entry_user)

        self.entry_pass = QLineEdit()
        self.entry_pass.setPlaceholderText("Password")
        self.entry_pass.setFixedSize(160, 36)
        top_bar.addWidget(self.entry_pass)

        btn_apply = QPushButton("＋")
        btn_apply.setToolTip("Inject Credentials")
        btn_apply.setFixedSize(36, 36)
        btn_apply.clicked.connect(self._start_apply_auth)
        top_bar.addWidget(btn_apply)

        btn_clear = QPushButton("✕")
        btn_clear.setToolTip("Wipe Credentials")
        btn_clear.setObjectName("danger")
        btn_clear.setFixedSize(36, 36)
        btn_clear.clicked.connect(self._start_clear_auth)
        top_bar.addWidget(btn_clear)

        top_bar.addStretch()

        btn_rename = QPushButton("Rename to Host")
        btn_rename.setFixedSize(150, 36)
        btn_rename.clicked.connect(self._start_rename)
        top_bar.addWidget(btn_rename)

        btn_about = QPushButton("ⓘ")
        btn_about.setObjectName("overlay_btn")
        btn_about.setFixedSize(36, 36)
        btn_about.clicked.connect(self._show_about)
        top_bar.addWidget(btn_about)

        main_layout.addLayout(top_bar)

        table_container = QWidget()
        table_layout = QGridLayout(table_container)
        table_layout.setContentsMargins(0, 0, 0, 0)

        self.table = QTableWidget()
        self.table.setColumnCount(7)
        
        self.checkbox_header = CheckBoxHeader(Qt.Orientation.Horizontal)
        self.checkbox_header.stateChanged.connect(self._set_all_checkboxes)
        self.table.setHorizontalHeader(self.checkbox_header)
        
        self.table.setHorizontalHeaderLabels(["", "#", "File Name", "Target Host", "Port", "Username", "Password"])
        
        for i in range(7):
            item = self.table.horizontalHeaderItem(i)
            if item:
                item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)

        self.table.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        self.table.setAlternatingRowColors(True)
        self.table.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        self.table.verticalHeader().setVisible(False)
        self.table.setShowGrid(False)
        
        header = self.table.horizontalHeader()
        header.setMinimumHeight(46)
        
        header.setSectionResizeMode(0, QHeaderView.ResizeMode.Fixed)
        self.table.setColumnWidth(0, 40)
        
        header.setSectionResizeMode(1, QHeaderView.ResizeMode.ResizeToContents)
        header.setSectionResizeMode(2, QHeaderView.ResizeMode.ResizeToContents)
        header.setSectionResizeMode(3, QHeaderView.ResizeMode.ResizeToContents)
        header.setSectionResizeMode(4, QHeaderView.ResizeMode.ResizeToContents)
        header.setSectionResizeMode(5, QHeaderView.ResizeMode.Stretch)
        header.setSectionResizeMode(6, QHeaderView.ResizeMode.Stretch)
        
        table_layout.addWidget(self.table, 0, 0)

        refresh_wrapper = QWidget()
        refresh_box = QVBoxLayout(refresh_wrapper)
        refresh_box.setContentsMargins(0, 8, 8, 0) 
        
        self.btn_refresh = QPushButton("↻")
        self.btn_refresh.setObjectName("overlay_btn")
        self.btn_refresh.setFixedSize(30, 30)
        self.btn_refresh.setToolTip("Refresh List")
        self.btn_refresh.clicked.connect(self._refresh_table)
        refresh_box.addWidget(self.btn_refresh)
        
        table_layout.addWidget(refresh_wrapper, 0, 0, Qt.AlignmentFlag.AlignTop | Qt.AlignmentFlag.AlignRight)
        main_layout.addWidget(table_container, stretch=2)

        log_container = QWidget()
        log_layout = QGridLayout(log_container)
        log_layout.setContentsMargins(0, 0, 0, 0)

        self.log_viewer = QTextEdit()
        self.log_viewer.setReadOnly(True)
        log_layout.addWidget(self.log_viewer, 0, 0)

        clear_wrapper = QWidget()
        clear_box = QVBoxLayout(clear_wrapper)
        clear_box.setContentsMargins(0, 8, 8, 0)
        
        self.btn_clear_log = QPushButton("✕")
        self.btn_clear_log.setObjectName("overlay_btn")
        self.btn_clear_log.setFixedSize(30, 30)
        self.btn_clear_log.setToolTip("Clear Log")
        self.btn_clear_log.clicked.connect(self.log_viewer.clear)
        clear_box.addWidget(self.btn_clear_log)

        log_layout.addWidget(clear_wrapper, 0, 0, Qt.AlignmentFlag.AlignTop | Qt.AlignmentFlag.AlignRight)
        main_layout.addWidget(log_container, stretch=1)
        
        gui_handler.log_signal.connect(self.log_viewer.append)

    def _show_about(self):
        dlg = AboutDialog(self)
        dlg.exec()

    def _run_silent_preflight(self):
        logger.info("Application initialized.")
        if not is_admin():
            logger.warning("Admin privileges not detected.")

    def _set_all_checkboxes(self, state: Qt.CheckState):
        for row in range(self.table.rowCount()):
            item = self.table.item(row, 0)
            if item:
                item.setCheckState(state)

    def _get_selected_files(self) -> list[Path]:
        selected = []
        for row in range(self.table.rowCount()):
            item = self.table.item(row, 0)
            if item and item.checkState() == Qt.CheckState.Checked:
                if row in self.current_file_paths:
                    selected.append(self.current_file_paths[row])
        return selected

    def _refresh_table(self):
        self.table.setRowCount(0)
        self.current_file_paths.clear()
        
        self.scanner_worker = ScannerWorker(self.target_directory)
        self.scanner_worker.finished.connect(self._populate_table)
        self.scanner_worker.error.connect(lambda e: logger.error(f"Scan Error: {e}"))
        self.scanner_worker.start()

    def _populate_table(self, data: list[dict]):
        self.table.setRowCount(len(data))
        for row, info in enumerate(data):
            self.current_file_paths[row] = info["path"]
            
            chk = QTableWidgetItem()
            chk.setFlags(Qt.ItemFlag.ItemIsUserCheckable | Qt.ItemFlag.ItemIsEnabled)
            current_header_state = Qt.CheckState.Checked if self.checkbox_header._is_on else Qt.CheckState.Unchecked
            chk.setCheckState(current_header_state)
            self.table.setItem(row, 0, chk)
            
            self.table.setItem(row, 1, QTableWidgetItem(str(row + 1)))
            self.table.setItem(row, 2, QTableWidgetItem(info["filename"]))
            self.table.setItem(row, 3, QTableWidgetItem(info["host"]))
            self.table.setItem(row, 4, QTableWidgetItem(info["port"]))
            self.table.setItem(row, 5, QTableWidgetItem(info["user"]))
            self.table.setItem(row, 6, QTableWidgetItem(info["pass"]))
            
            for col in range(1, 7):
                self.table.item(row, col).setTextAlignment(Qt.AlignmentFlag.AlignCenter)

        self.btn_refresh.raise_()

    def _start_worker(self, operation: str, username: str = "", password: str = ""):
        selected_files = self._get_selected_files()
        if not selected_files:
            QMessageBox.information(self, "No Selection", "Please check the box next to at least one file to process.")
            return

        self.table.setEnabled(False)
        self.action_worker = ActionWorker(operation, selected_files, username, password)
        self.action_worker.log_msg.connect(logger.info)
        self.action_worker.error.connect(self._on_worker_error)
        self.action_worker.finished.connect(self._on_worker_finished)
        self.action_worker.start()

    def _on_worker_error(self, e: str):
        logger.error(f"Action Error: {e}")
        QMessageBox.critical(self, "Error", f"An error occurred:\n{e}")

    def _on_worker_finished(self):
        self.table.setEnabled(True)
        self.action_worker = None
        self._refresh_table()

    def _start_apply_auth(self):
        user = self.entry_user.text().strip()
        pwd = self.entry_pass.text().strip()
        if not user or not pwd:
            QMessageBox.warning(self, "Input Required", "Both username and password fields must be filled to inject credentials.")
            return
        self._start_worker("apply_auth", user, pwd)

    def _start_clear_auth(self):
        self._start_worker("clear_auth")

    def _start_rename(self):
        self._start_worker("rename")

    def closeEvent(self, event):
        if self.action_worker and self.action_worker.isRunning():
            self.action_worker.stop()
            self.action_worker.wait()
        if self.scanner_worker and self.scanner_worker.isRunning():
            self.scanner_worker.wait()
        
        for handler in logger.handlers[:]:
            handler.close()
            logger.removeHandler(handler)
            
        event.accept()