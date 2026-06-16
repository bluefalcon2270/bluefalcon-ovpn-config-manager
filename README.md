# BlueFalcon OpenVPN Config Manager

A professional, single-window Windows desktop utility designed to safely and selectively batch-process OpenVPN configuration (`.ovpn`) files. This application allows you to monitor, inject, and remove inline credentials, as well as automatically rename files based on their destination host configuration. 

Featuring a modern, dark Google Material Design 3 UI layer. Built exclusively for Windows environments using modern Python 3.10+ and PyQt6.

## Features
* **Google Material Design 3 GUI:** Clean, flat, high border-radius dark mode interface.
* **Unified Data Dashboard:** Automatically scans your local directory and parses all `.ovpn` files into a clean table showing target hosts, ports, and current unmasked credentials.
* **Master Select Controls:** Integrated header checkbox for rapid "Select All / None" targeting to apply changes only to the files you want.
* **Authentication Management:** Seamlessly inject or wipe inline `<auth-user-pass>` credential blocks.
* **Intelligent Auto-Renaming:** Extract destination server hostnames from the `remote` directive and rename files instantly.
* **Safe & Non-Destructive:** Performs idempotency checks before renaming and preserves critical certificate blocks during file rewriting.

## Installation & Setup (Windows)

### Download Compiled Executable
Head over to the **Releases** section on the right side of this page to download the pre-compiled standalone `.exe`. No installation required!

### Run from Source

**Prerequisites:** Python 3.10+

1. Clone this repository to your local machine.
2. Open **Command Prompt** or **PowerShell** and navigate to the folder.
3. Install the required dependencies:
    ```cmd
    pip install -r requirements.txt
    ```
4. Run the application:
    ```cmd
    python main.py
    ```