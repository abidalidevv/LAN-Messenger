from PyQt6.QtWidgets import (
    QDialog,
    QVBoxLayout,
    QHBoxLayout,
    QGridLayout,
    QLabel,
    QLineEdit,
    QPushButton,
    QFileDialog,
    QMessageBox,
    QScrollArea,
    QWidget,
    QFrame,
)
from PyQt6.QtCore import Qt
from ..config import config
from ..utils.avatars import AVATARS, get_avatar


class SetupDialog(QDialog):
    """WhatsApp & Telegram Desktop styled Profile & Settings Dialog."""

    def __init__(self, parent=None, is_settings_mode: bool = False):
        super().__init__(parent)
        self.is_settings_mode = is_settings_mode
        self.setWindowTitle(
            "Settings & Profile — LAN Messenger"
            if is_settings_mode
            else "Welcome — Setup Your Profile"
        )
        self.setFixedSize(560, 680)
        self.setWindowFlags(self.windowFlags() & ~Qt.WindowType.WindowContextHelpButtonHint)
        self.selected_avatar_id = config.avatar_id
        self.avatar_chips = {}
        self.init_ui()

    def init_ui(self):
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(24, 20, 24, 20)
        main_layout.setSpacing(16)

        # 1. Header Banner Profile Card
        banner_card = QFrame()
        banner_card.setStyleSheet(
            "background: qlineargradient(x1:0, y1:0, x2:1, y2:1, stop:0 #1f2c34, stop:1 #111b21); "
            "border: 1px solid #2a3942; border-radius: 12px; padding: 12px 16px;"
        )
        b_layout = QHBoxLayout(banner_card)
        b_layout.setSpacing(16)

        # Large Avatar Preview
        self.big_avatar = QLabel()
        self.big_avatar.setFixedSize(68, 68)
        self.big_avatar.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self._update_big_avatar()
        b_layout.addWidget(self.big_avatar)

        # Profile Text Info
        p_info = QVBoxLayout()
        p_info.setSpacing(3)
        self.lbl_card_title = QLabel(config.username or "My PC")
        self.lbl_card_title.setStyleSheet("font-size: 18px; font-weight: 700; color: #e9edef;")
        
        self.lbl_card_sub = QLabel("LAN Messenger Profile • Visible to nearby devices")
        self.lbl_card_sub.setStyleSheet("font-size: 12px; color: #8696a0;")

        badge_row = QHBoxLayout()
        badge_row.setSpacing(6)
        lbl_status_chip = QLabel("🟢 Online on LAN")
        lbl_status_chip.setStyleSheet(
            "background-color: rgba(0, 168, 132, 0.15); color: #00a884; "
            "font-weight: 600; font-size: 11px; padding: 2px 8px; border-radius: 6px;"
        )
        badge_row.addWidget(lbl_status_chip)
        badge_row.addStretch()

        p_info.addWidget(self.lbl_card_title)
        p_info.addWidget(self.lbl_card_sub)
        p_info.addLayout(badge_row)
        b_layout.addLayout(p_info, 1)

        main_layout.addWidget(banner_card)

        # 2. Form Inputs Section
        form_card = QFrame()
        form_card.setStyleSheet(
            "background-color: #202c33; border: 1px solid #2a3942; border-radius: 12px; padding: 14px;"
        )
        f_layout = QVBoxLayout(form_card)
        f_layout.setSpacing(12)

        # Name and Email Row
        inputs_row = QHBoxLayout()
        inputs_row.setSpacing(12)

        col_name = QVBoxLayout()
        col_name.setSpacing(4)
        name_title = QLabel("Display Name:")
        name_title.setStyleSheet("font-weight: 600; font-size: 12px; color: #aebac1;")
        self.name_input = QLineEdit()
        self.name_input.setText(config.username)
        self.name_input.setPlaceholderText("e.g. Abid Laptop")
        self.name_input.textChanged.connect(lambda t: self.lbl_card_title.setText(t or "My PC"))
        col_name.addWidget(name_title)
        col_name.addWidget(self.name_input)
        inputs_row.addLayout(col_name, 1)

        col_email = QVBoxLayout()
        col_email.setSpacing(4)
        email_title = QLabel("Email (Optional):")
        email_title.setStyleSheet("font-weight: 600; font-size: 12px; color: #aebac1;")
        self.email_input = QLineEdit()
        self.email_input.setText(config.email)
        self.email_input.setPlaceholderText("your@email.com")
        col_email.addWidget(email_title)
        col_email.addWidget(self.email_input)
        inputs_row.addLayout(col_email, 1)

        f_layout.addLayout(inputs_row)

        # Download Directory
        dir_col = QVBoxLayout()
        dir_col.setSpacing(4)
        dir_title = QLabel("Save Downloads To:")
        dir_title.setStyleSheet("font-weight: 600; font-size: 12px; color: #aebac1;")
        dir_col.addWidget(dir_title)

        dir_box = QHBoxLayout()
        dir_box.setSpacing(8)
        self.dir_input = QLineEdit()
        self.dir_input.setText(config.download_dir)
        self.dir_input.setReadOnly(True)
        btn_browse = QPushButton("📁 Browse")
        btn_browse.clicked.connect(self._browse_folder)
        dir_box.addWidget(self.dir_input, 1)
        dir_box.addWidget(btn_browse)
        dir_col.addLayout(dir_box)

        f_layout.addLayout(dir_col)
        main_layout.addWidget(form_card)

        # 3. Avatar Gallery (Circular WhatsApp Chips)
        lbl_avatar_sec = QLabel("Choose Your Avatar Style:")
        lbl_avatar_sec.setStyleSheet("font-weight: 600; font-size: 13px; color: #e9edef;")
        main_layout.addWidget(lbl_avatar_sec)

        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFixedHeight(180)
        scroll.setStyleSheet(
            "background-color: #111b21; border: 1px solid #222d34; border-radius: 10px;"
        )

        grid_widget = QWidget()
        grid_layout = QGridLayout(grid_widget)
        grid_layout.setContentsMargins(10, 10, 10, 10)
        grid_layout.setSpacing(10)

        cols = 5
        for idx, av in enumerate(AVATARS):
            chip = QPushButton(av["icon"])
            chip.setFixedSize(54, 54)
            chip.setCursor(Qt.CursorShape.PointingHandCursor)
            chip.setToolTip(av["name"])
            chip.clicked.connect(lambda checked, aid=av["id"]: self._select_avatar(aid))

            self.avatar_chips[av["id"]] = chip
            grid_layout.addWidget(chip, idx // cols, idx % cols)

        self._refresh_avatar_chips()
        scroll.setWidget(grid_widget)
        main_layout.addWidget(scroll)

        main_layout.addStretch()

        # 4. Save Button
        btn_save = QPushButton("Save Profile & Close" if self.is_settings_mode else "🚀 Start LAN Messenger")
        btn_save.setObjectName("primaryAction")
        btn_save.setMinimumHeight(44)
        btn_save.clicked.connect(self._save_and_close)
        main_layout.addWidget(btn_save)

    def _update_big_avatar(self):
        av = get_avatar(self.selected_avatar_id)
        self.big_avatar.setStyleSheet(
            f"background: qlineargradient(x1:0, y1:0, x2:1, y2:1, stop:0 {av['bg']}, stop:1 #111b21); "
            f"color: #ffffff; border-radius: 34px; font-size: 32px; border: 3px solid #00a884;"
        )
        self.big_avatar.setText(av["icon"])

    def _refresh_avatar_chips(self):
        for aid, chip in self.avatar_chips.items():
            av = get_avatar(aid)
            is_sel = (aid == self.selected_avatar_id)
            if is_sel:
                chip.setStyleSheet(
                    f"background: {av['bg']}; color: #ffffff; border: 3px solid #00a884; "
                    f"border-radius: 27px; font-size: 24px;"
                )
            else:
                chip.setStyleSheet(
                    f"background: {av['bg']}; color: #ffffff; border: 1px solid rgba(255,255,255,0.1); "
                    f"border-radius: 27px; font-size: 22px;"
                )

    def _select_avatar(self, avatar_id: str):
        self.selected_avatar_id = avatar_id
        self._update_big_avatar()
        self._refresh_avatar_chips()

    def _browse_folder(self):
        folder = QFileDialog.getExistingDirectory(
            self, "Select Download Folder", self.dir_input.text()
        )
        if folder:
            self.dir_input.setText(folder)

    def _save_and_close(self):
        new_name = self.name_input.text().strip()
        if not new_name:
            QMessageBox.warning(self, "Invalid Name", "Please enter a display name.")
            return

        config.username = new_name
        config.email = self.email_input.text().strip()
        config.avatar_id = self.selected_avatar_id
        config.download_dir = self.dir_input.text()
        config.is_configured = True
        self.accept()
