<div align="center">

# 🔐 BlueFalcon OpenVPN Config Manager

**A professional, Material Design 3 Windows utility to safely batch-process and manage OpenVPN configuration files.**

![Windows](https://img.shields.io/badge/Platform-Windows-0078D6?style=for-the-badge&logo=windows&logoColor=white)
[![Language](https://img.shields.io/badge/Written%20in-Python-3776AB?style=for-the-badge&logo=python&logoColor=white)](https://www.python.org/)
[![UI Framework](https://img.shields.io/badge/Framework-PyQt6-41CD52?style=for-the-badge&logo=qt&logoColor=white)](https://riverbankcomputing.com/software/pyqt/)
[![License](https://img.shields.io/badge/License-MIT-yellow.svg?style=for-the-badge)](LICENSE)
[![YouTube](https://img.shields.io/badge/YouTube-FF0000?style=for-the-badge&logo=youtube&logoColor=white)](https://www.youtube.com/@BlueFalcon2270)

<br />
</div>

An automated, elegant desktop application designed to completely manage your OpenVPN (`.ovpn`) files. It allows you to monitor, inject, and completely wipe inline credentials, as well as automatically rename files based on their destination host configuration. Built exclusively for Windows environments using modern Python 3.10+ and PyQt6, wrapped in a beautiful dark Google Material Design 3 UI layer.
<br><br>

## ⚡ Quick Start

### Option A: Download Compiled Executable (Recommended)
No installation or Python required. Simply head over to the **[Releases](../../releases/latest)** section on the right side of this repository and download the standalone `BlueFalcon_OpenVPN_Manager.exe`. Double-click to run!

### Option B: Run from Source
If you prefer to run the raw Python script, open **Command Prompt** or **PowerShell** and run:

```cmd
git clone [https://github.com/bluefalcon2270/bluefalcon-ovpn-config-manager.git](https://github.com/bluefalcon2270/bluefalcon-ovpn-config-manager.git)
cd bluefalcon-ovpn-config-manager
pip install -r requirements.txt
python main.py
```

<br>

## 🌟 Features
By launching the application, you are greeted with a clean, unified dashboard featuring the following capabilities:

### 1️⃣ Unified Data Dashboard
Automatically scans your local directory and parses all `.ovpn` files into a clean visual table. Instantly see target hosts, ports, and current unmasked credentials for every file at a glance.

### 2️⃣ Authentication Management
Seamlessly inject or completely wipe inline `<auth-user-pass>` credential blocks. The app intelligently locates the correct insertion points and preserves your critical certificate blocks (`<ca>`, `<cert>`) without corrupting the file.

### 3️⃣ Intelligent Auto-Renaming
Extracts the destination server hostname from the `remote` directive inside the config and renames the file instantly. Includes a smart duplicate handler that sequentially numbers files (e.g., `host (1).ovpn`) so you never accidentally overwrite existing configs.

### 4️⃣ Master Select Controls
Features an integrated master header checkbox for rapid "Select All / Select None" targeting. Operations only apply to the files you explicitly check off.

### 5️⃣ Material Design 3 GUI
A fully custom, modern interface featuring a dark mode color palette, flat Unicode UI icons, rounded layout borders, and a dynamic status badge for real-time visual feedback. 

### 6️⃣ Background Threading & Safety
Utilizes asynchronous `QThread` workers so the interface never freezes during large batch operations. Includes OS validation, idempotency checks, and built-in diagnostic logging.

<br>

## 🚀 Future Roadmap
BlueFalcon OpenVPN Config Manager is constantly evolving. The following features are currently on the development radar:
- [x] **Material Design 3 Overhaul** *(Completed)*
- [x] **Modular Architecture Refactor** *(Completed)*
- [ ] **Drag-and-Drop File Import**
- [ ] **Advanced Regex Port/Host Extraction**
- [ ] **Cross-Platform Linux/macOS Support**

<br>

## ✅ Supported Systems
| Operating System | Compatibility | Notes |
| :--- | :---: | :--- |
| **Windows 11** | ✅ | Fully Supported |
| **Windows 10** | ✅ | Fully Supported |
| **Linux / macOS** | ❌ | Currently locked to Windows OS validation |

*(Note: Running from source requires **Python 3.10** or higher to support modern `match-case` syntax).*