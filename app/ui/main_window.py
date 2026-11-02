import os
import time
import subprocess
from pathlib import Path
from typing import Dict, Any, Optional

from PyQt6.QtWidgets import (
    QMainWindow,
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QSplitter,
    QPushButton,
    QLabel,
    QStatusBar,
    QMessageBox,
)
from PyQt6.QtCore import Qt, pyqtSlot
from PyQt6.QtGui import QIcon, QCloseEvent

from .styles import DARK_THEME_QSS
from .peer_list import PeerListSidebar
from .chat_panel import ChatPanel
from .setup_dialog import SetupDialog
from .add_peer_dialog import AddPeerDialog
from .network_dialog import NetworkStatusDialog
from .qr_dialog import QRCodeDialog
from .playit_dialog import PlayitTunnelDialog
from .help_dialog import UserGuideDialog
from .about_dialog import AboutDialog
from .call_dialog import IncomingCallDialog, ActiveCallDialog
from .screen_viewer import ScreenShareViewer
from .tray import TrayManager
from .sound import play_message_sound, play_transfer_complete_sound
from ..config import config
from ..network.engine import NetworkEngine
from ..network.media_engine import AudioCallManager, ScreenShareManager
from ..utils.paths import get_asset_path
from ..utils.file_helper import format_size, show_in_file_manager
from ..utils.history import history


