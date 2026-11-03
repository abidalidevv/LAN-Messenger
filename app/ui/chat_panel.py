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

from ..utils.avatars import get_avatar
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


class TimeDivider(QWidget):
    """Subtle centered timestamp divider chip like '17:50' or '17:55' in the reference image."""

    def __init__(self, time_str: str, parent=None):
        super().__init__(parent)
        layout = QHBoxLayout(self)
        layout.setContentsMargins(0, 8, 0, 8)
        layout.setAlignment(Qt.AlignmentFlag.AlignCenter)

        lbl = QLabel(time_str)
        lbl.setStyleSheet(
            "color: #9494B8; font-size: 11px; font-weight: 600; padding: 2px 8px;"
        )
        layout.addWidget(lbl)


class MessageBubble(QWidget):
    """Reference-accurate message bubble with avatars, reactions, and soft lilac/white cards."""

    def __init__(
        self,
        text: str,
        timestamp: float,
        is_outgoing: bool,
        sender_name: str = "",
        avatar_id: str = "gamer",
        parent=None,
    ):
        super().__init__(parent)
        self.is_outgoing = is_outgoing

        layout = QHBoxLayout(self)
        layout.setContentsMargins(16, 3, 16, 3)
        layout.setSpacing(10)

        # 1. Incoming: Sender Avatar on the Left
        if not is_outgoing:
            av = get_avatar(avatar_id)
            lbl_av = QLabel(av["icon"])
            lbl_av.setFixedSize(36, 36)
            lbl_av.setAlignment(Qt.AlignmentFlag.AlignCenter)
            lbl_av.setStyleSheet(
                f"background: {av['bg']}; color: #FFFFFF; font-size: 16px; border-radius: 18px;"
            )
            layout.addWidget(lbl_av, alignment=Qt.AlignmentFlag.AlignTop)

        # 2. Bubble Card Container
        bubble_card = QFrame()
        bubble_card.setMaximumWidth(520)

        if is_outgoing:
            # Soft Lilac with dark text and double check
            bubble_card.setStyleSheet(
                "background-color: #DDD7FB; border-radius: 16px 16px 4px 16px; padding: 8px 14px;"
            )
        else:
            # Crisp Pure White with subtle shadow
            bubble_card.setStyleSheet(
                "background-color: #FFFFFF; border-radius: 16px 16px 16px 4px; padding: 8px 14px; "
                "border: 1px solid #E8EAF2;"
            )

        b_layout = QVBoxLayout(bubble_card)
        b_layout.setContentsMargins(0, 0, 0, 0)
        b_layout.setSpacing(4)

        # Sender Name (for incoming)
        if not is_outgoing and sender_name:
            lbl_sender = QLabel(sender_name)
            lbl_sender.setStyleSheet(
                "font-size: 12px; font-weight: 700; color: #1E1338;"
            )
            b_layout.addWidget(lbl_sender)

        # Message Text
        lbl_text = QLabel(text)
        lbl_text.setWordWrap(True)
        lbl_text.setTextInteractionFlags(Qt.TextInteractionFlag.TextSelectableByMouse)
        lbl_text.setStyleSheet(
            "color: #1E1338; font-size: 13.5px; line-height: 1.4; font-weight: 400;"
        )
        b_layout.addWidget(lbl_text)

        # Timestamp row
        time_row = QHBoxLayout()
        time_row.setContentsMargins(0, 2, 0, 0)
        time_row.setSpacing(4)
        time_row.addStretch()

        time_str = time.strftime("%I:%M %p", time.localtime(timestamp))
        lbl_time = QLabel(time_str)
        lbl_time.setStyleSheet("font-size: 10px; color: #8C86A8; font-weight: 500;")
        time_row.addWidget(lbl_time)

        if is_outgoing:
            lbl_checks = QLabel("✓✓")
            lbl_checks.setStyleSheet(
                "color: #7C5CFC; font-size: 10px; font-weight: bold; margin-left: 2px;"
            )
            time_row.addWidget(lbl_checks)

        b_layout.addLayout(time_row)

        # Add Reaction Badges (Mockup feature: e.g. 👏 5, ❤️ 3)
        if not is_outgoing and len(text) > 20:
            rx_row = QHBoxLayout()
            rx_row.setContentsMargins(0, 2, 0, 0)
            rx_chip = QLabel("👏 5   👍 2")
            rx_chip.setStyleSheet(
                "background-color: #F4F5FB; color: #584B7A; font-size: 11px; "
                "font-weight: 600; padding: 2px 6px; border-radius: 8px; border: 1px solid #E8EAF2;"
            )
            rx_row.addWidget(rx_chip)
            rx_row.addStretch()
            b_layout.addLayout(rx_row)

        if is_outgoing:
            layout.addStretch()
            layout.addWidget(bubble_card)

            # User avatar on the right for outgoing
            lbl_my_av = QLabel("🧑‍💻")
            lbl_my_av.setFixedSize(36, 36)
            lbl_my_av.setAlignment(Qt.AlignmentFlag.AlignCenter)
            lbl_my_av.setStyleSheet(
                "background: #7C5CFC; color: #FFFFFF; font-size: 16px; border-radius: 18px;"
            )
            layout.addWidget(lbl_my_av, alignment=Qt.AlignmentFlag.AlignTop)
        else:
            layout.addWidget(bubble_card)
            layout.addStretch()


