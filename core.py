# Version: v1.5
# BlueFalcon OpenVPN Config Manager - Core Backend

import platform
import ctypes
import urllib.request
from pathlib import Path
from PyQt6.QtCore import QThread, pyqtSignal

def is_admin() -> bool:
    try:
        return ctypes.windll.shell32.IsUserAnAdmin() != 0
    except Exception:
        return False

def check_network() -> bool:
    try:
        urllib.request.urlopen('http://1.1.1.1', timeout=2)
        return True
    except Exception:
        return False

class ScannerWorker(QThread):
    finished = pyqtSignal(list)
    error = pyqtSignal(str)

    def __init__(self, target_dir: Path):
        super().__init__()
        self.target_dir = target_dir

    def run(self):
        try:
            files = list(self.target_dir.glob("*.ovpn"))
            results = []
            for i, filepath in enumerate(files):
                data = {
                    "path": filepath,
                    "filename": filepath.name,
                    "host": "",
                    "port": "",
                    "user": "",
                    "pass": ""
                }
                
                in_auth = False
                auth_lines = []
                
                with open(filepath, 'r', encoding='utf-8') as f:
                    for line in f:
                        stripped = line.strip()
                        if stripped.startswith('remote '):
                            parts = stripped.split()
                            if len(parts) >= 2: data["host"] = parts[1]
                            if len(parts) >= 3: data["port"] = parts[2]
                        elif stripped.startswith('port ') and not data["port"]:
                            parts = stripped.split()
                            if len(parts) >= 2: data["port"] = parts[1]
                        elif stripped == "<auth-user-pass>":
                            in_auth = True
                        elif stripped == "</auth-user-pass>":
                            in_auth = False
                        elif in_auth:
                            auth_lines.append(stripped)
                
                if len(auth_lines) >= 1: data["user"] = auth_lines[0]
                if len(auth_lines) >= 2: data["pass"] = auth_lines[1]
                
                results.append(data)
                
            self.finished.emit(results)
        except Exception as e:
            self.error.emit(str(e))

class ActionWorker(QThread):
    log_msg = pyqtSignal(str)
    finished = pyqtSignal()
    error = pyqtSignal(str)

    def __init__(self, operation: str, target_files: list[Path], username: str = "", password: str = ""):
        super().__init__()
        self.operation = operation
        self.target_files = target_files
        self.username = username
        self.password = password
        self._is_running = True

    def run(self):
        try:
            if not self.target_files:
                self.log_msg.emit("No files selected for processing.")
                self.finished.emit()
                return
            
            for filepath in self.target_files:
                if not self._is_running:
                    self.log_msg.emit("Operation cancelled by user.")
                    break

                match self.operation:
                    case "apply_auth":
                        self._process_auth(filepath, apply=True)
                    case "clear_auth":
                        self._process_auth(filepath, apply=False)
                    case "rename":
                        self._rename_file(filepath)

            self.log_msg.emit(f"--- {self.operation.replace('_', ' ').title()} Complete ---")
        except Exception as e:
            self.error.emit(str(e))
        finally:
            self.finished.emit()

    def stop(self):
        self._is_running = False

    def _process_auth(self, filepath: Path, apply: bool):
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                lines = f.readlines()

            cleaned_lines = []
            in_block = False
            
            for line in lines:
                stripped = line.strip()
                if stripped == "<auth-user-pass>":
                    in_block = True
                elif stripped == "</auth-user-pass>":
                    in_block = False
                elif in_block:
                    continue
                elif stripped == "auth-user-pass":
                    continue
                else:
                    cleaned_lines.append(line)
            
            insert_index = len(cleaned_lines)
            for i, line in enumerate(cleaned_lines):
                if line.strip() in ["<ca>", "<cert>", "<key>", "<tls-auth>", "<tls-crypt>"]:
                    insert_index = i
                    break
            
            if apply:
                auth_block = [
                    "auth-user-pass\n",
                    "<auth-user-pass>\n",
                    f"{self.username}\n",
                    f"{self.password}\n",
                    "</auth-user-pass>\n"
                ]
            else:
                auth_block = ["auth-user-pass\n"]
                
            new_lines = cleaned_lines[:insert_index] + auth_block + cleaned_lines[insert_index:]

            while new_lines and new_lines[-1].strip() == "":
                new_lines.pop()
            if new_lines and not new_lines[-1].endswith('\n'):
                new_lines[-1] += '\n'

            with open(filepath, 'w', encoding='utf-8') as f:
                f.writelines(new_lines)
            
            action = "Injected" if apply else "Wiped"
            self.log_msg.emit(f"{action} credentials in: {filepath.name}")
        except Exception as e:
            self.log_msg.emit(f"Error processing {filepath.name}: {str(e)}")

    def _rename_file(self, filepath: Path):
        try:
            hostname = None
            with open(filepath, 'r', encoding='utf-8') as f:
                for line in f:
                    if line.startswith('remote '):
                        parts = line.strip().split()
                        if len(parts) >= 2:
                            hostname = parts[1]
                            break
            
            if hostname:
                base_filename = f"{hostname}.ovpn"
                new_filepath = filepath.with_name(base_filename)
                
                if filepath == new_filepath:
                    return 
                
                if new_filepath.exists():
                    counter = 1
                    while True:
                        test_name = f"{hostname} ({counter}).ovpn"
                        test_path = filepath.with_name(test_name)
                        if not test_path.exists():
                            new_filepath = test_path
                            break
                        counter += 1
                        
                filepath.rename(new_filepath)
                self.log_msg.emit(f"Renamed: {filepath.name} -> {new_filepath.name}")
            else:
                self.log_msg.emit(f"Skipped: {filepath.name} (No 'remote' host found)")
        except Exception as e:
            self.log_msg.emit(f"Error renaming {filepath.name}: {str(e)}")