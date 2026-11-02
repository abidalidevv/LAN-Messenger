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
    """Modern WhatsApp-style chat bubble widget."""

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
        layout.setContentsMargins(12, 3, 12, 3)

        bubble_container = QFrame()
        bubble_container.setMaximumWidth(520)

        bg_color = "#005c4b" if is_outgoing else "#202c33"
        bubble_container.setStyleSheet(
            f"background-color: {bg_color}; border-radius: 10px; padding: 6px 12px;"
        )

        b_layout = QVBoxLayout(bubble_container)
        b_layout.setContentsMargins(4, 4, 4, 4)
        b_layout.setSpacing(4)

        if not is_outgoing and sender_name:
            lbl_sender = QLabel(sender_name)
            lbl_sender.setStyleSheet(
                "font-size: 11px; font-weight: bold; color: #00a884;"
            )
            b_layout.addWidget(lbl_sender)

        lbl_text = QLabel(text)
        lbl_text.setWordWrap(True)
        lbl_text.setTextInteractionFlags(Qt.TextInteractionFlag.TextSelectableByMouse)
        lbl_text.setStyleSheet("color: #e9edef; font-size: 14px;")
        b_layout.addWidget(lbl_text)

        # Timestamp
        time_str = time.strftime("%I:%M %p", time.localtime(timestamp))
        lbl_time = QLabel(time_str)
        lbl_time.setStyleSheet("font-size: 10px; color: #8696a0;")
        lbl_time.setAlignment(
            Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter
        )
        b_layout.addWidget(lbl_time)

        if is_outgoing:
            layout.addStretch()
            layout.addWidget(bubble_container)
        else:
            layout.addWidget(bubble_container)
            layout.addStretch()