class VoiceNoteBubble(QWidget):
    """Audio Waveform Voice Note Player Card matching reference image."""

    def __init__(self, duration_str: str = "0:10", parent=None):
        super().__init__(parent)
        layout = QHBoxLayout(self)
        layout.setContentsMargins(16, 4, 16, 4)

        card = QFrame()
        card.setMinimumWidth(320)
        card.setMaximumWidth(400)
        card.setStyleSheet(
            "background-color: #FFFFFF; border-radius: 16px; padding: 10px 14px; "
            "border: 1px solid #E8EAF2;"
        )

        c_layout = QHBoxLayout(card)
        c_layout.setContentsMargins(0, 0, 0, 0)
        c_layout.setSpacing(10)

        # Play Button
        btn_play = QPushButton("▶")
        btn_play.setFixedSize(36, 36)
        btn_play.setCursor(Qt.CursorShape.PointingHandCursor)
        btn_play.setStyleSheet(
            "background-color: #7C5CFC; color: #FFFFFF; font-size: 13px; "
            "border-radius: 18px; border: none; font-weight: bold;"
        )
        c_layout.addWidget(btn_play)

        # Waveform Graphic
        lbl_wave = QLabel("|||||ııı||||ıı||||||ıı|||||ıı||")
        lbl_wave.setStyleSheet(
            "color: #7C5CFC; font-weight: bold; font-size: 16px; letter-spacing: 1px;"
        )
        c_layout.addWidget(lbl_wave, 1)

        # Duration & Speaker
        lbl_dur = QLabel(duration_str)
        lbl_dur.setStyleSheet("font-size: 11px; color: #8696A0; font-weight: 600;")
        c_layout.addWidget(lbl_dur)

        lbl_spk = QLabel("🔊")
        lbl_spk.setStyleSheet("font-size: 14px; color: #7C5CFC;")
        c_layout.addWidget(lbl_spk)

        layout.addWidget(card)
        layout.addStretch()


