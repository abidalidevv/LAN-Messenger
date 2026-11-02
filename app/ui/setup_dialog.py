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
    """Modern configuration dialog with 20 prebuilt avatar picker and email."""

    def __init__(self, parent=None, is_settings_mode: bool = False):
        super().__init__(parent)
        self.is_settings_mode = is_settings_mode
        self.setWindowTitle(
            "Settings — LAN Messenger"
            if is_settings_mode
            else "Welcome to LAN Messenger"
        )
        self.setFixedSize(540, 620)
        self.setWindowFlags(self.windowFlags() & ~Qt.WindowType.WindowContextHelpButtonHint)
        self.selected_avatar_id = config.avatar_id
        self.avatar_buttons = {}
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(24, 20, 24, 20)
        layout.setSpacing(12)

        # Title / Header
        title_label = QLabel(
            "⚙️ Settings & Profile"
            if self.is_settings_mode
            else "🚀 Welcome! Setup Your Profile"
        )
        title_label.setStyleSheet(
            "font-size: 18px; font-weight: bold; color: #00a884;"
        )
        layout.addWidget(title_label)

        sub_label = QLabel(
            "Choose your display name, avatar, and settings. Devices on your home network will see this profile."
        )
        sub_label.setWordWrap(True)
        sub_label.setStyleSheet("color: #8696a0; font-size: 12px;")
        layout.addWidget(sub_label)

        # Name and Email in horizontal row
        inputs_row = QHBoxLayout()

        col_name = QVBoxLayout()
        name_title = QLabel("Display Name:")
        name_title.setStyleSheet("font-weight: 600; font-size: 13px; color: #e9edef;")
        self.name_input = QLineEdit()
        self.name_input.setText(config.username)
        self.name_input.setPlaceholderText("e.g. Abid Laptop, Bilal PC")
        col_name.addWidget(name_title)
        col_name.addWidget(self.name_input)
        inputs_row.addLayout(col_name, 1)

        col_email = QVBoxLayout()
        email_title = QLabel("Email (Optional):")
        email_title.setStyleSheet("font-weight: 600; font-size: 13px; color: #e9edef;")
        self.email_input = QLineEdit()
        self.email_input.setText(config.email)
        self.email_input.setPlaceholderText("yourname@example.com")
        col_email.addWidget(email_title)
        col_email.addWidget(self.email_input)
        inputs_row.addLayout(col_email, 1)

        layout.addLayout(inputs_row)

        # Avatar Selector Header
        lbl_avatar_sec = QLabel("Choose Your Avatar (20 Prebuilt Styles):")
        lbl_avatar_sec.setStyleSheet(
            "font-weight: 600; font-size: 13px; color: #e9edef; margin-top: 4px;"
        )
        layout.addWidget(lbl_avatar_sec)

        # Avatar Scroll Area (Grid of 20 avatars)
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFixedHeight(220)
        scroll.setStyleSheet(
            "background-color: #111b21; border: 1px solid #2a3942; border-radius: 8px;"
        )

        grid_widget = QWidget()
        grid_layout = QGridLayout(grid_widget)
        grid_layout.setContentsMargins(8, 8, 8, 8)
        grid_layout.setSpacing(8)

        cols = 5
        for idx, av in enumerate(AVATARS):
            btn = QPushButton(f"{av['icon']}\n{av['name']}")
            btn.setFixedSize(92, 70)
            btn.setCursor(Qt.CursorShape.PointingHandCursor)
            btn.clicked.connect(
                lambda checked, aid=av["id"]: self._select_avatar(aid)
            )

            is_sel = av["id"] == self.selected_avatar_id
            border_style = (
                "2px solid #00a884" if is_sel else "1px solid #2a3942"
            )
            btn.setStyleSheet(
                f"background-color: {av['bg']}; color: #ffffff; border: {border_style}; border-radius: 10px; font-weight: bold; font-size: 11px;"
            )

            self.avatar_buttons[av["id"]] = btn
            grid_layout.addWidget(btn, idx // cols, idx % cols)

        scroll.setWidget(grid_widget)
        layout.addWidget(scroll)

        # Download Directory input
        dir_title = QLabel("Save Received Files To:")
        dir_title.setStyleSheet("font-weight: 600; font-size: 13px; color: #e9edef;")
        layout.addWidget(dir_title)

        dir_box = QHBoxLayout()
        self.dir_input = QLineEdit()
        self.dir_input.setText(config.download_dir)
        self.dir_input.setReadOnly(True)
        btn_browse = QPushButton("Browse...")
        btn_browse.clicked.connect(self._browse_folder)
        dir_box.addWidget(self.dir_input)
        dir_box.addWidget(btn_browse)
        layout.addLayout(dir_box)

        layout.addStretch()

        # Save Button
        btn_save = QPushButton(
            "Save Changes" if self.is_settings_mode else "Get Started"
        )
        btn_save.setObjectName("primaryAction")
        btn_save.clicked.connect(self._save_and_close)
        layout.addWidget(btn_save)

    def _select_avatar(self, avatar_id: str):
        self.selected_avatar_id = avatar_id
        for aid, btn in self.avatar_buttons.items():
            av = get_avatar(aid)
            is_sel = aid == avatar_id
            border_style = (
                "3px solid #00a884" if is_sel else "1px solid #2a3942"
            )
            btn.setStyleSheet(
                f"background-color: {av['bg']}; color: #ffffff; border: {border_style}; border-radius: 10px; font-weight: bold; font-size: 11px;"
            )

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