class FileBubble(QWidget):
    """File transfer card with image preview thumbnail, progress bar, open and folder buttons."""

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
        layout.setContentsMargins(12, 4, 12, 4)

        card = QFrame()
        card.setMaximumWidth(460)
        bg_color = "#005c4b" if is_outgoing else "#202c33"
        card.setStyleSheet(
            f"background-color: {bg_color}; border-radius: 10px; padding: 8px 12px;"
        )

        c_layout = QVBoxLayout(card)
        c_layout.setContentsMargins(4, 4, 4, 4)
        c_layout.setSpacing(6)

        if not is_outgoing and sender_name:
            lbl_sender = QLabel(sender_name)
            lbl_sender.setStyleSheet(
                "font-size: 11px; font-weight: bold; color: #00a884;"
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
        cat = get_file_category(filename)
        icon = CATEGORY_ICONS.get(cat, "📎")
        lbl_icon = QLabel(icon)
        lbl_icon.setStyleSheet("font-size: 26px;")
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

        # Progress bar (if in progress)
        self.progress_bar = QProgressBar()
        self.progress_bar.setRange(0, 100)
        self.progress_bar.setValue(100 if is_completed else 0)
        self.progress_bar.setVisible(not is_completed)
        c_layout.addWidget(self.progress_bar)

        # Action buttons row
        self.btn_row = QHBoxLayout()
        self.btn_open = QPushButton("Open File")
        self.btn_open.clicked.connect(self._open_file)
        self.btn_folder = QPushButton("Show in Folder")
        self.btn_folder.clicked.connect(self._show_folder)

        self.btn_row.addWidget(self.btn_open)
        self.btn_row.addWidget(self.btn_folder)
        self.btn_row.addStretch()

        # Timestamp
        time_str = time.strftime("%I:%M %p", time.localtime(timestamp))
        lbl_time = QLabel(time_str)
        lbl_time.setStyleSheet("font-size: 10px; color: #8696a0;")
        self.btn_row.addWidget(lbl_time)

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
                        260,
                        180,
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
    """WhatsApp-style conversation panel with drag-and-drop, clipboard sync, and thumbnails."""

    sig_send_text = pyqtSignal(str, str)  # peer_ip, text
    sig_send_file = pyqtSignal(str, str)  # peer_ip, filepath
    sig_start_call = pyqtSignal(str)  # peer_ip
    sig_start_screenshare = pyqtSignal(str)  # peer_ip

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

        # Header
        self.header_frame = QFrame()
        self.header_frame.setObjectName("chatHeader")
        header_layout = QHBoxLayout(self.header_frame)
        header_layout.setContentsMargins(16, 10, 16, 10)

        self.lbl_peer_name = QLabel("Select a device to start sharing")
        self.lbl_peer_name.setStyleSheet(
            "font-size: 16px; font-weight: bold; color: #e9edef;"
        )
        self.lbl_peer_status = QLabel("")
        self.lbl_peer_status.setStyleSheet("font-size: 12px; color: #8696a0;")

        col = QVBoxLayout()
        col.setSpacing(2)
        col.addWidget(self.lbl_peer_name)
        col.addWidget(self.lbl_peer_status)
        header_layout.addLayout(col)
        header_layout.addStretch()

        self.btn_call = QPushButton("📞 Call")
        self.btn_call.setToolTip("Start Free LAN Voice Call")
        self.btn_call.clicked.connect(self._on_call_clicked)
        self.btn_call.setVisible(False)
        header_layout.addWidget(self.btn_call)

        self.btn_screen = QPushButton("🖥️ Screen")
        self.btn_screen.setToolTip("Start Free LAN Screen Sharing")
        self.btn_screen.clicked.connect(self._on_screen_clicked)
        self.btn_screen.setVisible(False)
        header_layout.addWidget(self.btn_screen)

        self.btn_quick_file = QPushButton("📎 Send File")
        self.btn_quick_file.clicked.connect(self._on_attach_clicked)
        self.btn_quick_file.setVisible(False)
        header_layout.addWidget(self.btn_quick_file)

        main_layout.addWidget(self.header_frame)

        # Message Scroll Area
        self.scroll_area = QScrollArea()
        self.scroll_area.setObjectName("chatScrollArea")
        self.scroll_area.setWidgetResizable(True)
        self.scroll_area.setHorizontalScrollBarPolicy(
            Qt.ScrollBarPolicy.ScrollBarAlwaysOff
        )

        self.content_widget = QWidget()
        self.content_widget.setObjectName("chatContent")
        self.content_layout = QVBoxLayout(self.content_widget)
        self.content_layout.setContentsMargins(16, 16, 16, 16)
        self.content_layout.setSpacing(4)
        self.content_layout.addStretch()

        self.scroll_area.setWidget(self.content_widget)
        main_layout.addWidget(self.scroll_area, 1)

        # Drag and Drop Banner
        self.drag_banner = QLabel("⬇️ Drop files here to send instantly!")
        self.drag_banner.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.drag_banner.setStyleSheet(
            "background-color: #00a884; color: #111b21; font-weight: bold; padding: 8px; font-size: 13px;"
        )
        self.drag_banner.setVisible(False)
        main_layout.addWidget(self.drag_banner)

        # Input Box Container
        self.input_container = QFrame()
        self.input_container.setObjectName("inputContainer")
        input_layout = QHBoxLayout(self.input_container)
        input_layout.setContentsMargins(12, 10, 12, 10)
        input_layout.setSpacing(8)

        self.btn_attach = QPushButton("📎")
        self.btn_attach.setObjectName("btnAttach")
        self.btn_attach.setToolTip("Attach File (Images, Videos, PDF, Any File)")
        self.btn_attach.clicked.connect(self._on_attach_clicked)
        input_layout.addWidget(self.btn_attach)

        # Instant Clipboard Sync Button
        self.btn_clipboard = QPushButton("📋")
        self.btn_clipboard.setObjectName("btnAttach")
        self.btn_clipboard.setToolTip(
            "Send Clipboard (Auto-paste copied text or screenshot image)"
        )
        self.btn_clipboard.clicked.connect(self._on_send_clipboard)
        input_layout.addWidget(self.btn_clipboard)

        self.msg_input = QLineEdit()
        self.msg_input.setObjectName("messageInput")
        self.msg_input.setPlaceholderText("Type a message... (Press Enter to send)")
        self.msg_input.returnPressed.connect(self._on_send_clicked)
        input_layout.addWidget(self.msg_input, 1)

        self.btn_send = QPushButton("➤")
        self.btn_send.setObjectName("btnSend")
        self.btn_send.setToolTip("Send Message")
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
            self.lbl_peer_status.setText(
                "📢 Broadcast Channel • Message will be sent to ALL connected PCs and phones"
            )
        else:
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

    def mark_file_completed(self, transfer_id: str, final_path: str):
        if transfer_id in self.file_bubbles:
            self.file_bubbles[transfer_id].mark_completed(final_path)

    def _scroll_to_bottom(self):
        self.scroll_area.verticalScrollBar().setValue(
            self.scroll_area.verticalScrollBar().maximum()
        )

    def _on_send_clicked(self):
        text = self.msg_input.text().strip()
        if not text or not self.current_peer_ip:
            return
        self.sig_send_text.emit(self.current_peer_ip, text)
        self.add_text_bubble(text, time.time(), is_outgoing=True)
        self.msg_input.clear()

    def _on_send_clipboard(self):
        """Instant Clipboard Sync: detects text or copied screenshot image and sends immediately."""
        if not self.current_peer_ip:
            return
        clipboard = QApplication.clipboard()
        mime = clipboard.mimeData()

        if mime.hasImage():
            # Copied screenshot or image in clipboard!
            image = clipboard.image()
            if not image.isNull():
                temp_dir = tempfile.gettempdir()
                filename = f"screenshot_{int(time.time())}.png"
                temp_path = os.path.join(temp_dir, filename)
                image.save(temp_path, "PNG")
                self.sig_send_file.emit(self.current_peer_ip, temp_path)
                return

        text = clipboard.text().strip()
        if text:
            self.sig_send_text.emit(self.current_peer_ip, text)
            self.add_text_bubble(text, time.time(), is_outgoing=True)
        else:
            QMessageBox.information(
                self,
                "Clipboard Empty",
                "Your clipboard is currently empty. Copy some text or a screenshot first!",
            )

    def _on_attach_clicked(self):
        if not self.current_peer_ip:
            return
        files, _ = QFileDialog.getOpenFileNames(
            self,
            "Select Files to Share",
            "",
            "All Files (*.*);;Images (*.png *.jpg *.jpeg *.gif *.webp);;Videos (*.mp4 *.mkv);;Documents (*.pdf *.docx *.zip)",
        )
        for filepath in files:
            self.sig_send_file.emit(self.current_peer_ip, filepath)

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
        for url in event.mimeData().urls():
            filepath = url.toLocalFile()
            if os.path.isfile(filepath):
                self.sig_send_file.emit(self.current_peer_ip, filepath)
        event.acceptProposedAction()