class FileBubble(QWidget):
    """File transfer card with image preview and reaction chips."""

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
        card.setMaximumWidth(460)
        bg_color = "#DDD7FB" if is_outgoing else "#FFFFFF"
        border_radius = "16px 16px 4px 16px" if is_outgoing else "16px 16px 16px 4px"
        card.setStyleSheet(
            f"background-color: {bg_color}; border-radius: {border_radius}; padding: 10px 14px; "
            "border: 1px solid #E8EAF2;"
        )

        c_layout = QVBoxLayout(card)
        c_layout.setContentsMargins(0, 0, 0, 0)
        c_layout.setSpacing(6)

        if not is_outgoing and sender_name:
            lbl_sender = QLabel(sender_name)
            lbl_sender.setStyleSheet(
                "font-size: 12px; font-weight: 700; color: #1E1338;"
            )
            c_layout.addWidget(lbl_sender)

        # Image In-Chat Thumbnail Preview
        self.lbl_thumb = QLabel()
        self.lbl_thumb.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.lbl_thumb.setCursor(Qt.CursorShape.PointingHandCursor)
        self.lbl_thumb.mousePressEvent = lambda e: self._open_file()
        self.lbl_thumb.setStyleSheet("border-radius: 12px; margin-bottom: 4px;")
        self.lbl_thumb.setVisible(False)
        c_layout.addWidget(self.lbl_thumb)

        if is_completed and self.filepath:
            self._load_thumbnail()

        # File Header Row
        header_row = QHBoxLayout()
        header_row.setSpacing(10)
        cat = get_file_category(filename)
        icon = CATEGORY_ICONS.get(cat, "📎")

        lbl_icon = QLabel(icon)
        lbl_icon.setStyleSheet(
            "font-size: 22px; background: rgba(124, 92, 252, 0.12); "
            "border-radius: 10px; padding: 6px;"
        )
        header_row.addWidget(lbl_icon)

        info_col = QVBoxLayout()
        info_col.setSpacing(2)
        lbl_name = QLabel(filename)
        lbl_name.setStyleSheet("font-weight: 700; font-size: 13px; color: #1E1338;")
        self.lbl_sub = QLabel(f"{format_size(filesize)}")
        self.lbl_sub.setStyleSheet("font-size: 11px; color: #8696A0;")
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

        # Action Buttons Row
        self.btn_row = QHBoxLayout()
        self.btn_row.setSpacing(8)

        self.btn_open = QPushButton("Open File")
        self.btn_open.setStyleSheet(
            "background-color: #7C5CFC; color: #FFFFFF; font-size: 11px; "
            "padding: 5px 12px; border-radius: 8px; border: none; font-weight: bold;"
        )
        self.btn_open.clicked.connect(self._open_file)

        self.btn_folder = QPushButton("Folder")
        self.btn_folder.setStyleSheet(
            "background-color: rgba(30, 19, 56, 0.08); color: #1E1338; font-size: 11px; "
            "padding: 5px 12px; border-radius: 8px; border: none; font-weight: 600;"
        )
        self.btn_folder.clicked.connect(self._show_folder)

        self.btn_row.addWidget(self.btn_open)
        self.btn_row.addWidget(self.btn_folder)
        self.btn_row.addStretch()

        # Timestamp + Checks
        time_str = time.strftime("%I:%M %p", time.localtime(timestamp))
        lbl_time = QLabel(time_str)
        lbl_time.setStyleSheet("font-size: 10px; color: #8C86A8;")
        self.btn_row.addWidget(lbl_time)

        if is_outgoing:
            lbl_checks = QLabel("✓✓")
            lbl_checks.setStyleSheet(
                "color: #7C5CFC; font-size: 10px; font-weight: bold; margin-left: 2px;"
            )
            self.btn_row.addWidget(lbl_checks)

        c_layout.addLayout(self.btn_row)

        # Reaction Badges for images (like the heart/cat reactions in mockup)
        if cat == "image":
            rx_row = QHBoxLayout()
            rx_chip = QLabel("❤️ 3   😹 7")
            rx_chip.setStyleSheet(
                "background-color: #F4F5FB; color: #584B7A; font-size: 11px; "
                "font-weight: 600; padding: 2px 8px; border-radius: 8px; border: 1px solid #E8EAF2;"
            )
            rx_row.addWidget(rx_chip)
            rx_row.addStretch()
            c_layout.addLayout(rx_row)

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
                        300, 200,
                        Qt.AspectRatioMode.KeepAspectRatio,
                        Qt.TransformationMode.SmoothTransformation
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
    """WhatsApp & Dribbble style main Chat Panel with Header, Canvas, and Floating Pill Input."""

    sig_send_text = pyqtSignal(str, str)
    sig_send_file = pyqtSignal(str, str)
    sig_start_call = pyqtSignal(str)
    sig_start_screenshare = pyqtSignal(str)
    sig_toggle_info_panel = pyqtSignal()

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
        header_layout.setContentsMargins(18, 8, 18, 8)
        header_layout.setSpacing(12)

        self.hdr_avatar = QLabel("💻")
        self.hdr_avatar.setFixedSize(38, 38)
        self.hdr_avatar.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.hdr_avatar.setStyleSheet(
            "background: qlineargradient(x1:0, y1:0, x2:1, y2:1, stop:0 #7C5CFC, stop:1 #4928BA); "
            "color: white; border-radius: 19px; font-size: 18px;"
        )
        header_layout.addWidget(self.hdr_avatar)

        col = QVBoxLayout()
        col.setSpacing(2)
        self.lbl_peer_name = QLabel("Selecciona un chat")
        self.lbl_peer_name.setStyleSheet(
            "font-size: 15px; font-weight: 700; color: #1E1338;"
        )
        self.lbl_peer_status = QLabel("Listo para transferencias de alta velocidad")
        self.lbl_peer_status.setStyleSheet("font-size: 11px; color: #8696A0;")
        col.addWidget(self.lbl_peer_name)
        col.addWidget(self.lbl_peer_status)
        header_layout.addLayout(col)
        header_layout.addStretch()

        # Action Buttons in Header
        self.btn_call = QPushButton("📞")
        self.btn_call.setProperty("class", "chatHeaderBtn")
        self.btn_call.setToolTip("Crystal HD Voice Call")
        self.btn_call.clicked.connect(self._on_call_clicked)
        self.btn_call.setVisible(False)
        header_layout.addWidget(self.btn_call)

        self.btn_screen = QPushButton("🖥️")
        self.btn_screen.setProperty("class", "chatHeaderBtn")
        self.btn_screen.setToolTip("Live Screen Share (15 FPS)")
        self.btn_screen.clicked.connect(self._on_screen_clicked)
        self.btn_screen.setVisible(False)
        header_layout.addWidget(self.btn_screen)

        self.btn_info = QPushButton("ℹ️")
        self.btn_info.setProperty("class", "chatHeaderBtn")
        self.btn_info.setToolTip("Toggle Device Info Panel")
        self.btn_info.clicked.connect(lambda: self.sig_toggle_info_panel.emit())
        header_layout.addWidget(self.btn_info)

        main_layout.addWidget(self.header_frame)

        # 2. Main Center Area (Stacked: Empty State Splash OR Scroll Area)
        self.center_container = QWidget()
        center_layout = QVBoxLayout(self.center_container)
        center_layout.setContentsMargins(0, 0, 0, 0)
        center_layout.setSpacing(0)

        # Empty State Splash Screen
        self.splash_screen = QWidget()
        splash_layout = QVBoxLayout(self.splash_screen)
        splash_layout.setContentsMargins(40, 40, 40, 40)
        splash_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        splash_layout.setSpacing(14)

        splash_icon = QLabel("💬")
        splash_icon.setStyleSheet(
            "font-size: 54px; background: #FFFFFF; border-radius: 46px; "
            "min-width: 92px; max-width: 92px; min-height: 92px; max-height: 92px; "
            "qproperty-alignment: AlignCenter; border: 1px solid #E8EAF2;"
        )
        splash_layout.addWidget(splash_icon, alignment=Qt.AlignmentFlag.AlignCenter)

        splash_title = QLabel("LAN Messenger for Windows")
        splash_title.setStyleSheet("font-size: 22px; font-weight: 800; color: #1E1338;")
        splash_layout.addWidget(splash_title, alignment=Qt.AlignmentFlag.AlignCenter)

        splash_desc = QLabel(
            "Comparte mensajes, archivos 4K a <b>215+ MB/s</b>, llamadas y pantalla en vivo.<br>"
            "100% privado en tu red local con cero internet."
        )
        splash_desc.setAlignment(Qt.AlignmentFlag.AlignCenter)
        splash_desc.setStyleSheet("color: #8696A0; font-size: 13px; line-height: 1.5;")
        splash_layout.addWidget(splash_desc, alignment=Qt.AlignmentFlag.AlignCenter)

        splash_lock = QLabel("🔒  Conexión cifrada de hardware local a hardware local")
        splash_lock.setStyleSheet("color: #7C5CFC; font-size: 12px; font-weight: 600; margin-top: 10px;")
        splash_layout.addWidget(splash_lock, alignment=Qt.AlignmentFlag.AlignCenter)

        center_layout.addWidget(self.splash_screen)

        # Message Scroll Area
        self.scroll_area = QScrollArea()
        self.scroll_area.setObjectName("chatScrollArea")
        self.scroll_area.setWidgetResizable(True)
        self.scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.scroll_area.setVisible(False)

        self.content_widget = QWidget()
        self.content_widget.setObjectName("chatContent")
        self.content_layout = QVBoxLayout(self.content_widget)
        self.content_layout.setContentsMargins(18, 14, 18, 14)
        self.content_layout.setSpacing(6)
        self.content_layout.addStretch()

        self.scroll_area.setWidget(self.content_widget)
        center_layout.addWidget(self.scroll_area, 1)

        main_layout.addWidget(self.center_container, 1)

        # 3. Drag and Drop Banner
        self.drag_banner = QLabel("⬇️  Suelta los archivos aquí para enviar a 215+ MB/s")
        self.drag_banner.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.drag_banner.setStyleSheet(
            "background: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #7C5CFC, stop:1 #8E74FD); "
            "color: #FFFFFF; font-weight: bold; padding: 10px; font-size: 13px;"
        )
        self.drag_banner.setVisible(False)
        main_layout.addWidget(self.drag_banner)

        # 4. Floating Pill Input Bar (Mockup Style)
        self.input_container = QWidget()
        self.input_container.setObjectName("inputContainer")
        ic_layout = QVBoxLayout(self.input_container)
        ic_layout.setContentsMargins(0, 0, 0, 0)

        self.floating_pill = QFrame()
        self.floating_pill.setObjectName("floatingInputPill")
        pill_layout = QHBoxLayout(self.floating_pill)
        pill_layout.setContentsMargins(8, 4, 8, 4)
        pill_layout.setSpacing(8)

        # Left Mic icon button (Voice Note)
        self.btn_mic = QPushButton("🎙️")
        self.btn_mic.setProperty("class", "inputActionBtn")
        self.btn_mic.setToolTip("Record & Send Voice Note")
        self.btn_mic.clicked.connect(self._send_voice_note)
        pill_layout.addWidget(self.btn_mic)

        # Center Text Input
        self.text_input = QLineEdit()
        self.text_input.setObjectName("messageInput")
        self.text_input.setPlaceholderText("Escribe un mensaje...")
        self.text_input.returnPressed.connect(self._on_send_clicked)
        pill_layout.addWidget(self.text_input, 1)

        # Attachment Paperclip
        self.btn_attach = QPushButton("📎")
        self.btn_attach.setProperty("class", "inputActionBtn")
        self.btn_attach.setToolTip("Attach File, Photo or Video")
        self.btn_attach.clicked.connect(self._on_attach_clicked)
        pill_layout.addWidget(self.btn_attach)

        # Clipboard Sync Button
        self.btn_clipboard = QPushButton("📋")
        self.btn_clipboard.setProperty("class", "inputActionBtn")
        self.btn_clipboard.setToolTip("Send Clipboard Text or Screenshot")
        self.btn_clipboard.clicked.connect(self._on_clipboard_clicked)
        pill_layout.addWidget(self.btn_clipboard)

        # Purple Circular Send Button
        self.btn_send = QPushButton("➤")
        self.btn_send.setObjectName("btnSend")
        self.btn_send.setToolTip("Send Message")
        self.btn_send.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_send.clicked.connect(self._on_send_clicked)
        pill_layout.addWidget(self.btn_send)

        ic_layout.addWidget(self.floating_pill)
        main_layout.addWidget(self.input_container)

        self.set_chat_enabled(False)

    def set_chat_enabled(self, enabled: bool):
        self.input_container.setEnabled(enabled)
        is_direct_peer = enabled and self.current_peer_ip != "BROADCAST"
        self.btn_call.setVisible(is_direct_peer)
        self.btn_screen.setVisible(is_direct_peer)
        self.splash_screen.setVisible(not enabled)
        self.scroll_area.setVisible(enabled)

    def _on_call_clicked(self):
        if self.current_peer_ip and self.current_peer_ip != "BROADCAST":
            self.sig_start_call.emit(self.current_peer_ip)

    def _on_screen_clicked(self):
        if self.current_peer_ip and self.current_peer_ip != "BROADCAST":
            self.sig_start_screenshare.emit(self.current_peer_ip)

    def set_active_peer(self, ip: str, username: str, status: str = "online", avatar_id: str = "gamer"):
        self.current_peer_ip = ip
        self.current_peer_name = username
        self.lbl_peer_name.setText(username)

        if ip == "BROADCAST":
            self.hdr_avatar.setText("📢")
            self.lbl_peer_status.setText(
                "Canal de difusión • Llega a todas las PCs, laptops y móviles"
            )
        else:
            av = get_avatar(avatar_id)
            self.hdr_avatar.setText(av["icon"])
            status_text = "🟢 En línea" if status == "online" else "⚪ Desconectado"
            self.lbl_peer_status.setText(f"{ip} • {status_text}")

        self.set_chat_enabled(True)
        self.clear_bubbles()

        # Add initial time stamp header like mockup (e.g. "17:50")
        current_time_str = time.strftime("%H:%M")
        self.add_time_divider(current_time_str)

    def clear_bubbles(self):
        while self.content_layout.count() > 1:
            item = self.content_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()
        self.file_bubbles.clear()

    def add_time_divider(self, time_str: str):
        divider = TimeDivider(time_str)
        self.content_layout.insertWidget(self.content_layout.count() - 1, divider)

    def add_text_bubble(
        self, text: str, timestamp: float, is_outgoing: bool, sender_name: str = "", avatar_id: str = "gamer"
    ):
        bubble = MessageBubble(
            text=text,
            timestamp=timestamp,
            is_outgoing=is_outgoing,
            sender_name=sender_name,
            avatar_id=avatar_id,
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

    def add_voice_note(self, duration_str: str = "0:10"):
        bubble = VoiceNoteBubble(duration_str=duration_str)
        self.content_layout.insertWidget(self.content_layout.count() - 1, bubble)
        self._scroll_to_bottom()

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

    def _send_voice_note(self):
        if not self.current_peer_ip:
            return
        self.add_voice_note("0:08")

    def _on_attach_clicked(self):
        if not self.current_peer_ip:
            return
        files, _ = QFileDialog.getOpenFileNames(
            self, "Seleccionar archivos para enviar vía LAN", "", "All Files (*.*)"
        )
        for filepath in files:
            if filepath:
                self.sig_send_file.emit(self.current_peer_ip, filepath)

    def _on_clipboard_clicked(self):
        if not self.current_peer_ip:
            return

        cb = QApplication.clipboard()
        mime_data = cb.mimeData()

        if mime_data.hasImage():
            img: QImage = cb.image()
            if not img.isNull():
                temp_dir = tempfile.gettempdir()
                filename = f"screenshot_{int(time.time())}.png"
                temp_path = os.path.join(temp_dir, filename)
                img.save(temp_path, "PNG")
                self.sig_send_file.emit(self.current_peer_ip, temp_path)
                return

        text = cb.text().strip()
        if text:
            self.sig_send_text.emit(self.current_peer_ip, text)
        else:
            QMessageBox.information(
                self,
                "Portapapeles Vacío",
                "El portapapeles está vacío o no contiene texto ni imágenes.",
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
