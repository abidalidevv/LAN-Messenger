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
    """WhatsApp & Dribbble styled clean white peer list item."""

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
        self.time_label_text = "1m"
        self.init_ui()

    def init_ui(self):
        layout = QHBoxLayout(self)
        layout.setContentsMargins(8, 8, 8, 8)
        layout.setSpacing(12)

        # Avatar Container with Online Indicator Ring
        avatar_container = QWidget()
        avatar_container.setFixedSize(48, 48)
        ac_layout = QVBoxLayout(avatar_container)
        ac_layout.setContentsMargins(0, 0, 0, 0)

        self.avatar = QLabel(avatar_container)
        self.avatar.setFixedSize(46, 46)
        self.avatar.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self._render_avatar()

        # Online Status Ring Badge (Bottom Right of Avatar)
        self.status_badge = QLabel(avatar_container)
        self.status_badge.setFixedSize(12, 12)
        self.status_badge.move(32, 32)
        self._update_status_badge()

        layout.addWidget(avatar_container)

        # Info column (Name, Last Message, Timestamp)
        info_col = QVBoxLayout()
        info_col.setContentsMargins(0, 1, 0, 1)
        info_col.setSpacing(3)

        # Top Row: Name + Time
        top_row = QHBoxLayout()
        top_row.setContentsMargins(0, 0, 0, 0)
        self.lbl_name = QLabel(self.username)
        self.lbl_name.setStyleSheet(
            "font-weight: 700; font-size: 14px; color: #1E1338;"
        )
        top_row.addWidget(self.lbl_name)
        top_row.addStretch()

        self.lbl_time = QLabel(self.time_label_text)
        self.lbl_time.setStyleSheet("font-size: 11px; color: #9494B8; font-weight: 500;")
        top_row.addWidget(self.lbl_time)
        info_col.addLayout(top_row)

        # Bottom Row: Last Message Snippet + Unread Badge / Read Checks
        bot_row = QHBoxLayout()
        bot_row.setContentsMargins(0, 0, 0, 0)
        self.lbl_sub = QLabel(
            "Broadcast to all connected devices" if self.is_broadcast else self.ip
        )
        self.lbl_sub.setStyleSheet("font-size: 12px; color: #8696A0;")
        bot_row.addWidget(self.lbl_sub, 1)

        self.lbl_checks = QLabel("✓✓")
        self.lbl_checks.setStyleSheet("color: #9494B8; font-size: 11px; font-weight: bold;")
        self.lbl_checks.setVisible(not self.is_broadcast)
        bot_row.addWidget(self.lbl_checks)

        self.lbl_badge = QLabel("")
        self.lbl_badge.setStyleSheet(
            "background-color: #7C5CFC; color: #FFFFFF; font-weight: 800; "
            "font-size: 10px; border-radius: 9px; min-width: 18px; max-height: 18px; "
            "qproperty-alignment: AlignCenter; padding: 1px 5px;"
        )
        self.lbl_badge.setVisible(False)
        bot_row.addWidget(self.lbl_badge)
        info_col.addLayout(bot_row)

        layout.addLayout(info_col, 1)

    def _render_avatar(self):
        if self.is_broadcast:
            self.avatar.setStyleSheet(
                "background: qlineargradient(x1:0, y1:0, x2:1, y2:1, stop:0 #7C5CFC, stop:1 #4928BA); "
                "color: #FFFFFF; border-radius: 23px; font-size: 20px;"
            )
            self.avatar.setText("📢")
            return

        av = get_avatar(self.avatar_id)
        self.avatar.setStyleSheet(
            f"background: qlineargradient(x1:0, y1:0, x2:1, y2:1, stop:0 {av['bg']}, stop:1 #1E1338); "
            f"color: #FFFFFF; border-radius: 23px; font-size: 20px; border: 1px solid rgba(0, 0, 0, 0.06);"
        )
        self.avatar.setText(av["icon"])

    def _update_status_badge(self):
        if self.is_broadcast:
            self.status_badge.setVisible(False)
            return

        is_online = (self.status == "online")
        dot_color = "#00D26A" if is_online else "#B0B3C7"
        self.status_badge.setStyleSheet(
            f"background-color: {dot_color}; border: 2px solid #FFFFFF; border-radius: 6px;"
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

    def set_last_message(self, text: str, time_str: str = "now"):
        self.last_msg = text
        display_text = (text[:26] + "...") if len(text) > 26 else text
        self.lbl_sub.setText(display_text)
        self.lbl_time.setText(time_str)

    def increment_unread(self):
        self.unread_count += 1
        self.lbl_badge.setText(str(self.unread_count))
        self.lbl_badge.setVisible(True)
        self.lbl_checks.setVisible(False)

    def clear_unread(self):
        self.unread_count = 0
        self.lbl_badge.setVisible(False)
        self.lbl_checks.setVisible(not self.is_broadcast)


class PeerListSidebar(QWidget):
    """WhatsApp & Dribbble style Clean White Sidebar with Chips and Floating New Chat."""

    sig_peer_selected = pyqtSignal(str)
    sig_quick_scan = pyqtSignal()
    sig_quick_add = pyqtSignal()

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("sidebar")
        self.peer_widgets: Dict[str, PeerItemWidget] = {}
        self.current_filter = "todos"  # "todos", "unread", "grupos"
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        # 1. Header: "Chats" + Quick Scan
        header_widget = QWidget()
        header_widget.setObjectName("sidebarHeader")
        h_layout = QHBoxLayout(header_widget)
        h_layout.setContentsMargins(16, 14, 16, 6)

        lbl_title = QLabel("Chats")
        lbl_title.setObjectName("sidebarTitle")
        h_layout.addWidget(lbl_title)
        h_layout.addStretch()

        btn_scan = QPushButton("⚡")
        btn_scan.setToolTip("Scan local subnets for devices")
        btn_scan.setStyleSheet(
            "background: #F4F5FB; color: #7C5CFC; font-size: 14px; border: none; "
            "border-radius: 15px; min-width: 30px; min-height: 30px; font-weight: bold;"
        )
        btn_scan.setCursor(Qt.CursorShape.PointingHandCursor)
        btn_scan.clicked.connect(lambda: self.sig_quick_scan.emit())
        h_layout.addWidget(btn_scan)

        layout.addWidget(header_widget)

        # 2. Search Box Container
        search_box_container = QWidget()
        search_box_container.setObjectName("searchContainer")
        sb_layout = QHBoxLayout(search_box_container)
        sb_layout.setContentsMargins(14, 4, 14, 8)

        self.search_input = QLineEdit()
        self.search_input.setObjectName("searchBox")
        self.search_input.setPlaceholderText("🔍  Buscar dispositivos...")
        self.search_input.textChanged.connect(self._filter_peers)
        sb_layout.addWidget(self.search_input)

        layout.addWidget(search_box_container)

        # 3. Category Filter Chips (Todos, No leídos, Grupos)
        filter_bar = QWidget()
        filter_bar.setObjectName("filterBar")
        fb_layout = QHBoxLayout(filter_bar)
        fb_layout.setContentsMargins(14, 0, 14, 8)
        fb_layout.setSpacing(6)

        self.chip_all = QPushButton("Todos")
        self.chip_all.setProperty("class", "filterChip filterChipActive")
        self.chip_all.setCursor(Qt.CursorShape.PointingHandCursor)
        self.chip_all.clicked.connect(lambda: self._set_filter("todos"))
        fb_layout.addWidget(self.chip_all)

        self.chip_unread = QPushButton("No leídos")
        self.chip_unread.setProperty("class", "filterChip")
        self.chip_unread.setCursor(Qt.CursorShape.PointingHandCursor)
        self.chip_unread.clicked.connect(lambda: self._set_filter("unread"))
        fb_layout.addWidget(self.chip_unread)

        self.chip_groups = QPushButton("Grupos")
        self.chip_groups.setProperty("class", "filterChip")
        self.chip_groups.setCursor(Qt.CursorShape.PointingHandCursor)
        self.chip_groups.clicked.connect(lambda: self._set_filter("grupos"))
        fb_layout.addWidget(self.chip_groups)
        fb_layout.addStretch()

        layout.addWidget(filter_bar)

        # 4. Peer List View
        self.list_widget = QListWidget()
        self.list_widget.setObjectName("peerList")
        self.list_widget.itemClicked.connect(self._on_item_clicked)
        layout.addWidget(self.list_widget, 1)

        # 5. Bottom Floating Action: "Nuevo chat 💬+"
        btn_new_chat = QPushButton("Nuevo chat  ➕")
        btn_new_chat.setObjectName("btnNewChat")
        btn_new_chat.setCursor(Qt.CursorShape.PointingHandCursor)
        btn_new_chat.setToolTip("Connect new device by IP address or Playit link")
        btn_new_chat.clicked.connect(lambda: self.sig_quick_add.emit())
        layout.addWidget(btn_new_chat)

        # Pinned Broadcast Channel
        self._add_broadcast_channel()

    def _set_filter(self, filter_name: str):
        self.current_filter = filter_name

        self.chip_all.setProperty("class", "filterChip filterChipActive" if filter_name == "todos" else "filterChip")
        self.chip_unread.setProperty("class", "filterChip filterChipActive" if filter_name == "unread" else "filterChip")
        self.chip_groups.setProperty("class", "filterChip filterChipActive" if filter_name == "grupos" else "filterChip")

        self.chip_all.style().unpolish(self.chip_all)
        self.chip_all.style().polish(self.chip_all)
        self.chip_unread.style().unpolish(self.chip_unread)
        self.chip_unread.style().polish(self.chip_unread)
        self.chip_groups.style().unpolish(self.chip_groups)
        self.chip_groups.style().polish(self.chip_groups)

        self._filter_peers(self.search_input.text())

    def _add_broadcast_channel(self):
        item = QListWidgetItem()
        widget = PeerItemWidget(
            ip=BROADCAST_ID,
            username="All Devices (Broadcast)",
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
            widget.update_info(username=username, status=status, avatar_id=avatar_id)
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
            widget.set_last_message(text, time_str=time.strftime("%I:%M %p"))
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

    def _filter_peers(self, query: str = ""):
        query = query.lower().strip()
        for i in range(self.list_widget.count()):
            item = self.list_widget.item(i)
            ip = item.data(Qt.ItemDataRole.UserRole)
            widget = self.peer_widgets.get(ip)
            if not widget:
                continue

            # Query match
            match_query = (query in ip.lower()) or (query in widget.username.lower()) or (query in widget.last_msg.lower())

            # Filter chip match
            match_chip = True
            if self.current_filter == "unread":
                match_chip = widget.unread_count > 0
            elif self.current_filter == "grupos":
                match_chip = (ip == BROADCAST_ID)

            item.setHidden(not (match_query and match_chip))