class MainWindow(QMainWindow):
    """Main Application Window for LAN Messenger."""

    def __init__(self, network_engine: NetworkEngine):
        super().__init__()
        self.engine = network_engine
        self.setWindowTitle(f"LAN Messenger — {config.username}")
        self.resize(1020, 680)
        self.setMinimumSize(780, 500)

        # Apply dark theme
        self.setStyleSheet(DARK_THEME_QSS)

        # Set App Icon
        icon_path = get_asset_path("app_icon.png")
        self.setWindowIcon(QIcon(icon_path))

        self.active_peer_ip: Optional[str] = None
        self.active_transfers: Dict[str, Any] = {}

        # Real-Time Media Managers
        self.audio_manager = AudioCallManager(self)
        self.screen_manager = ScreenShareManager(fps=15, parent=self)
        self.active_call_ip: Optional[str] = None
        self.active_call_dialog: Optional[ActiveCallDialog] = None
        self.active_screen_ip: Optional[str] = None
        self.screen_viewer: Optional[ScreenShareViewer] = None

        self.init_ui()
        self.init_tray()
        self.connect_signals()

    def init_ui(self):
        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        main_layout = QHBoxLayout(central_widget)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)

        # 1. Left Navigation Rail (62px WhatsApp/Telegram Style)
        nav_rail = QWidget()
        nav_rail.setObjectName("navRail")
        nr_layout = QVBoxLayout(nav_rail)
        nr_layout.setContentsMargins(0, 8, 0, 8)
        nr_layout.setSpacing(4)

        # Brand button
        btn_brand = QPushButton("💬")
        btn_brand.setProperty("class", "navBtnBrand")
        btn_brand.setToolTip(f"LAN Messenger v2.5 — {config.username}")
        nr_layout.addWidget(btn_brand)

        # Chats Nav button (Active)
        self.btn_nav_chats = QPushButton("💬")
        self.btn_nav_chats.setProperty("class", "navBtn navBtnActive")
        self.btn_nav_chats.setToolTip("Chats")
        nr_layout.addWidget(self.btn_nav_chats)

        # Broadcast Nav button
        self.btn_nav_broadcast = QPushButton("📢")
        self.btn_nav_broadcast.setProperty("class", "navBtn")
        self.btn_nav_broadcast.setToolTip("Group Broadcast (All Devices)")
        self.btn_nav_broadcast.clicked.connect(self._select_broadcast)
        nr_layout.addWidget(self.btn_nav_broadcast)

        # Scan LAN Nav button
        self.btn_nav_scan = QPushButton("⚡")
        self.btn_nav_scan.setProperty("class", "navBtn")
        self.btn_nav_scan.setToolTip("Scan Network for Devices (Huawei & Tenda)")
        self.btn_nav_scan.clicked.connect(self._scan_subnets)
        nr_layout.addWidget(self.btn_nav_scan)

        # Connect IP Nav button
        self.btn_nav_add = QPushButton("➕")
        self.btn_nav_add.setProperty("class", "navBtn")
        self.btn_nav_add.setToolTip("Connect PC by IP or Domain")
        self.btn_nav_add.clicked.connect(self._open_add_peer)
        nr_layout.addWidget(self.btn_nav_add)

        # Mobile QR Nav button
        self.btn_nav_mobile = QPushButton("📱")
        self.btn_nav_mobile.setProperty("class", "navBtn")
        self.btn_nav_mobile.setToolTip("Connect Mobile Phone via QR Code")
        self.btn_nav_mobile.clicked.connect(self._open_mobile_qr)
        nr_layout.addWidget(self.btn_nav_mobile)

        # Internet Link (Playit) Nav button
        self.btn_nav_playit = QPushButton("🌐")
        self.btn_nav_playit.setProperty("class", "navBtn")
        self.btn_nav_playit.setToolTip("Playit.gg Internet Link (Connect Friends Worldwide)")
        self.btn_nav_playit.clicked.connect(self._open_playit_dialog)
        nr_layout.addWidget(self.btn_nav_playit)

        # Downloads Nav button
        self.btn_nav_downloads = QPushButton("📁")
        self.btn_nav_downloads.setProperty("class", "navBtn")
        self.btn_nav_downloads.setToolTip("Open Downloads Folder")
        self.btn_nav_downloads.clicked.connect(self._open_downloads_folder)
        nr_layout.addWidget(self.btn_nav_downloads)

        nr_layout.addStretch()

        # Developer Button (Abid Developer)
        self.btn_nav_dev = QPushButton("👨‍💻")
        self.btn_nav_dev.setProperty("class", "navBtn")
        self.btn_nav_dev.setToolTip("Abid Developer Profile & Remote Hub")
        self.btn_nav_dev.clicked.connect(self._open_about_dialog)
        nr_layout.addWidget(self.btn_nav_dev)

        # User Guide
        self.btn_nav_guide = QPushButton("📖")
        self.btn_nav_guide.setProperty("class", "navBtn")
        self.btn_nav_guide.setToolTip("User Guide & Documentation")
        self.btn_nav_guide.clicked.connect(self._open_user_guide)
        nr_layout.addWidget(self.btn_nav_guide)

        # Settings
        self.btn_nav_settings = QPushButton("⚙️")
        self.btn_nav_settings.setProperty("class", "navBtn")
        self.btn_nav_settings.setToolTip("Settings & Profile")
        self.btn_nav_settings.clicked.connect(self._open_settings)
        nr_layout.addWidget(self.btn_nav_settings)

        main_layout.addWidget(nav_rail)

        # 2. Central Splitter (Sidebar + Chat Panel)
        self.splitter = QSplitter(Qt.Orientation.Horizontal)
        self.splitter.setHandleWidth(1)

        self.sidebar = PeerListSidebar()
        self.sidebar.sig_peer_selected.connect(self._on_peer_selected)
        self.sidebar.sig_quick_scan.connect(self._scan_subnets)
        self.sidebar.sig_quick_add.connect(self._open_add_peer)
        self.splitter.addWidget(self.sidebar)

        self.chat_panel = ChatPanel()
        self.chat_panel.sig_send_text.connect(self._on_send_text)
        self.chat_panel.sig_send_file.connect(self._on_send_file)
        self.chat_panel.sig_start_call.connect(self._start_call)
        self.chat_panel.sig_start_screenshare.connect(self._start_screenshare)
        self.splitter.addWidget(self.chat_panel)

        self.splitter.setSizes([310, 710])
        main_layout.addWidget(self.splitter, 1)

        # 3. Modern Status Bar
        self.status_bar = QStatusBar()
        self.setStatusBar(self.status_bar)

        self.lbl_status_ip = QLabel("Starting network engine...")
        self.lbl_status_peers = QLabel("0 devices found")
        self.lbl_dev_brand = QPushButton("👨‍💻 Abid Developer")
        self.lbl_dev_brand.setToolTip("Click to view Abid Developer profile & remote links")
        self.lbl_dev_brand.setStyleSheet(
            "color: #00a884; font-size: 11px; font-weight: bold; background: transparent; border: none; padding-right: 10px;"
        )
        self.lbl_dev_brand.setCursor(Qt.CursorShape.PointingHandCursor)
        self.lbl_dev_brand.clicked.connect(self._open_about_dialog)

        self.status_bar.addWidget(self.lbl_status_ip, 1)
        self.status_bar.addPermanentWidget(self.lbl_dev_brand)
        self.status_bar.addPermanentWidget(self.lbl_status_peers)

    def init_tray(self):
        self.tray = TrayManager(self)
        self.tray.sig_show_window.connect(self._restore_window)
        self.tray.sig_open_downloads.connect(self._open_downloads_folder)
        self.tray.sig_open_settings.connect(self._open_settings)
        self.tray.sig_scan_network.connect(self._scan_subnets)
        self.tray.sig_exit_app.connect(self._force_exit)

    def connect_signals(self):
        # Network Engine Signals
        self.engine.sig_engine_ready.connect(self._on_engine_ready)
        self.engine.sig_peer_discovered.connect(self._on_peer_discovered)
        self.engine.sig_peer_status.connect(self._on_peer_status_changed)
        self.engine.sig_text_received.connect(self._on_text_received)
        self.engine.sig_file_progress.connect(self._on_file_progress)
        self.engine.sig_file_received.connect(self._on_file_received)
        self.engine.sig_file_sent.connect(self._on_file_sent)
        self.engine.sig_sweep_completed.connect(self._on_sweep_completed)

        # Media Event Signals
        self.engine.sig_call_request.connect(self._on_incoming_call)
        self.engine.sig_call_accepted.connect(self._on_call_accepted)
        self.engine.sig_call_rejected.connect(self._on_call_rejected)
        self.engine.sig_call_ended.connect(self._on_call_ended)
        self.engine.sig_audio_frame.connect(self._on_incoming_audio_frame)
        self.engine.sig_screen_started.connect(self._on_incoming_screen_start)
        self.engine.sig_screen_frame.connect(self._on_incoming_screen_frame)
        self.engine.sig_screen_stopped.connect(self._on_incoming_screen_stop)

        # Media Engine Frame Signals
        self.audio_manager.sig_audio_frame_ready.connect(
            self._send_local_audio_frame
        )
        self.screen_manager.sig_screen_frame_ready.connect(
            self._send_local_screen_frame
        )

    @pyqtSlot(str, int)
    def _on_engine_ready(self, local_ip: str, port: int):
        self.lbl_status_ip.setText(
            f"🟢 Online @ {local_ip}:{port} • Subnets: {', '.join(config.custom_subnets)}"
        )

    @pyqtSlot(dict)
    def _on_peer_discovered(self, peer_info: Dict[str, Any]):
        self.sidebar.add_or_update_peer(peer_info)
        count = len(self.sidebar.peer_widgets)
        self.lbl_status_peers.setText(f"{count} device(s) registered")

    @pyqtSlot(str, str)
    def _on_peer_status_changed(self, ip: str, status: str):
        self.sidebar.update_peer_status(ip, status)
        if self.active_peer_ip == ip:
            username = (
                self.sidebar.peer_widgets[ip].username
                if ip in self.sidebar.peer_widgets
                else ip
            )
            self.chat_panel.lbl_peer_status.setText(
                f"{ip} • {'🟢 Online' if status == 'online' else '⚪ Offline'}"
            )

    @pyqtSlot(str)
    def _on_peer_selected(self, ip: str):
        self.active_peer_ip = ip
        widget = self.sidebar.peer_widgets.get(ip)
        username = widget.username if widget else f"Peer @ {ip}"
        status = widget.status if widget else "online"

        self.chat_panel.set_active_peer(ip, username, status)

        # Load persisted history
        msgs = history.get_messages(ip)
        for m in msgs:
            if m.get("type") == "file":
                finfo = m.get("file_info", {})
                self.chat_panel.add_file_bubble(
                    filename=finfo.get("filename", "file"),
                    filesize=finfo.get("filesize", 0),
                    filepath=finfo.get("filepath", ""),
                    is_outgoing=m.get("is_outgoing", False),
                    timestamp=m.get("timestamp", time.time()),
                    is_completed=True,
                )
            else:
                self.chat_panel.add_text_bubble(
                    text=m.get("text", ""),
                    timestamp=m.get("timestamp", time.time()),
                    is_outgoing=m.get("is_outgoing", False),
                    sender_name=m.get("sender", ""),
                )

    @pyqtSlot(str, str)
    def _on_send_text(self, peer_ip: str, text: str):
        self.engine.send_text(peer_ip, text)
        history.add_message(
            peer_ip=peer_ip,
            sender=config.username,
            text=text,
            is_outgoing=True,
            msg_type="text",
        )
        self.sidebar.update_last_message(peer_ip, f"You: {text}", is_active_chat=True)

    @pyqtSlot(str, str, float)
    def _on_text_received(self, peer_ip: str, text: str, timestamp: float):
        peer_widget = self.sidebar.peer_widgets.get(peer_ip)
        sender_name = peer_widget.username if peer_widget else f"PC @ {peer_ip}"

        history.add_message(
            peer_ip=peer_ip,
            sender=sender_name,
            text=text,
            is_outgoing=False,
            msg_type="text",
        )

        is_active = self.active_peer_ip in [peer_ip, "BROADCAST"]
        self.sidebar.update_last_message(
            peer_ip, f"{sender_name}: {text}", is_active_chat=is_active
        )

        if is_active:
            self.chat_panel.add_text_bubble(
                text=text,
                timestamp=timestamp,
                is_outgoing=False,
                sender_name=sender_name,
            )

        play_message_sound()

        # If window is minimized or not active, show Windows Toast Notification
        if not self.isActiveWindow() or not is_active:
            self.tray.show_notification(
                f"New Message from {sender_name}",
                text if len(text) <= 80 else text[:77] + "...",
            )

    @pyqtSlot(str, str)
    def _on_send_file(self, peer_ip: str, filepath: str):
        path = Path(filepath)
        filename = path.name
        filesize = path.stat().st_size

        self.engine.send_file(peer_ip, filepath)

        bubble = self.chat_panel.add_file_bubble(
            filename=filename,
            filesize=filesize,
            filepath=filepath,
            is_outgoing=True,
            timestamp=time.time(),
            is_completed=False,
        )

    @pyqtSlot(str, str, str, int)
    def _on_file_sent(self, peer_ip: str, filepath: str, filename: str, filesize: int):
        history.add_message(
            peer_ip=peer_ip,
            sender=config.username,
            text=f"📎 Sent {filename} ({format_size(filesize)})",
            is_outgoing=True,
            msg_type="file",
            file_info={
                "filename": filename,
                "filesize": filesize,
                "filepath": filepath,
            },
        )
        play_transfer_complete_sound()

    @pyqtSlot(str, int, int, float, bool)
    def _on_file_progress(
        self,
        transfer_id: str,
        done: int,
        total: int,
        speed_mbps: float,
        is_upload: bool,
    ):
        self.chat_panel.update_file_progress(transfer_id, done, total, speed_mbps)

    @pyqtSlot(str, str, str, int)
    def _on_file_received(
        self, peer_ip: str, filepath: str, filename: str, filesize: int
    ):
        peer_widget = self.sidebar.peer_widgets.get(peer_ip)
        sender_name = peer_widget.username if peer_widget else f"PC @ {peer_ip}"

        history.add_message(
            peer_ip=peer_ip,
            sender=sender_name,
            text=f"📎 Received {filename} ({format_size(filesize)})",
            is_outgoing=False,
            msg_type="file",
            file_info={
                "filename": filename,
                "filesize": filesize,
                "filepath": filepath,
            },
        )

        is_active = self.active_peer_ip in [peer_ip, "BROADCAST"]
        if is_active:
            self.chat_panel.add_file_bubble(
                filename=filename,
                filesize=filesize,
                filepath=filepath,
                is_outgoing=False,
                timestamp=time.time(),
                is_completed=True,
                sender_name=sender_name,
            )

        self.sidebar.update_last_message(
            peer_ip, f"📎 {filename}", is_active_chat=is_active
        )
        play_transfer_complete_sound()

        # Toast notification
        self.tray.show_notification(
            f"File Received from {sender_name}",
            f"{filename} ({format_size(filesize)})\nSaved to Downloads/LANMessenger",
        )

    # Navigation / Dialog Handlers
    # Voice Call and Screen Share Handlers
    def _start_call(self, peer_ip: str):
        self.active_call_ip = peer_ip
        widget = self.sidebar.peer_widgets.get(peer_ip)
        peer_name = widget.username if widget else peer_ip
        avatar_id = widget.avatar_id if widget else "gamer"

        self.engine.request_call(peer_ip)

        self.active_call_dialog = ActiveCallDialog(
            peer_name=peer_name, avatar_id=avatar_id, parent=self
        )
        self.active_call_dialog.sig_hangup.connect(self._hangup_call)
        self.active_call_dialog.sig_toggle_mute.connect(
            self.audio_manager.set_muted
        )
        self.active_call_dialog.show()

    def _on_incoming_call(self, peer_ip: str, data: dict):
        caller_name = data.get("caller", f"PC @ {peer_ip}")
        dlg = IncomingCallDialog(
            caller_name=caller_name, caller_ip=peer_ip, parent=self
        )
        if dlg.exec():
            # Accepted
            self.active_call_ip = peer_ip
            self.engine.accept_call(peer_ip)
            self.audio_manager.start_call()

            self.active_call_dialog = ActiveCallDialog(
                peer_name=caller_name, parent=self
            )
            self.active_call_dialog.sig_hangup.connect(self._hangup_call)
            self.active_call_dialog.sig_toggle_mute.connect(
                self.audio_manager.set_muted
            )
            self.active_call_dialog.show()
        else:
            # Declined
            self.engine.reject_call(peer_ip)

    def _on_call_accepted(self, peer_ip: str):
        self.audio_manager.start_call()

    def _on_call_rejected(self, peer_ip: str):
        self.audio_manager.stop_call()
        if self.active_call_dialog:
            self.active_call_dialog.close()
            self.active_call_dialog = None
        QMessageBox.information(
            self, "Call Declined", f"The call to {peer_ip} was declined."
        )

    def _on_call_ended(self, peer_ip: str):
        self.audio_manager.stop_call()
        if self.active_call_dialog:
            self.active_call_dialog.close()
            self.active_call_dialog = None
        self.active_call_ip = None

    def _hangup_call(self):
        if self.active_call_ip:
            self.engine.end_call(self.active_call_ip)
            self.audio_manager.stop_call()
            self.active_call_ip = None

    def _send_local_audio_frame(self, pcm_bytes: bytes):
        if self.active_call_ip:
            self.engine.send_audio_chunk(self.active_call_ip, pcm_bytes)

    def _on_incoming_audio_frame(self, peer_ip: str, pcm_bytes: bytes):
        self.audio_manager.play_audio_chunk(pcm_bytes)

    # Screen Sharing Handlers
    def _start_screenshare(self, peer_ip: str):
        reply = QMessageBox.question(
            self,
            "Share Screen",
            f"Are you sure you want to share your live screen with {peer_ip}?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
        )
        if reply == QMessageBox.StandardButton.Yes:
            self.active_screen_ip = peer_ip
            self.engine.start_screen_share(peer_ip)
            self.screen_manager.start_sharing()
            self.lbl_status_ip.setText(
                f"🖥️ Live Screen Sharing active with {peer_ip} (15 FPS)"
            )

    def _send_local_screen_frame(self, jpeg_bytes: bytes):
        if self.active_screen_ip:
            self.engine.send_screen_chunk(self.active_screen_ip, jpeg_bytes)
        self.screen_manager.frame_sent()

    def _on_incoming_screen_start(self, peer_ip: str, data: dict):
        sharer_name = data.get("sharer", f"PC @ {peer_ip}")
        if self.screen_viewer:
            self.screen_viewer.close()

        self.screen_viewer = ScreenShareViewer(sharer_name=sharer_name)
        self.screen_viewer.sig_viewer_closed.connect(
            lambda: self.engine.stop_screen_share(peer_ip)
        )
        self.screen_viewer.show()

    def _on_incoming_screen_frame(self, peer_ip: str, jpeg_bytes: bytes):
        if self.screen_viewer:
            self.screen_viewer.update_frame(jpeg_bytes)

    def _on_incoming_screen_stop(self, peer_ip: str):
        if self.screen_viewer:
            self.screen_viewer.close()
            self.screen_viewer = None
        if self.active_screen_ip == peer_ip:
            self.screen_manager.stop_sharing()
            self.active_screen_ip = None

    def _select_broadcast(self):
        self.sidebar.select_peer("BROADCAST")
        self._on_peer_selected("BROADCAST")

    def _open_add_peer(self):
        dlg = AddPeerDialog(self, network_engine=self.engine)
        dlg.sig_peer_selected.connect(self._on_peer_selected)
        dlg.exec()

    def _scan_subnets(self):
        self.btn_nav_scan.setEnabled(False)
        self.lbl_status_ip.setText("⚡ Scanning both subnets (192.168.100.x & 192.168.7.x)...")
        self.engine.scan_subnets()

    @pyqtSlot(int)
    def _on_sweep_completed(self, count: int):
        self.btn_nav_scan.setEnabled(True)
        self.lbl_status_ip.setText(
            f"🟢 Online • Scan complete: {count} active device(s) found"
        )

    def _open_downloads_folder(self):
        path = config.download_dir
        Path(path).mkdir(parents=True, exist_ok=True)
        if os.name == "nt":
            os.startfile(path)
        else:
            subprocess.Popen(["xdg-open", path])

    def _open_network_info(self):
        dlg = NetworkStatusDialog(self)
        dlg.exec()

    def _open_mobile_qr(self):
        dlg = QRCodeDialog(port=9878, parent=self)
        dlg.exec()

    def _open_playit_dialog(self):
        dlg = PlayitTunnelDialog(self)
        dlg.exec()

    def _open_user_guide(self):
        dlg = UserGuideDialog(self)
        dlg.exec()

    def _open_about_dialog(self):
        dlg = AboutDialog(self)
        dlg.sig_connect_hub.connect(self._on_connect_hub_requested)
        dlg.exec()

    def _on_connect_hub_requested(self, hub_addr: str):
        self.engine.add_manual_peer(hub_addr)
        self.active_peer_ip = hub_addr
        self.sidebar.add_or_update_peer({
            "ip": hub_addr,
            "username": "Abid Developer Hub",
            "port": 9876,
            "status": "online",
        })
        self.sidebar.select_peer(hub_addr)

    def _open_settings(self):
        dlg = SetupDialog(self, is_settings_mode=True)
        if dlg.exec():
            self.setWindowTitle(f"LAN Messenger — {config.username}")
            self.engine.update_username(config.username)

    def _restore_window(self):
        self.show()
        self.setWindowState(
            self.windowState() & ~Qt.WindowState.WindowMinimized
            | Qt.WindowState.WindowActive
        )
        self.raise_()
        self.activateWindow()

    def _force_exit(self):
        self.engine.stop()
        self.tray.tray_icon.hide()
        self.close()

    def closeEvent(self, event: QCloseEvent):
        if config.minimize_to_tray:
            event.ignore()
            self.hide()
            self.tray.show_notification(
                "LAN Messenger",
                "App minimized to system tray. Double-click tray icon to open.",
            )
        else:
            self.engine.stop()
            self.tray.tray_icon.hide()
            event.accept()

