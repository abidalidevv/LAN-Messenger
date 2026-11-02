import os
import time
import tempfile
from typing import Dict, Any, Optional
from pathlib import Path

from PyQt6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QPushButton,
    QScrollArea,
    QFileDialog,
    QProgressBar,
    QFrame,
    QApplication,
    QMessageBox,
)
from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QDragEnterEvent, QDropEvent, QPixmap, QImage

from ..utils.file_helper import (
    format_size,
    get_file_category,
    open_file_default,
    show_in_file_manager,
)

CATEGORY_ICONS = {
    "image": "🖼️",
    "video": "🎥",
    "audio": "🎵",
    "pdf": "📄",
    "archive": "📦",
    "document": "📝",
    "executable": "⚙️",
    "file": "📎",
}


class MessageBubble(QWidget):
    """Authentic WhatsApp Desktop styled chat bubble."""

    def __init__(
        self,
        text: str,
        timestamp: float,
        is_outgoing: bool,
        sender_name: str = "",
        parent=None,
    ):
        super().__init__(parent)
        self.is_outgoing = is_outgoing

        layout = QHBoxLayout(self)
        layout.setContentsMargins(16, 2, 16, 2)

        bubble_container = QFrame()
        bubble_container.setMaximumWidth(540)

        # WhatsApp signature colors and corner tails
        bg_color = "#005c4b" if is_outgoing else "#202c33"
        border_radius = "14px 14px 3px 14px" if is_outgoing else "14px 14px 14px 3px"
        bubble_container.setStyleSheet(
            f"background-color: {bg_color}; border-radius: {border_radius}; padding: 7px 12px;"
        )

        b_layout = QVBoxLayout(bubble_container)
        b_layout.setContentsMargins(2, 2, 2, 2)
        b_layout.setSpacing(3)

        if not is_outgoing and sender_name:
            lbl_sender = QLabel(sender_name)
            lbl_sender.setStyleSheet(
                "font-size: 11px; font-weight: bold; color: #53bdeb; margin-bottom: 2px;"
            )
            b_layout.addWidget(lbl_sender)

        lbl_text = QLabel(text)
        lbl_text.setWordWrap(True)
        lbl_text.setTextInteractionFlags(Qt.TextInteractionFlag.TextSelectableByMouse)
        lbl_text.setStyleSheet("color: #e9edef; font-size: 14px; line-height: 1.35;")
        b_layout.addWidget(lbl_text)

        # Timestamp + WhatsApp Double Checkmarks
        time_row = QHBoxLayout()
        time_row.setContentsMargins(0, 0, 0, 0)
        time_row.setSpacing(4)
        time_row.addStretch()

        time_str = time.strftime("%I:%M %p", time.localtime(timestamp))
        lbl_time = QLabel(time_str)
        lbl_time.setStyleSheet("font-size: 11px; color: #8696a0;")
        time_row.addWidget(lbl_time)

        if is_outgoing:
            lbl_checks = QLabel("✓✓")
            lbl_checks.setStyleSheet(
                "color: #53bdeb; font-size: 11px; font-weight: bold; margin-left: 2px;"
            )
            time_row.addWidget(lbl_checks)

        b_layout.addLayout(time_row)

        if is_outgoing:
            layout.addStretch()
            layout.addWidget(bubble_container)
        else:
            layout.addWidget(bubble_container)
            layout.addStretch()


