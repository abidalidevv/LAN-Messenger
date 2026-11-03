import os
from typing import Dict, Any, List, Optional
from PyQt6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QGridLayout,
    QLabel,
    QPushButton,
    QScrollArea,
    QFrame,
    QApplication,
    QMessageBox,
)
from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QPixmap
from ..utils.avatars import get_avatar
from ..utils.file_helper import get_file_category, format_size, open_file_default


class PeerInfoPanel(QWidget):
    """WhatsApp & Dribbble style Right Details Panel (Info. del grupo / Peer Details)."""

    sig_close_panel = pyqtSignal()
    sig_start_call = pyqtSignal(str)
    sig_start_screen = pyqtSignal(str)
    sig_open_file = pyqtSignal(str)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("rightInfoPanel")
        self.current_peer_ip: Optional[str] = None
        self.current_username: str = ""
        self.current_avatar_id: str = "gamer"
        self.current_status: str = "online"
        self.shared_photos: List[str] = []
        self.shared_docs: List[Dict[str, Any]] = []

        self.init_ui()

    def init_ui(self):
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)

        # 1. Header: "Info. del grupo" + Close "✕"
        header_widget = QWidget()
        header_widget.setObjectName("infoPanelHeader")
        h_layout = QHBoxLayout(header_widget)
        h_layout.setContentsMargins(18, 14, 18, 10)

        self.lbl_title = QLabel("Info. del grupo")
        self.lbl_title.setObjectName("infoPanelTitle")
        h_layout.addWidget(self.lbl_title)
        h_layout.addStretch()

        btn_close = QPushButton("✕")
        btn_close.setObjectName("btnCloseInfo")
        btn_close.setCursor(Qt.CursorShape.PointingHandCursor)
        btn_close.clicked.connect(lambda: self.sig_close_panel.emit())
        h_layout.addWidget(btn_close)

        main_layout.addWidget(header_widget)

        # Scroll Area for Content
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setStyleSheet("background: transparent; border: none;")
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)

        content = QWidget()
        content.setStyleSheet("background: transparent;")
        c_layout = QVBoxLayout(content)
        c_layout.setContentsMargins(12, 10, 12, 16)
        c_layout.setSpacing(14)

        # 2. Hero Profile Card
        hero_card = QWidget()
        hero_layout = QVBoxLayout(hero_card)
        hero_layout.setContentsMargins(0, 8, 0, 8)
        hero_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        hero_layout.setSpacing(8)

        self.big_avatar = QLabel()
        self.big_avatar.setFixedSize(86, 86)
        self.big_avatar.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.big_avatar.setStyleSheet(
            "background: qlineargradient(x1:0, y1:0, x2:1, y2:1, stop:0 #7C5CFC, stop:1 #4928BA); "
            "color: #FFFFFF; font-size: 38px; border-radius: 43px; border: 3px solid rgba(255, 255, 255, 0.15);"
        )
        self.big_avatar.setText("💻")
        hero_layout.addWidget(self.big_avatar, alignment=Qt.AlignmentFlag.AlignCenter)

        self.lbl_hero_name = QLabel("Select a Device")
        self.lbl_hero_name.setStyleSheet(
            "font-size: 18px; font-weight: 800; color: #FFFFFF;"
        )
        hero_layout.addWidget(self.lbl_hero_name, alignment=Qt.AlignmentFlag.AlignCenter)

        self.lbl_hero_sub = QLabel("No active chat selected")
        self.lbl_hero_sub.setStyleSheet("font-size: 12px; color: #A599C8;")
        hero_layout.addWidget(self.lbl_hero_sub, alignment=Qt.AlignmentFlag.AlignCenter)

        # 3. Four Quick Action Chips Row
        actions_row = QHBoxLayout()
        actions_row.setSpacing(12)
        actions_row.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.btn_call = QPushButton("📞")
        self.btn_call.setProperty("class", "infoActionChip")
        self.btn_call.setToolTip("Start Voice Call")
        self.btn_call.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_call.clicked.connect(self._on_call)
        actions_row.addWidget(self.btn_call)

        self.btn_screen = QPushButton("🖥️")
        self.btn_screen.setProperty("class", "infoActionChip")
        self.btn_screen.setToolTip("Start Screen Share")
        self.btn_screen.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_screen.clicked.connect(self._on_screen)
        actions_row.addWidget(self.btn_screen)

        self.btn_star = QPushButton("⭐")
        self.btn_star.setProperty("class", "infoActionChip")
        self.btn_star.setToolTip("Add to Favorites")
        self.btn_star.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_star.clicked.connect(self._toggle_star)
        actions_row.addWidget(self.btn_star)

        self.btn_mute = QPushButton("🔔")
        self.btn_mute.setProperty("class", "infoActionChip")
        self.btn_mute.setToolTip("Toggle Notifications")
        self.btn_mute.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_mute.clicked.connect(self._toggle_mute)
        actions_row.addWidget(self.btn_mute)

        hero_layout.addLayout(actions_row)
        c_layout.addWidget(hero_card)

        # 4. Section: Fotos y Videos
        self.photos_card = QFrame()
        self.photos_card.setProperty("class", "infoSectionCard")
        p_layout = QVBoxLayout(self.photos_card)
        p_layout.setContentsMargins(10, 10, 10, 10)
        p_layout.setSpacing(8)

        ph_hdr = QHBoxLayout()
        self.lbl_photos_count = QLabel("Fotos y Videos")
        self.lbl_photos_count.setProperty("class", "infoSectionHeader")
        ph_hdr.addWidget(self.lbl_photos_count)
        ph_hdr.addStretch()
        lbl_v1 = QLabel("Ver todo")
        lbl_v1.setProperty("class", "infoSectionLink")
        ph_hdr.addWidget(lbl_v1)
        p_layout.addLayout(ph_hdr)

        # Grid of photo thumbnails
        self.photo_grid = QGridLayout()
        self.photo_grid.setSpacing(6)
        self.photo_thumbs = []
        for i in range(4):
            thumb = QLabel("🖼️")
            thumb.setFixedSize(58, 58)
            thumb.setAlignment(Qt.AlignmentFlag.AlignCenter)
            thumb.setStyleSheet(
                "background-color: #382866; border-radius: 10px; font-size: 18px; color: #FFFFFF;"
            )
            self.photo_grid.addWidget(thumb, i // 2, i % 2)
            self.photo_thumbs.append(thumb)
        p_layout.addLayout(self.photo_grid)
        c_layout.addWidget(self.photos_card)

        # 5. Section: Documentos
        self.docs_card = QFrame()
        self.docs_card.setProperty("class", "infoSectionCard")
        d_layout = QVBoxLayout(self.docs_card)
        d_layout.setContentsMargins(10, 10, 10, 10)
        d_layout.setSpacing(8)

        dh_hdr = QHBoxLayout()
        self.lbl_docs_count = QLabel("Documentos")
        self.lbl_docs_count.setProperty("class", "infoSectionHeader")
        dh_hdr.addWidget(self.lbl_docs_count)
        dh_hdr.addStretch()
        lbl_v2 = QLabel("Ver todo")
        lbl_v2.setProperty("class", "infoSectionLink")
        dh_hdr.addWidget(lbl_v2)
        d_layout.addLayout(dh_hdr)

        self.docs_list_layout = QVBoxLayout()
        self.docs_list_layout.setSpacing(6)
        d_layout.addLayout(self.docs_list_layout)

        self._render_sample_docs()
        c_layout.addWidget(self.docs_card)

        # 6. Section: Links & Network
        self.links_card = QFrame()
        self.links_card.setProperty("class", "infoSectionCard")
        l_layout = QVBoxLayout(self.links_card)
        l_layout.setContentsMargins(10, 10, 10, 10)
        l_layout.setSpacing(8)

        lh_hdr = QHBoxLayout()
        lbl_links = QLabel("Links y Red LAN")
        lbl_links.setProperty("class", "infoSectionHeader")
        lh_hdr.addWidget(lbl_links)
        lh_hdr.addStretch()
        l_layout.addLayout(lh_hdr)

        self.lbl_network_desc = QLabel(
            "<b>Dual Subnets:</b> Huawei 192.168.100.x & Tenda 192.168.7.x<br>"
            "<b>Playit Hub:</b> <code style='color:#E0DAFD;'>shrimp-cigars.tun.ply.gg</code>"
        )
        self.lbl_network_desc.setTextInteractionFlags(Qt.TextInteractionFlag.TextSelectableByMouse)
        self.lbl_network_desc.setStyleSheet("color: #A599C8; font-size: 11px; line-height: 1.4;")
        l_layout.addWidget(self.lbl_network_desc)

        c_layout.addWidget(self.links_card)
        c_layout.addStretch()

        scroll.setWidget(content)
        main_layout.addWidget(scroll, 1)

    def set_peer_info(
        self,
        ip: str,
        username: str,
        status: str = "online",
        avatar_id: str = "gamer",
    ):
        self.current_peer_ip = ip
        self.current_username = username
        self.current_avatar_id = avatar_id
        self.current_status = status

        if ip == "BROADCAST":
            self.lbl_title.setText("Info. del grupo")
            self.lbl_hero_name.setText("All Devices (Broadcast)")
            self.lbl_hero_sub.setText("Reaches all local PCs, laptops & phones")
            self.big_avatar.setText("📢")
            self.big_avatar.setStyleSheet(
                "background: qlineargradient(x1:0, y1:0, x2:1, y2:1, stop:0 #7C5CFC, stop:1 #4928BA); "
                "color: #FFFFFF; font-size: 38px; border-radius: 43px;"
            )
            self.btn_call.setVisible(False)
            self.btn_screen.setVisible(False)
        else:
            self.lbl_title.setText("Detalles del dispositivo")
            self.lbl_hero_name.setText(username)
            status_text = "🟢 En línea" if status == "online" else "⚪ Desconectado"
            self.lbl_hero_sub.setText(f"{ip} • {status_text}")

            av = get_avatar(avatar_id)
            self.big_avatar.setText(av["icon"])
            self.big_avatar.setStyleSheet(
                f"background: qlineargradient(x1:0, y1:0, x2:1, y2:1, stop:0 {av['bg']}, stop:1 #1E1338); "
                f"color: #FFFFFF; font-size: 38px; border-radius: 43px; border: 3px solid rgba(255, 255, 255, 0.15);"
            )
            self.btn_call.setVisible(True)
            self.btn_screen.setVisible(True)

    def add_shared_file(self, filepath: str, filename: str, filesize: int):
        cat = get_file_category(filename)
        if cat == "image" and os.path.exists(filepath):
            if filepath not in self.shared_photos:
                self.shared_photos.insert(0, filepath)
                self._update_photos_grid()
        else:
            doc_entry = {"path": filepath, "name": filename, "size": filesize}
            if doc_entry not in self.shared_docs:
                self.shared_docs.insert(0, doc_entry)
                self._update_docs_list()

    def _update_photos_grid(self):
        count = len(self.shared_photos)
        self.lbl_photos_count.setText(f"Fotos y Videos {count}")
        for idx, thumb in enumerate(self.photo_thumbs):
            if idx < len(self.shared_photos):
                img_path = self.shared_photos[idx]
                pix = QPixmap(img_path)
                if not pix.isNull():
                    scaled = pix.scaled(
                        58, 58,
                        Qt.AspectRatioMode.KeepAspectRatioByExpanding,
                        Qt.TransformationMode.SmoothTransformation
                    )
                    thumb.setPixmap(scaled)
                    thumb.setCursor(Qt.CursorShape.PointingHandCursor)
                    thumb.mousePressEvent = lambda e, p=img_path: open_file_default(p)

    def _update_docs_list(self):
        count = len(self.shared_docs)
        self.lbl_docs_count.setText(f"Documentos {count}")

        # Clear existing
        while self.docs_list_layout.count():
            item = self.docs_list_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()

        for doc in self.shared_docs[:4]:
            card = QFrame()
            card.setStyleSheet(
                "background-color: rgba(255, 255, 255, 0.05); border-radius: 8px; padding: 6px;"
            )
            h = QHBoxLayout(card)
            h.setContentsMargins(4, 2, 4, 2)
            h.setSpacing(8)

            lbl_icon = QLabel("📄")
            lbl_icon.setStyleSheet("font-size: 16px;")
            h.addWidget(lbl_icon)

            col = QVBoxLayout()
            col.setSpacing(1)
            name_lbl = QLabel(doc["name"])
            name_lbl.setStyleSheet("color: #FFFFFF; font-size: 11px; font-weight: 600;")
            sub_lbl = QLabel(format_size(doc["size"]))
            sub_lbl.setStyleSheet("color: #A599C8; font-size: 10px;")
            col.addWidget(name_lbl)
            col.addWidget(sub_lbl)
            h.addLayout(col, 1)

            btn_open = QPushButton("Open")
            btn_open.setStyleSheet(
                "background-color: #7C5CFC; color: #FFFFFF; font-size: 10px; "
                "padding: 3px 8px; border-radius: 6px; font-weight: bold; border: none;"
            )
            btn_open.clicked.connect(lambda ch, p=doc["path"]: open_file_default(p))
            h.addWidget(btn_open)

            self.docs_list_layout.addWidget(card)

    def _render_sample_docs(self):
        # Initial sample placeholders as seen in mockup
        sample_data = [
            {"path": "", "name": "UX Writing | colocar en la...", "size": 2450000},
            {"path": "", "name": "Banners de ofertas BlackFriday...", "size": 8900000},
        ]
        self.shared_docs = sample_data
        self._update_docs_list()

    def _on_call(self):
        if self.current_peer_ip and self.current_peer_ip != "BROADCAST":
            self.sig_start_call.emit(self.current_peer_ip)

    def _on_screen(self):
        if self.current_peer_ip and self.current_peer_ip != "BROADCAST":
            self.sig_start_screen.emit(self.current_peer_ip)

    def _toggle_star(self):
        QMessageBox.information(
            self, "Favorite", f"{self.current_username or 'Peer'} marked as favorite!"
        )

    def _toggle_mute(self):
        QMessageBox.information(
            self, "Notifications", f"Notifications updated for {self.current_username or 'Peer'}."
        )

