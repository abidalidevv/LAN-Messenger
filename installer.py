import os
import sys
import shutil
import subprocess
from pathlib import Path

from PyQt6.QtWidgets import (
    QApplication,
    QWizard,
    QWizardPage,
    QVBoxLayout,
    QHBoxLayout,
    QGridLayout,
    QLabel,
    QLineEdit,
    QPushButton,
    QCheckBox,
    QFileDialog,
    QScrollArea,
    QWidget,
    QProgressBar,
    QMessageBox,
)
from PyQt6.QtGui import QIcon, QPixmap
from PyQt6.QtCore import Qt

from app.utils.avatars import AVATARS, get_avatar
from app.utils.paths import get_asset_path


def get_default_install_dir() -> Path:
    local_app_data = os.environ.get("LOCALAPPDATA")
    if local_app_data:
        return Path(local_app_data) / "Programs" / "LANMessenger"
    return Path.home() / "AppData" / "Local" / "Programs" / "LANMessenger"


def create_windows_shortcut(
    target_path: Path, shortcut_path: Path, icon_path: Path, description: str
):
    """Creates a Windows .lnk shortcut via VBScript."""
    vbs_content = f"""
Set oWS = WScript.CreateObject("WScript.Shell")
sLinkFile = "{str(shortcut_path)}"
Set oLink = oWS.CreateShortcut(sLinkFile)
oLink.TargetPath = "{str(target_path)}"
oLink.WorkingDirectory = "{str(target_path.parent)}"
oLink.Description = "{description}"
oLink.IconLocation = "{str(icon_path)}"
oLink.Save
"""
    temp_vbs = Path(os.environ.get("TEMP", ".")) / f"sc_{os.getpid()}.vbs"
    with open(temp_vbs, "w", encoding="utf-8") as f:
        f.write(vbs_content)
    subprocess.run(["cscript", "/nologo", str(temp_vbs)], shell=True)
    try:
        temp_vbs.unlink()
    except Exception:
        pass


class WelcomePage(QWizardPage):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setTitle("Welcome to LAN Messenger Setup")
        self.setSubTitle(
            "This wizard will install LAN Messenger on your computer.\n"
            "High-speed local network messaging and file sharing with zero internet."
        )

        layout = QVBoxLayout(self)
        layout.setSpacing(14)

        icon_path = get_asset_path("app_icon.png")
        if os.path.exists(icon_path):
            pix = QPixmap(icon_path).scaled(
                72, 72, Qt.AspectRatioMode.KeepAspectRatio
            )
            lbl_icon = QLabel()
            lbl_icon.setPixmap(pix)
            layout.addWidget(lbl_icon, alignment=Qt.AlignmentFlag.AlignCenter)

        desc = QLabel(
            "<b>Features included:</b><br>"
            "• Direct PC-to-PC HD file sharing at full wire speed<br>"
            "• Automatic dual-router discovery (Huawei + Tenda)<br>"
            "• Mobile phone QR Code connect (Android & iPhone)<br>"
            "• 📢 Group Broadcast channel & 📋 Clipboard sync<br>"
            "• 100% Private, no phone number, no cloud server"
        )
        desc.setStyleSheet("color: #e9edef; font-size: 13px; line-height: 1.5;")
        layout.addWidget(desc)
        layout.addStretch()


class DirectoryPage(QWizardPage):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setTitle("Select Installation Folder")
        self.setSubTitle(
            "Where should LAN Messenger be installed on your computer?"
        )

        layout = QVBoxLayout(self)
        layout.setSpacing(12)

        lbl = QLabel("Destination Folder (Auto-detected):")
        layout.addWidget(lbl)

        box = QHBoxLayout()
        self.path_input = QLineEdit()
        self.path_input.setText(str(get_default_install_dir()))
        btn_browse = QPushButton("Browse...")
        btn_browse.clicked.connect(self._browse)
        box.addWidget(self.path_input)
        box.addWidget(btn_browse)
        layout.addLayout(box)

        self.cb_desktop = QCheckBox("Create Desktop Shortcut")
        self.cb_desktop.setChecked(True)
        layout.addWidget(self.cb_desktop)

        self.cb_startmenu = QCheckBox("Create Start Menu Shortcut")
        self.cb_startmenu.setChecked(True)
        layout.addWidget(self.cb_startmenu)

        self.cb_firewall = QCheckBox(
            "Automatically configure Windows Firewall rules"
        )
        self.cb_firewall.setChecked(True)
        layout.addWidget(self.cb_firewall)

        layout.addStretch()

    def _browse(self):
        folder = QFileDialog.getExistingDirectory(
            self, "Select Install Folder", self.path_input.text()
        )
        if folder:
            self.path_input.setText(folder)