class FileBubble(QWidget):
    """Modern WhatsApp file card with thumbnail preview and progress animation."""

    def __init__(
        self,
        filename: str,
        filesize: int,
        filepath: str,
        is_outgoing: bool,
        timestamp: float,
        transfer_id: str = "",
        is_completed: bool = True,
        sender_name: str = "",
        parent=None,
    ):
        super().__init__(parent)
        self.filename = filename
        self.filesize = filesize
        self.filepath = filepath
        self.is_outgoing = is_outgoing
        self.transfer_id = transfer_id

        layout = QHBoxLayout(self)
        layout.setContentsMargins(16, 4, 16, 4)

        card = QFrame()
        card.setMaximumWidth(480)
        bg_color = "#005c4b" if is_outgoing else "#202c33"
        border_radius = "14px 14px 3px 14px" if is_outgoing else "14px 14px 14px 3px"
        card.setStyleSheet(
            f"background-color: {bg_color}; border-radius: {border_radius}; padding: 10px 14px;"
        )

        c_layout = QVBoxLayout(card)
        c_layout.setContentsMargins(2, 2, 2, 2)
        c_layout.setSpacing(6)

        if not is_outgoing and sender_name:
            lbl_sender = QLabel(sender_name)
            lbl_sender.setStyleSheet(
                "font-size: 11px; font-weight: bold; color: #53bdeb;"
            )
            c_layout.addWidget(lbl_sender)

        # Image In-Chat Thumbnail Preview
        self.lbl_thumb = QLabel()
        self.lbl_thumb.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.lbl_thumb.setCursor(Qt.CursorShape.PointingHandCursor)
        self.lbl_thumb.mousePressEvent = lambda e: self._open_file()
        self.lbl_thumb.setStyleSheet("border-radius: 8px; margin-bottom: 4px;")
        self.lbl_thumb.setVisible(False)
        c_layout.addWidget(self.lbl_thumb)

        if is_completed and self.filepath:
            self._load_thumbnail()

        # File header row
        header_row = QHBoxLayout()
        header_row.setSpacing(10)
        cat = get_file_category(filename)
        icon = CATEGORY_ICONS.get(cat, "📎")
        
        lbl_icon = QLabel(icon)
        lbl_icon.setStyleSheet(
            "font-size: 24px; background: rgba(0, 0, 0, 0.2); "
            "border-radius: 8px; padding: 6px;"
        )
        header_row.addWidget(lbl_icon)

        info_col = QVBoxLayout()
        info_col.setSpacing(2)
        lbl_name = QLabel(filename)
        lbl_name.setStyleSheet("font-weight: 600; font-size: 13px; color: #e9edef;")
        self.lbl_sub = QLabel(f"{format_size(filesize)}")
        self.lbl_sub.setStyleSheet("font-size: 11px; color: #8696a0;")
        info_col.addWidget(lbl_name)
        info_col.addWidget(self.lbl_sub)
        header_row.addLayout(info_col, 1)

        c_layout.addLayout(header_row)

        # Progress bar
        self.progress_bar = QProgressBar()
        self.progress_bar.setRange(0, 100)
        self.progress_bar.setValue(100 if is_completed else 0)
        self.progress_bar.setVisible(not is_completed)
        c_layout.addWidget(self.progress_bar)

        # Action buttons row
        self.btn_row = QHBoxLayout()
        self.btn_row.setSpacing(8)

        self.btn_open = QPushButton("Open File")
        self.btn_open.setStyleSheet(
            "background-color: rgba(255, 255, 255, 0.08); color: #e9edef; font-size: 12px; "
            "padding: 5px 12px; border-radius: 6px; border: none; font-weight: 500;"
        )
        self.btn_open.clicked.connect(self._open_file)

        self.btn_folder = QPushButton("Show in Folder")
        self.btn_folder.setStyleSheet(
            "background-color: rgba(255, 255, 255, 0.08); color: #e9edef; font-size: 12px; "
            "padding: 5px 12px; border-radius: 6px; border: none; font-weight: 500;"
        )
        self.btn_folder.clicked.connect(self._show_folder)

        self.btn_row.addWidget(self.btn_open)
        self.btn_row.addWidget(self.btn_folder)
        self.btn_row.addStretch()

        # Timestamp + Checks
        time_str = time.strftime("%I:%M %p", time.localtime(timestamp))
        lbl_time = QLabel(time_str)
        lbl_time.setStyleSheet("font-size: 11px; color: #8696a0;")
        self.btn_row.addWidget(lbl_time)

        if is_outgoing:
            lbl_checks = QLabel("✓✓")
            lbl_checks.setStyleSheet(
                "color: #53bdeb; font-size: 11px; font-weight: bold; margin-left: 2px;"
            )
            self.btn_row.addWidget(lbl_checks)

        c_layout.addLayout(self.btn_row)

        if not is_completed:
            self.btn_open.setEnabled(False)
            self.btn_folder.setEnabled(False)

        if is_outgoing:
            layout.addStretch()
            layout.addWidget(card)
        else:
            layout.addWidget(card)
            layout.addStretch()

    def _load_thumbnail(self):
        cat = get_file_category(self.filename)
        if cat == "image" and os.path.exists(self.filepath):
            try:
                pixmap = QPixmap(self.filepath)
                if not pixmap.isNull():
                    scaled = pixmap.scaled(
                        280,
                        190,
                        Qt.AspectRatioMode.KeepAspectRatio,
                        Qt.TransformationMode.SmoothTransformation,
                    )
                    self.lbl_thumb.setPixmap(scaled)
                    self.lbl_thumb.setVisible(True)
            except Exception:
                pass

    def update_progress(self, done: int, total: int, speed_mbps: float):
        if total > 0:
            pct = int((done / total) * 100)
            self.progress_bar.setValue(pct)
            self.lbl_sub.setText(
                f"{format_size(done)} / {format_size(total)} ({speed_mbps:.1f} MB/s)"
            )

    def mark_completed(self, final_filepath: str):
        self.filepath = final_filepath
        self.progress_bar.setValue(100)
        self.progress_bar.setVisible(False)
        self.lbl_sub.setText(f"{format_size(self.filesize)} • Completed")
        self.btn_open.setEnabled(True)
        self.btn_folder.setEnabled(True)
        self._load_thumbnail()

    def _open_file(self):
        if self.filepath:
            open_file_default(self.filepath)

    def _show_folder(self):
        if self.filepath:
            show_in_file_manager(self.filepath)


