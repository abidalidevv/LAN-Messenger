import sys
from PyQt6.QtWidgets import QSystemTrayIcon, QMenu
from PyQt6.QtGui import QIcon, QAction
from PyQt6.QtCore import QObject, pyqtSignal
from ..utils.paths import get_asset_path


class TrayManager(QObject):
    """Manages Windows System Tray icon and native toast notifications."""

    sig_show_window = pyqtSignal()
    sig_open_downloads = pyqtSignal()
    sig_open_settings = pyqtSignal()
    sig_scan_network = pyqtSignal()
    sig_exit_app = pyqtSignal()

    def __init__(self, parent=None):
        super().__init__(parent)
        self.tray_icon = QSystemTrayIcon(parent)
        self.init_tray()

    def init_tray(self):
        icon_path = get_asset_path("app_icon.png")
        icon = QIcon(icon_path)
        self.tray_icon.setIcon(icon)
        self.tray_icon.setToolTip("LAN Messenger — Active on Home Network")

        # Context Menu
        menu = QMenu()

        act_open = QAction("Open LAN Messenger", menu)
        act_open.triggered.connect(self.sig_show_window.emit)
        menu.addAction(act_open)

        menu.addSeparator()

        act_scan = QAction("🔍 Scan LAN Devices", menu)
        act_scan.triggered.connect(self.sig_scan_network.emit)
        menu.addAction(act_scan)

        act_downloads = QAction("📁 Open Downloads Folder", menu)
        act_downloads.triggered.connect(self.sig_open_downloads.emit)
        menu.addAction(act_downloads)

        act_settings = QAction("⚙️ Settings", menu)
        act_settings.triggered.connect(self.sig_open_settings.emit)
        menu.addAction(act_settings)

        menu.addSeparator()

        act_exit = QAction("Exit LAN Messenger", menu)
        act_exit.triggered.connect(self.sig_exit_app.emit)
        menu.addAction(act_exit)

        self.tray_icon.setContextMenu(menu)
        self.tray_icon.activated.connect(self._on_tray_activated)
        self.tray_icon.show()

    def _on_tray_activated(self, reason):
        if (
            reason == QSystemTrayIcon.ActivationReason.Trigger
            or reason == QSystemTrayIcon.ActivationReason.DoubleClick
        ):
            self.sig_show_window.emit()

    def show_notification(
        self,
        title: str,
        message: str,
        icon_type: QSystemTrayIcon.MessageIcon = QSystemTrayIcon.MessageIcon.Information,
    ):
        """Displays native Windows balloon / toast notification."""
        if self.tray_icon.isSystemTrayAvailable():
            self.tray_icon.showMessage(title, message, icon_type, 4000)

