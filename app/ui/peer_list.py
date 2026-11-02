from typing import Dict, Any, Optional
from PyQt6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QListWidget,
    QListWidgetItem,
    QFrame,
)
from PyQt6.QtCore import Qt, pyqtSignal
from ..utils.avatars import get_avatar

BROADCAST_ID = "BROADCAST"


class PeerItemWidget(QWidget):
    """Custom rendering for a peer entry with avatar, status, and unread badge."""

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
        self.init_ui()

    def init_ui(self):
        layout = QHBoxLayout(self)
        layout.setContentsMargins(4, 4, 4, 4)
        layout.setSpacing(12)

        # Avatar
        self.avatar = QLabel()
        self.avatar.setFixedSize(44, 44)
        self._render_avatar()
        layout.addWidget(self.avatar)

        # Info layout
        info_layout = QVBoxLayout()
        info_layout.setSpacing(2)
        info_layout.setContentsMargins(0, 0, 0, 0)

        name_row = QHBoxLayout()
        self.lbl_name = QLabel(self.username)
        self.lbl_name.setStyleSheet(
            "font-weight: 600; font-size: 14px; color: #e9edef;"
        )
        self.lbl_status_dot = QLabel(
            "📢"
            if self.is_broadcast
            else ("🟢" if self.status == "online" else "⚪")
        )
        self.lbl_status_dot.setStyleSheet("font-size: 10px;")
        name_row.addWidget(self.lbl_name)
        name_row.addWidget(self.lbl_status_dot)
        name_row.addStretch()

        self.lbl_sub = QLabel(
            "Broadcast to all connected devices" if self.is_broadcast else self.ip
        )
        self.lbl_sub.setStyleSheet("font-size: 12px; color: #8696a0;")

        info_layout.addLayout(name_row)
        info_layout.addWidget(self.lbl_sub)
        layout.addLayout(info_layout, 1)

        # Unread badge
        self.lbl_badge = QLabel("")
        self.lbl_badge.setStyleSheet(
            "background-color: #00a884; color: #111b21; font-weight: bold; font-size: 11px; border-radius: 9px; padding: 2px 6px;"
        )
        self.lbl_badge.setVisible(False)
        layout.addWidget(self.lbl_badge)

    def _render_avatar(self):
        if self.is_broadcast:
            self.avatar.setStyleSheet(
                "background-color: #00a884; color: #ffffff; border-radius: 22px; font-size: 20px; qproperty-alignment: AlignCenter;"
            )
            self.avatar.setText("📢")
            return

        av = get_avatar(self.avatar_id)
        self.avatar.setStyleSheet(
            f"background-color: {av['bg']}; color: #ffffff; border-radius: 22px; font-size: 20px; qproperty-alignment: AlignCenter;"
        )
        self.avatar.setText(av["icon"])

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
            self.lbl_status_dot.setText("🟢" if status == "online" else "⚪")

    def set_last_message(self, text: str):
        self.last_msg = text
        display_text = (text[:24] + "...") if len(text) > 24 else text
        self.lbl_sub.setText(f"{display_text}")

    def increment_unread(self):
        self.unread_count += 1
        self.lbl_badge.setText(str(self.unread_count))
        self.lbl_badge.setVisible(True)

    def clear_unread(self):
        self.unread_count = 0
        self.lbl_badge.setVisible(False)


class PeerListSidebar(QWidget):
    """Sidebar widget with search, pinned broadcast channel, and live peers list."""

    sig_peer_selected = pyqtSignal(str)  # emitted with peer_ip or BROADCAST_ID

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("sidebar")
        self.peer_widgets: Dict[str, PeerItemWidget] = {}
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        # Header Search Area
        header_widget = QWidget()
        header_widget.setObjectName("sidebarHeader")
        header_layout = QVBoxLayout(header_widget)
        header_layout.setContentsMargins(12, 12, 12, 12)

        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("🔍 Search or filter devices...")
        self.search_input.textChanged.connect(self._filter_peers)
        header_layout.addWidget(self.search_input)

        layout.addWidget(header_widget)

        # List Widget
        self.list_widget = QListWidget()
        self.list_widget.itemClicked.connect(self._on_item_clicked)
        layout.addWidget(self.list_widget)

        # Add Permanent Pinned Broadcast Channel at top
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
