import time
from typing import Dict, Any, Optional
from PyQt6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QListWidget,
    QListWidgetItem,
    QPushButton,
    QFrame,
)
from PyQt6.QtCore import Qt, pyqtSignal
from ..utils.avatars import get_avatar

BROADCAST_ID = "BROADCAST"


class PeerItemWidget(QWidget):
    """Modern WhatsApp Desktop / Telegram styled peer list item."""

    def __init__(
        self,
        ip: str,
        username: str,
        status: str = "online",
        avatar_id: str = "gamer",
        is_broadcast: bool = False,
        parent=None,
    ):
        super().__init__(parent)
        self.ip = ip
        self.username = username
        self.status = status
        self.avatar_id = avatar_id
        self.is_broadcast = is_broadcast
        self.unread_count = 0
        self.last_msg = ""
        self.last_time = time.time()
        self.init_ui()

    def init_ui(self):
        layout = QHBoxLayout(self)
        layout.setContentsMargins(10, 8, 10, 8)
        layout.setSpacing(12)

        # Avatar Container with Online Indicator Ring
        avatar_container = QWidget()
        avatar_container.setFixedSize(50, 50)
        ac_layout = QVBoxLayout(avatar_container)
        ac_layout.setContentsMargins(0, 0, 0, 0)

        self.avatar = QLabel(avatar_container)
        self.avatar.setFixedSize(48, 48)
        self.avatar.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self._render_avatar()

        # Online Status Ring Badge (Bottom Right of Avatar)
        self.status_badge = QLabel(avatar_container)
        self.status_badge.setFixedSize(14, 14)
        self.status_badge.move(34, 34)
        self._update_status_badge()

        layout.addWidget(avatar_container)

        # Info column (Name, Last Message, Timestamp)
        info_col = QVBoxLayout()
        info_col.setContentsMargins(0, 2, 0, 2)
        info_col.setSpacing(4)

        # Top Row: Name + Time
        top_row = QHBoxLayout()
        top_row.setContentsMargins(0, 0, 0, 0)
        self.lbl_name = QLabel(self.username)
        self.lbl_name.setStyleSheet(
            "font-weight: 600; font-size: 14px; color: #e9edef;"
        )
        top_row.addWidget(self.lbl_name)
        top_row.addStretch()

        self.lbl_time = QLabel("")
        self.lbl_time.setStyleSheet("font-size: 11px; color: #8696a0;")
        top_row.addWidget(self.lbl_time)
        info_col.addLayout(top_row)

        # Bottom Row: Last Message Snippet + Unread Badge
        bot_row = QHBoxLayout()
        bot_row.setContentsMargins(0, 0, 0, 0)
        self.lbl_sub = QLabel(
            "Tap to broadcast to all devices" if self.is_broadcast else self.ip
        )
        self.lbl_sub.setStyleSheet("font-size: 12px; color: #8696a0;")
        bot_row.addWidget(self.lbl_sub, 1)

        self.lbl_badge = QLabel("")
        self.lbl_badge.setStyleSheet(
            "background-color: #00a884; color: #111b21; font-weight: bold; "
            "font-size: 11px; border-radius: 9px; min-width: 18px; max-height: 18px; "
            "qproperty-alignment: AlignCenter; padding: 1px 5px;"
        )
        self.lbl_badge.setVisible(False)
        bot_row.addWidget(self.lbl_badge)
        info_col.addLayout(bot_row)

        layout.addLayout(info_col, 1)

    def _render_avatar(self):
        if self.is_broadcast:
            self.avatar.setStyleSheet(
                "background: qlineargradient(x1:0, y1:0, x2:1, y2:1, stop:0 #00a884, stop:1 #005c4b); "
                "color: #ffffff; border-radius: 24px; font-size: 22px;"
            )
            self.avatar.setText("📢")
            return

        av = get_avatar(self.avatar_id)
        self.avatar.setStyleSheet(
            f"background: qlineargradient(x1:0, y1:0, x2:1, y2:1, stop:0 {av['bg']}, stop:1 #111b21); "
            f"color: #ffffff; border-radius: 24px; font-size: 22px; border: 1px solid rgba(255, 255, 255, 0.08);"
        )
        self.avatar.setText(av["icon"])

    def _update_status_badge(self):
        if self.is_broadcast:
            self.status_badge.setVisible(False)
            return

        is_online = (self.status == "online")
        dot_color = "#00a884" if is_online else "#8696a0"
        self.status_badge.setStyleSheet(
            f"background-color: {dot_color}; border: 2px solid #111b21; border-radius: 7px;"
        )
        self.status_badge.setVisible(True)

    def update_info(
        self,
        username: Optional[str] = None,
        status: Optional[str] = None,
        avatar_id: Optional[str] = None,
    ):
        if username and username != self.username:
            self.username = username
            self.lbl_name.setText(username)
        if avatar_id and avatar_id != self.avatar_id:
            self.avatar_id = avatar_id
            self._render_avatar()
        if status and not self.is_broadcast:
            self.status = status
            self._update_status_badge()

    def set_last_message(self, text: str):
        self.last_msg = text
        display_text = (text[:28] + "...") if len(text) > 28 else text
        self.lbl_sub.setText(display_text)
        self.lbl_time.setText(time.strftime("%I:%M %p"))

    def increment_unread(self):
        self.unread_count += 1
        self.lbl_badge.setText(str(self.unread_count))
        self.lbl_badge.setVisible(True)

    def clear_unread(self):
        self.unread_count = 0
        self.lbl_badge.setVisible(False)