class ProfilePage(QWizardPage):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setTitle("Set Up Your Profile")
        self.setSubTitle(
            "Choose your display name, avatar, and optional email."
        )

        layout = QVBoxLayout(self)
        layout.setSpacing(10)

        # Name and Email
        row = QHBoxLayout()

        col_name = QVBoxLayout()
        col_name.addWidget(QLabel("Your Display Name:"))
        self.name_input = QLineEdit()
        self.name_input.setText(os.environ.get("USERNAME", "My PC").capitalize())
        col_name.addWidget(self.name_input)
        row.addLayout(col_name)

        col_email = QVBoxLayout()
        col_email.addWidget(QLabel("Email (Optional):"))
        self.email_input = QLineEdit()
        self.email_input.setPlaceholderText("user@example.com")
        col_email.addWidget(self.email_input)
        row.addLayout(col_email)

        layout.addLayout(row)

        layout.addWidget(QLabel("Select an Avatar from 20 Prebuilt Styles:"))

        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFixedHeight(180)

        grid_widget = QWidget()
        grid_layout = QGridLayout(grid_widget)
        grid_layout.setSpacing(6)

        self.selected_avatar = "gamer"
        self.buttons = {}
        for idx, av in enumerate(AVATARS):
            btn = QPushButton(av["icon"])
            btn.setFixedSize(50, 50)
            btn.setCursor(Qt.CursorShape.PointingHandCursor)
            btn.setToolTip(av["name"])
            btn.clicked.connect(
                lambda checked, aid=av["id"]: self._select_avatar(aid)
            )
            self.buttons[av["id"]] = btn
            grid_layout.addWidget(btn, idx // 5, idx % 5)

        scroll.setWidget(grid_widget)
        layout.addWidget(scroll)
        self._select_avatar("gamer")

    def _select_avatar(self, aid: str):
        self.selected_avatar = aid
        for a_id, btn in self.buttons.items():
            av = get_avatar(a_id)
            is_sel = a_id == aid
            border = "3px solid #00a884" if is_sel else "1px solid rgba(255,255,255,0.1)"
            btn.setStyleSheet(
                f"background-color: {av['bg']}; color: #fff; border: {border}; border-radius: 25px; font-size: 22px;"
            )


class InstallPage(QWizardPage):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setTitle("Installing...")
        self.setSubTitle("Please wait while LAN Messenger is being installed.")

        layout = QVBoxLayout(self)
        layout.setSpacing(16)

        self.lbl_status = QLabel("Extracting and installing files...")
        layout.addWidget(self.lbl_status)

        self.prog_bar = QProgressBar()
        self.prog_bar.setRange(0, 100)
        self.prog_bar.setValue(10)
        layout.addWidget(self.prog_bar)

        self.cb_launch = QCheckBox("Launch LAN Messenger now")
        self.cb_launch.setChecked(True)
        layout.addWidget(self.cb_launch)

        layout.addStretch()

    def initializePage(self):
        # Perform installation steps
        wizard = self.wizard()
        dest_dir = Path(wizard.dir_page.path_input.text().strip())
        dest_dir.mkdir(parents=True, exist_ok=True)

        self.prog_bar.setValue(30)
        self.lbl_status.setText("Copying program files...")

        # Current executable or project root
        base_dir = Path(__file__).resolve().parent
        exe_source = base_dir / "LANMessenger.exe"
        if not exe_source.exists():
            exe_source = base_dir / "dist" / "LANMessenger.exe"

        dest_exe = dest_dir / "LANMessenger.exe"
        if exe_source.exists():
            shutil.copy2(exe_source, dest_exe)

        # Copy Assets
        dest_assets = dest_dir / "assets"
        dest_assets.mkdir(parents=True, exist_ok=True)
        src_assets = base_dir / "assets"
        if src_assets.exists():
            for f in src_assets.glob("*"):
                shutil.copy2(f, dest_assets / f.name)

        self.prog_bar.setValue(60)

        # Save Initial Config
        appdata_dir = (
            Path(os.environ.get("APPDATA", ".")) / "LANMessenger"
        )
        appdata_dir.mkdir(parents=True, exist_ok=True)
        cfg_file = appdata_dir / "config.json"

        user_name = wizard.profile_page.name_input.text().strip() or "My PC"
        user_email = wizard.profile_page.email_input.text().strip()
        user_avatar = wizard.profile_page.selected_avatar

        import json

        cfg_data = {
            "username": user_name,
            "email": user_email,
            "avatar_id": user_avatar,
            "is_configured": True,
            "tcp_port": 9876,
            "udp_port": 9877,
            "download_dir": str(Path.home() / "Downloads" / "LANMessenger"),
            "saved_peers": ["192.168.100.8", "192.168.7.7"],
            "custom_subnets": ["192.168.100", "192.168.7"],
            "sound_enabled": True,
            "notifications_enabled": True,
            "minimize_to_tray": True,
            "theme": "dark",
        }
        with open(cfg_file, "w", encoding="utf-8") as f:
            json.dump(cfg_data, f, indent=4)

        self.prog_bar.setValue(80)
        self.lbl_status.setText("Creating shortcuts and firewall rules...")

        icon_dest = dest_assets / "app_icon.ico"

        # Desktop Shortcut
        if wizard.dir_page.cb_desktop.isChecked():
            user_desktop = Path(os.environ.get("USERPROFILE", ".")) / "Desktop"
            create_windows_shortcut(
                dest_exe,
                user_desktop / "LAN Messenger.lnk",
                icon_dest,
                "LAN Messenger",
            )

        # Start Menu Shortcut
        if wizard.dir_page.cb_startmenu.isChecked():
            start_menu = (
                Path(os.environ.get("APPDATA", "."))
                / "Microsoft"
                / "Windows"
                / "Start Menu"
                / "Programs"
            )
            create_windows_shortcut(
                dest_exe,
                start_menu / "LAN Messenger.lnk",
                icon_dest,
                "LAN Messenger",
            )

        # Firewall Rules
        if wizard.dir_page.cb_firewall.isChecked():
            try:
                subprocess.run(
                    f'netsh advfirewall firewall add rule name="LANMessenger_TCP" dir=in action=allow protocol=TCP localport=9876 program="{str(dest_exe)}"',
                    shell=True,
                )
                subprocess.run(
                    f'netsh advfirewall firewall add rule name="LANMessenger_UDP" dir=in action=allow protocol=UDP localport=9877 program="{str(dest_exe)}"',
                    shell=True,
                )
            except Exception:
                pass

        self.prog_bar.setValue(100)
        self.lbl_status.setText("Installation completed successfully!")

        wizard.installed_exe = dest_exe


class SetupWizard(QWizard):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("LAN Messenger Setup Wizard")
        self.setFixedSize(580, 500)
        self.setWindowFlags(self.windowFlags() & ~Qt.WindowType.WindowContextHelpButtonHint)

        icon_path = get_asset_path("app_icon.png")
        self.setWindowIcon(QIcon(icon_path))

        self.installed_exe = None

        self.welcome_page = WelcomePage(self)
        self.dir_page = DirectoryPage(self)
        self.profile_page = ProfilePage(self)
        self.install_page = InstallPage(self)

        self.addPage(self.welcome_page)
        self.addPage(self.dir_page)
        self.addPage(self.profile_page)
        self.addPage(self.install_page)


def main():
    app = QApplication(sys.argv)
    wizard = SetupWizard()
    wizard.show()
    app.exec()

    # Launch app if selected
    if wizard.install_page.cb_launch.isChecked() and wizard.installed_exe:
        if wizard.installed_exe.exists():
            subprocess.Popen([str(wizard.installed_exe)])


if __name__ == "__main__":
    main()

