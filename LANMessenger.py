import sys
import os
import socket
from pathlib import Path

# Add current directory to sys.path so modules resolve whether run as script or packaged
BASE_DIR = Path(__file__).resolve().parent
if str(BASE_DIR) not in sys.path:
    sys.path.insert(0, str(BASE_DIR))

from PyQt6.QtWidgets import QApplication, QMessageBox
from PyQt6.QtGui import QIcon
from PyQt6.QtCore import Qt

from app.config import config
from app.network.engine import NetworkEngine
from app.ui.main_window import MainWindow
from app.ui.setup_dialog import SetupDialog
from app.utils.paths import get_asset_path


def check_single_instance(port: int = 49876) -> socket.socket:
    """Enforces single application instance per PC via a local bound socket."""
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:
        s.bind(("127.0.0.1", port))
        s.listen(1)
        return s
    except socket.error:
        print("LAN Messenger is already running on this PC.")
        return None


def main():
    # Set Windows Taskbar Application ID so custom icon displays properly on Windows Taskbar
    if sys.platform == "win32":
        try:
            import ctypes

            myappid = "homelan.lanmessenger.app.1"
            ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID(myappid)
        except Exception:
            pass

    # Enforce single instance
    lock_socket = check_single_instance()
    if lock_socket is None:
        # App is already running
        app = QApplication(sys.argv)
        QMessageBox.information(
            None,
            "Already Running",
            "LAN Messenger is already running in your system tray or background.",
        )
        sys.exit(0)

    # Enable High DPI scaling
    QApplication.setHighDpiScaleFactorRoundingPolicy(
        Qt.HighDpiScaleFactorRoundingPolicy.PassThrough
    )

    app = QApplication(sys.argv)
    app.setApplicationName("LANMessenger")
    app.setOrganizationName("HomeLAN")

    # Set Application Icon
    icon_path = get_asset_path("app_icon.png")
    app.setWindowIcon(QIcon(icon_path))

    # First run setup dialog if user hasn't configured name yet
    if not config.is_configured:
        setup_dlg = SetupDialog()
        if not setup_dlg.exec():
            # User canceled initial setup
            sys.exit(0)

    # Start Background Network Engine
    engine = NetworkEngine()
    engine.start()

    # Show Main Window
    window = MainWindow(network_engine=engine)
    window.show()

    # Ensure engine stops cleanly on exit
    app.aboutToQuit.connect(engine.stop)

    # Run Qt Event Loop
    exit_code = app.exec()

    # Cleanup socket
    try:
        lock_socket.close()
    except Exception:
        pass

    sys.exit(exit_code)


if __name__ == "__main__":
    main()

