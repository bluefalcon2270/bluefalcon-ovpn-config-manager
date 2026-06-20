<div align="center">

# 🔐 BlueFalcon OpenVPN Config Manager

**A professional mini app to manage OpenVPN configs and automate logins with your username and password.**

![Windows](https://img.shields.io/badge/Platform-Windows-0078D6?style=for-the-badge&logo=windows&logoColor=white)
[![License](https://img.shields.io/badge/License-MIT-yellow.svg?style=for-the-badge)](LICENSE)
[![YouTube](https://img.shields.io/badge/YouTube-FF0000?style=for-the-badge&logo=youtube&logoColor=white)](https://www.youtube.com/@BlueFalcon2270)

<br />
</div>

An automated desktop application designed to manage your OpenVPN (`.ovpn`) files. It allows you to monitor, inject, and remove credentials, as well as automatically rename files based on their destination server.
<br><br>

## 🚀 How to Use

**Step 1: Download**
* Go to the **Releases** section on the right side of this page.
* Download the `BlueFalcon_OpenVPN_Manager.exe` file. No installation is required.

**Step 2: Setup Your Folder**
* Create a new folder anywhere on your computer.
* Place the downloaded `.exe` file AND all your `.ovpn` config files into this exact same folder.

**Step 3: Run and Manage**
* Double-click the `.exe` file to open the app.
* The app will automatically scan the folder and display your config files in the dashboard.
* **To Add Login:** Check the boxes next to your files, type your Username and Password at the top, and click **＋ Inject**.
* **To Remove Login:** Check the boxes and click **✕ Wipe**.
* **To Rename:** Check the boxes and click **Rename to Host** to auto-rename the files based on their server IP.

<br>

## 🌟 Features

* **Authentication Management:** Instantly add your username and password into your `.ovpn` files so you can auto-login without typing them every time. You can also wipe them clean just as easily.
* **Intelligent Auto-Renaming:** Automatically renames your config files based on the server they connect to, making them easy to identify.
* **Clean and Simple Interface:** A dark-mode, modern dashboard that shows all your files, target servers, and current passwords in one clear table.

<br>

## 💻 For Developers

If you want to edit the Python code or build the app yourself, the code is organized into three simple files (`main.py`, `gui.py`, and `core.py`). 

To build your own `.exe` file, install the requirements and run this command:

```cmd
pyinstaller --noconfirm --onefile --windowed --icon="icon.ico" --name "BlueFalcon_OpenVPN_Manager" "main.py"
```

<br>

## ✅ Supported Systems

* **Windows 11:** Fully Supported
* **Windows 10:** Fully Supported