class ChatPanel(QWidget):
    """WhatsApp Desktop style main Chat Panel with Empty State, Header, Bubbles, and Input."""

    sig_send_text = pyqtSignal(str, str)
    sig_send_file = pyqtSignal(str, str)
    sig_start_call = pyqtSignal(str)
    sig_start_screenshare = pyqtSignal(str)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("chatContainer")
        self.current_peer_ip: Optional[str] = None
        self.current_peer_name: str = ""
        self.file_bubbles: Dict[str, FileBubble] = {}

        self.setAcceptDrops(True)
        self.init_ui()

    def init_ui(self):
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)

        # 1. Top Chat Header
        self.header_frame = QFrame()
        self.header_frame.setObjectName("chatHeader")
        header_layout = QHBoxLayout(self.header_frame)
        header_layout.setContentsMargins(18, 6, 18, 6)
        header_layout.setSpacing(12)

        # Peer Avatar in Header
        self.hdr_avatar = QLabel()
        self.hdr_avatar.setFixedSize(38, 38)
        self.hdr_avatar.setStyleSheet(
            "background: qlineargradient(x1:0, y1:0, x2:1, y2:1, stop:0 #00a884, stop:1 #005c4b); "
            "color: white; border-radius: 19px; font-size: 18px; qproperty-alignment: AlignCenter;"
        )
        self.hdr_avatar.setText("💬")
        header_layout.addWidget(self.hdr_avatar)

        # Name and Status Subtitle
        col = QVBoxLayout()
        col.setSpacing(2)
        self.lbl_peer_name = QLabel("Select a device to start chat")
        self.lbl_peer_name.setStyleSheet(
            "font-size: 15px; font-weight: 600; color: #e9edef;"
        )
        self.lbl_peer_status = QLabel("Ready for high-speed transfers")
        self.lbl_peer_status.setStyleSheet("font-size: 11px; color: #8696a0;")
        col.addWidget(self.lbl_peer_name)
        col.addWidget(self.lbl_peer_status)
        header_layout.addLayout(col)
        header_layout.addStretch()

        # Action Buttons in Header
        self.btn_call = QPushButton("📞")
        self.btn_call.setObjectName("btnCall")
        self.btn_call.setProperty("class", "chatHeaderBtn")
        self.btn_call.setToolTip("Start Crystal HD Voice Call")
        self.btn_call.clicked.connect(self._on_call_clicked)
        self.btn_call.setVisible(False)
        header_layout.addWidget(self.btn_call)

        self.btn_screen = QPushButton("🖥️")
        self.btn_screen.setObjectName("btnScreen")
        self.btn_screen.setProperty("class", "chatHeaderBtn")
        self.btn_screen.setToolTip("Start Live 15 FPS Screen Share")
        self.btn_screen.clicked.connect(self._on_screen_clicked)
        self.btn_screen.setVisible(False)
        header_layout.addWidget(self.btn_screen)

        self.btn_quick_file = QPushButton("📎")
        self.btn_quick_file.setObjectName("btnQuickFile")
        self.btn_quick_file.setProperty("class", "chatHeaderBtn")
        self.btn_quick_file.setToolTip("Send File or 4K Video")
        self.btn_quick_file.clicked.connect(self._on_attach_clicked)
        self.btn_quick_file.setVisible(False)
        header_layout.addWidget(self.btn_quick_file)

        main_layout.addWidget(self.header_frame)

        # 2. Main Center Area (Stacked: Empty State Splash OR Scroll Area)
        self.center_container = QWidget()
        center_layout = QVBoxLayout(self.center_container)
        center_layout.setContentsMargins(0, 0, 0, 0)
        center_layout.setSpacing(0)

        # Empty State Splash Screen (WhatsApp Web style)
        self.splash_screen = QWidget()
        splash_layout = QVBoxLayout(self.splash_screen)
        splash_layout.setContentsMargins(40, 40, 40, 40)
        splash_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        splash_layout.setSpacing(14)

        splash_icon = QLabel("💬")
        splash_icon.setStyleSheet(
            "font-size: 64px; background: #202c33; border-radius: 50px; "
            "min-width: 100px; max-width: 100px; min-height: 100px; max-height: 100px; "
            "qproperty-alignment: AlignCenter;"
        )
        splash_layout.addWidget(splash_icon, alignment=Qt.AlignmentFlag.AlignCenter)

        splash_title = QLabel("LAN Messenger for Windows")
        splash_title.setStyleSheet("font-size: 24px; font-weight: bold; color: #e9edef;")
        splash_layout.addWidget(splash_title, alignment=Qt.AlignmentFlag.AlignCenter)

        splash_desc = QLabel(
            "Send and receive messages and uncompressed 4K files with zero internet.<br>"
            "Wire speeds up to <b>215+ MB/s</b>, crystal HD voice calls & live screen sharing."
        )
        splash_desc.setAlignment(Qt.AlignmentFlag.AlignCenter)
        splash_desc.setStyleSheet("color: #8696a0; font-size: 13px; line-height: 1.5;")
        splash_layout.addWidget(splash_desc, alignment=Qt.AlignmentFlag.AlignCenter)

        splash_lock = QLabel("🔒  End-to-end private on local network")
        splash_lock.setStyleSheet("color: #667781; font-size: 12px; margin-top: 10px;")
        splash_layout.addWidget(splash_lock, alignment=Qt.AlignmentFlag.AlignCenter)

        center_layout.addWidget(self.splash_screen)

        # Message Scroll Area
        self.scroll_area = QScrollArea()
        self.scroll_area.setObjectName("chatScrollArea")
        self.scroll_area.setWidgetResizable(True)
        self.scroll_area.setHorizontalScrollBarPolicy(
            Qt.ScrollBarPolicy.ScrollBarAlwaysOff
        )
        self.scroll_area.setVisible(False)

        self.content_widget = QWidget()
        self.content_widget.setObjectName("chatContent")
        self.content_layout = QVBoxLayout(self.content_widget)
        self.content_layout.setContentsMargins(18, 18, 18, 18)
        self.content_layout.setSpacing(6)
        self.content_layout.addStretch()

        self.scroll_area.setWidget(self.content_widget)
        center_layout.addWidget(self.scroll_area, 1)

        main_layout.addWidget(self.center_container, 1)

        # 3. Drag and Drop Banner
        self.drag_banner = QLabel("⬇️  Drop files here to send instantly!")
        self.drag_banner.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.drag_banner.setStyleSheet(
            "background: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #00a884, stop:1 #06cf9c); "
            "color: #111b21; font-weight: bold; padding: 10px; font-size: 14px;"
        )
        self.drag_banner.setVisible(False)
        main_layout.addWidget(self.drag_banner)

        # 4. Input Box Container (WhatsApp Style Pill)
        self.input_container = QFrame()
        self.input_container.setObjectName("inputContainer")
        input_layout = QHBoxLayout(self.input_container)
        input_layout.setContentsMargins(14, 8, 14, 8)
        input_layout.setSpacing(8)

        self.btn_attach = QPushButton("📎")
        self.btn_attach.setProperty("class", "inputActionBtn")
        self.btn_attach.setToolTip("Attach File, 4K Video, Image or Folder")
        self.btn_attach.clicked.connect(self._on_attach_clicked)
        input_layout.addWidget(self.btn_attach)

        self.btn_clipboard = QPushButton("📋")
        self.btn_clipboard.setProperty("class", "inputActionBtn")
        self.btn_clipboard.setToolTip("Send Clipboard Text or Screenshot directly")
        self.btn_clipboard.clicked.connect(self._on_clipboard_clicked)
        input_layout.addWidget(self.btn_clipboard)

        self.text_input = QLineEdit()
        self.text_input.setObjectName("messageInput")
        self.text_input.setPlaceholderText("Type a message...")
        self.text_input.returnPressed.connect(self._on_send_clicked)
        input_layout.addWidget(self.text_input, 1)

        self.btn_send = QPushButton("➤")
        self.btn_send.setObjectName("btnSend")
        self.btn_send.setToolTip("Send Message")
        self.btn_send.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_send.clicked.connect(self._on_send_clicked)
        input_layout.addWidget(self.btn_send)

        main_layout.addWidget(self.input_container)

        self.set_chat_enabled(False)

    def set_chat_enabled(self, enabled: bool):
        self.input_container.setEnabled(enabled)
        is_direct_peer = enabled and self.current_peer_ip != "BROADCAST"
        self.btn_call.setVisible(is_direct_peer)
        self.btn_screen.setVisible(is_direct_peer)
        self.btn_quick_file.setVisible(enabled)
        self.splash_screen.setVisible(not enabled)
        self.scroll_area.setVisible(enabled)

    def _on_call_clicked(self):
        if self.current_peer_ip and self.current_peer_ip != "BROADCAST":
            self.sig_start_call.emit(self.current_peer_ip)

    def _on_screen_clicked(self):
        if self.current_peer_ip and self.current_peer_ip != "BROADCAST":
            self.sig_start_screenshare.emit(self.current_peer_ip)

    def set_active_peer(self, ip: str, username: str, status: str = "online"):
        self.current_peer_ip = ip
        self.current_peer_name = username
        self.lbl_peer_name.setText(username)

        if ip == "BROADCAST":
            self.hdr_avatar.setText("📢")
            self.lbl_peer_status.setText(
                "📢 Broadcast Channel • Reaches all PCs, laptops & mobiles"
            )
        else:
            self.hdr_avatar.setText("💻")
            status_text = "🟢 Online" if status == "online" else "⚪ Offline"
            self.lbl_peer_status.setText(f"{ip} • {status_text}")

        self.set_chat_enabled(True)
        self.clear_bubbles()

    def clear_bubbles(self):
        while self.content_layout.count() > 1:
            item = self.content_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()
        self.file_bubbles.clear()

    def add_text_bubble(
        self, text: str, timestamp: float, is_outgoing: bool, sender_name: str = ""
    ):
        bubble = MessageBubble(
            text=text,
            timestamp=timestamp,
            is_outgoing=is_outgoing,
            sender_name=sender_name,
        )
        self.content_layout.insertWidget(self.content_layout.count() - 1, bubble)
        self._scroll_to_bottom()

    def add_file_bubble(
        self,
        filename: str,
        filesize: int,
        filepath: str,
        is_outgoing: bool,
        timestamp: float,
        transfer_id: str = "",
        is_completed: bool = True,
        sender_name: str = "",
    ) -> FileBubble:
        bubble = FileBubble(
            filename=filename,
            filesize=filesize,
            filepath=filepath,
            is_outgoing=is_outgoing,
            timestamp=timestamp,
            transfer_id=transfer_id,
            is_completed=is_completed,
            sender_name=sender_name,
        )
        self.content_layout.insertWidget(self.content_layout.count() - 1, bubble)
        if transfer_id:
            self.file_bubbles[transfer_id] = bubble
        self._scroll_to_bottom()
        return bubble

    def update_file_progress(
        self, transfer_id: str, done: int, total: int, speed_mbps: float
    ):
        if transfer_id in self.file_bubbles:
            self.file_bubbles[transfer_id].update_progress(done, total, speed_mbps)

    def complete_file_transfer(self, transfer_id: str, final_filepath: str):
        if transfer_id in self.file_bubbles:
            self.file_bubbles[transfer_id].mark_completed(final_filepath)

    def _scroll_to_bottom(self):
        QApplication.processEvents()
        sb = self.scroll_area.verticalScrollBar()
        if sb:
            sb.setValue(sb.maximum())

    def _on_send_clicked(self):
        text = self.text_input.text().strip()
        if text and self.current_peer_ip:
            self.sig_send_text.emit(self.current_peer_ip, text)
            self.text_input.clear()

    def _on_attach_clicked(self):
        if not self.current_peer_ip:
            return
        files, _ = QFileDialog.getOpenFileNames(
            self, "Select Files to Send via LAN", "", "All Files (*.*)"
        )
        for filepath in files:
            if filepath:
                self.sig_send_file.emit(self.current_peer_ip, filepath)

    def _on_clipboard_clicked(self):
        if not self.current_peer_ip:
            return

        cb = QApplication.clipboard()
        mime_data = cb.mimeData()

        # Check if clipboard has image
        if mime_data.hasImage():
            img: QImage = cb.image()
            if not img.isNull():
                temp_dir = tempfile.gettempdir()
                filename = f"screenshot_{int(time.time())}.png"
                temp_path = os.path.join(temp_dir, filename)
                img.save(temp_path, "PNG")
                self.sig_send_file.emit(self.current_peer_ip, temp_path)
                return

        # Check text
        text = cb.text().strip()
        if text:
            self.sig_send_text.emit(self.current_peer_ip, text)
        else:
            QMessageBox.information(
                self,
                "Clipboard Empty",
                "Clipboard is empty or does not contain text or images.",
            )

    # Drag and Drop Implementation
    def dragEnterEvent(self, event: QDragEnterEvent):
        if event.mimeData().hasUrls() and self.current_peer_ip:
            event.acceptProposedAction()
            self.drag_banner.setVisible(True)

    def dragLeaveEvent(self, event):
        self.drag_banner.setVisible(False)

    def dropEvent(self, event: QDropEvent):
        self.drag_banner.setVisible(False)
        if not self.current_peer_ip:
            return

        urls = event.mimeData().urls()
        for url in urls:
            filepath = url.toLocalFile()
            if filepath and os.path.isfile(filepath):
                self.sig_send_file.emit(self.current_peer_ip, filepath)
        event.acceptProposedAction()