class PeerListSidebar(QWidget):
    """WhatsApp Desktop style Sidebar with Header, Search bar, and Peer List."""

    sig_peer_selected = pyqtSignal(str)  # emitted with peer_ip or BROADCAST_ID
    sig_quick_scan = pyqtSignal()
    sig_quick_add = pyqtSignal()

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("sidebar")
        self.peer_widgets: Dict[str, PeerItemWidget] = {}
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        # Header: "Chats" Title + Quick Action Icons
        header_widget = QWidget()
        header_widget.setObjectName("sidebarHeader")
        h_layout = QHBoxLayout(header_widget)
        h_layout.setContentsMargins(16, 12, 12, 12)

        lbl_title = QLabel("Chats")
        lbl_title.setObjectName("sidebarTitle")
        h_layout.addWidget(lbl_title)
        h_layout.addStretch()

        btn_scan = QPushButton("⚡")
        btn_scan.setToolTip("Scan local subnets for active devices")
        btn_scan.setStyleSheet(
            "background: transparent; color: #aebac1; font-size: 16px; border: none; "
            "border-radius: 16px; min-width: 32px; min-height: 32px; max-width: 32px; max-height: 32px;"
        )
        btn_scan.setCursor(Qt.CursorShape.PointingHandCursor)
        btn_scan.clicked.connect(lambda: self.sig_quick_scan.emit())
        h_layout.addWidget(btn_scan)

        btn_add = QPushButton("➕")
        btn_add.setToolTip("Connect new device by IP or Domain")
        btn_add.setStyleSheet(
            "background: transparent; color: #aebac1; font-size: 16px; border: none; "
            "border-radius: 16px; min-width: 32px; min-height: 32px; max-width: 32px; max-height: 32px;"
        )
        btn_add.setCursor(Qt.CursorShape.PointingHandCursor)
        btn_add.clicked.connect(lambda: self.sig_quick_add.emit())
        h_layout.addWidget(btn_add)

        layout.addWidget(header_widget)

        # Search Bar Container
        search_box_container = QWidget()
        search_box_container.setObjectName("searchContainer")
        sb_layout = QHBoxLayout(search_box_container)
        sb_layout.setContentsMargins(12, 6, 12, 8)

        self.search_input = QLineEdit()
        self.search_input.setObjectName("searchBox")
        self.search_input.setPlaceholderText("🔍  Search or start new chat")
        self.search_input.textChanged.connect(self._filter_peers)
        sb_layout.addWidget(self.search_input)

        layout.addWidget(search_box_container)

        # Peer List View
        self.list_widget = QListWidget()
        self.list_widget.setObjectName("peerList")
        self.list_widget.itemClicked.connect(self._on_item_clicked)
        layout.addWidget(self.list_widget, 1)

        # Pinned Broadcast Channel
        self._add_broadcast_channel()

    def _add_broadcast_channel(self):
        item = QListWidgetItem()
        widget = PeerItemWidget(
            ip=BROADCAST_ID,
            username="📢 All Devices (Broadcast)",
            status="online",
            is_broadcast=True,
        )
        item.setSizeHint(widget.sizeHint())
        item.setData(Qt.ItemDataRole.UserRole, BROADCAST_ID)
        self.list_widget.addItem(item)
        self.list_widget.setItemWidget(item, widget)
        self.peer_widgets[BROADCAST_ID] = widget

    def add_or_update_peer(self, peer_info: Dict[str, Any]):
        ip = peer_info["ip"]
        if ip == BROADCAST_ID:
            return

        username = peer_info.get("username", f"Peer @ {ip}")
        status = peer_info.get("status", "online")
        avatar_id = peer_info.get("avatar_id", "gamer")

        if ip in self.peer_widgets:
            widget = self.peer_widgets[ip]
            widget.update_info(
                username=username, status=status, avatar_id=avatar_id
            )
        else:
            item = QListWidgetItem()
            widget = PeerItemWidget(
                ip=ip, username=username, status=status, avatar_id=avatar_id
            )
            item.setSizeHint(widget.sizeHint())
            item.setData(Qt.ItemDataRole.UserRole, ip)

            self.list_widget.addItem(item)
            self.list_widget.setItemWidget(item, widget)
            self.peer_widgets[ip] = widget

    def update_peer_status(self, ip: str, status: str):
        if ip in self.peer_widgets:
            self.peer_widgets[ip].update_info(status=status)

    def update_last_message(self, ip: str, text: str, is_active_chat: bool = False):
        if ip in self.peer_widgets:
            widget = self.peer_widgets[ip]
            widget.set_last_message(text)
            if not is_active_chat:
                widget.increment_unread()

    def select_peer(self, ip: str):
        for i in range(self.list_widget.count()):
            item = self.list_widget.item(i)
            if item.data(Qt.ItemDataRole.UserRole) == ip:
                self.list_widget.setCurrentItem(item)
                if ip in self.peer_widgets:
                    self.peer_widgets[ip].clear_unread()
                break

    def _on_item_clicked(self, item: QListWidgetItem):
        ip = item.data(Qt.ItemDataRole.UserRole)
        if ip:
            if ip in self.peer_widgets:
                self.peer_widgets[ip].clear_unread()
            self.sig_peer_selected.emit(ip)

    def _filter_peers(self, query: str):
        query = query.lower().strip()
        for i in range(self.list_widget.count()):
            item = self.list_widget.item(i)
            ip = item.data(Qt.ItemDataRole.UserRole)
            if ip == BROADCAST_ID:
                continue
            widget = self.peer_widgets.get(ip)
            if widget:
                match = (query in ip.lower()) or (query in widget.username.lower())
                item.setHidden(not match)
