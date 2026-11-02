import webbrowser
from PyQt6.QtWidgets import (
    QDialog,
    QVBoxLayout,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QPushButton,
    QListWidget,
    QListWidgetItem,
    QMessageBox,
    QFrame,
)
from PyQt6.QtCore import Qt, pyqtSignal
from ..config import config


class TailscaleHelpDialog(QDialog):
    """Informational popup explaining how to connect friends outside the home via Tailscale."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("🌍 Connect with Friends Outside Your Home (Free)")
        self.setFixedSize(500, 390)
        self.setWindowFlags(self.windowFlags() & ~Qt.WindowType.WindowContextHelpButtonHint)
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(24, 20, 24, 20)
        layout.setSpacing(14)

        title = QLabel("🌍 How to Connect Across Different Homes / Cities")
        title.setStyleSheet("font-size: 16px; font-weight: bold; color: #00a884;")
        layout.addWidget(title)

        info_box = QFrame()
        info_box.setStyleSheet(
            "background-color: #202c33; border-radius: 8px; padding: 12px;"
        )
        box_layout = QVBoxLayout(info_box)
        box_layout.setSpacing(8)

        text = QLabel(
            "Home Wi-Fi routers have private IPs (192.168.x.x). If your friend lives in another house or city, you can connect <b>100% FREE</b> using Tailscale:<br><br>"
            "<b>1.</b> You and your friend both download <b>Tailscale</b> (free 1-click app):<br>"
            "&nbsp;&nbsp;&nbsp;&nbsp;👉 <a href='https://tailscale.com/download' style='color:#00a884;'>https://tailscale.com/download</a><br><br>"
            "<b>2.</b> Sign in with Google (takes 30 seconds).<br><br>"
            "<b>3.</b> Tailscale assigns both PCs a secure Virtual LAN IP (starts with <b>100.x.x.x</b>).<br><br>"
            "<b>4.</b> Enter your friend's <b>100.x.x.x IP</b> in the box and click Connect!"
        )
        text.setWordWrap(True)
        text.setTextInteractionFlags(Qt.TextInteractionFlag.TextSelectableByMouse)
        text.setStyleSheet("font-size: 13px; color: #e9edef; line-height: 1.4;")
        box_layout.addWidget(text)

        layout.addWidget(info_box)

        btn_row = QHBoxLayout()
        btn_website = QPushButton("🌐 Open Tailscale.com")
        btn_website.clicked.connect(
            lambda: webbrowser.open("https://tailscale.com/download")
        )
        btn_row.addWidget(btn_website)

        btn_gotit = QPushButton("I Got the IP — Enter Now")
        btn_gotit.setObjectName("primaryAction")
        btn_gotit.clicked.connect(self.accept)
        btn_row.addWidget(btn_gotit)

        layout.addLayout(btn_row)


class AddPeerDialog(QDialog):
    """Dialog to manually add a peer IP or perform an instant network sweep."""

    sig_peer_selected = pyqtSignal(str)

    def __init__(self, parent=None, network_engine=None):
        super().__init__(parent)
        self.engine = network_engine
        self.setWindowTitle("Connect PC by IP / Scan Network")
        self.setFixedSize(480, 470)
        self.setWindowFlags(self.windowFlags() & ~Qt.WindowType.WindowContextHelpButtonHint)
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(24, 20, 24, 20)
        layout.setSpacing(14)

        title = QLabel("🔍 Connect to PC / Laptop")
        title.setStyleSheet("font-size: 18px; font-weight: bold; color: #00a884;")
        layout.addWidget(title)

        desc = QLabel(
            "Enter the IP address of the device on your home network, or use Tailscale IP for friends in other locations."
        )
        desc.setWordWrap(True)
        desc.setStyleSheet("color: #8696a0; font-size: 12px;")
        layout.addWidget(desc)

        # Tailscale Helper Banner Button
        btn_tailscale = QPushButton(
            "🌍 Friend in another city? Click for Free Tailscale Guide"
        )
        btn_tailscale.setStyleSheet(
            "background-color: #1f2c34; color: #00a884; border: 1px dashed #00a884; font-weight: bold; padding: 8px; border-radius: 8px;"
        )
        btn_tailscale.setCursor(Qt.CursorShape.PointingHandCursor)
        btn_tailscale.clicked.connect(self._open_tailscale_popup)
        layout.addWidget(btn_tailscale)

        # Manual IP input
        input_layout = QHBoxLayout()
        self.ip_input = QLineEdit()
        self.ip_input.setPlaceholderText(
            "e.g. 192.168.7.5, 192.168.100.8, or Tailscale 100.x.x.x"
        )
        btn_connect = QPushButton("Connect")
        btn_connect.setObjectName("primaryAction")
        btn_connect.clicked.connect(self._on_manual_add)
        input_layout.addWidget(self.ip_input)
        input_layout.addWidget(btn_connect)
        layout.addLayout(input_layout)

        # Scan section
        scan_layout = QHBoxLayout()
        self.lbl_scan_status = QLabel(
            "Home Subnets: 192.168.100.x & 192.168.7.x"
        )
        self.lbl_scan_status.setStyleSheet("color: #8696a0; font-size: 12px;")
        self.btn_scan = QPushButton("⚡ Scan LAN")
        self.btn_scan.clicked.connect(self._on_scan_clicked)
        scan_layout.addWidget(self.lbl_scan_status)
        scan_layout.addStretch()
        scan_layout.addWidget(self.btn_scan)
        layout.addLayout(scan_layout)

        # Found list
        lbl_found = QLabel("Discovered / Saved Devices:")
        lbl_found.setStyleSheet(
            "font-weight: 600; color: #e9edef; font-size: 13px;"
        )
        layout.addWidget(lbl_found)

        self.list_widget = QListWidget()
        self.list_widget.itemDoubleClicked.connect(self._on_item_double_clicked)
        layout.addWidget(self.list_widget)

        # Populate with existing peers if any
        if self.engine:
            for ip, pinfo in self.engine.peers.items():
                if ip == "BROADCAST":
                    continue
                status_icon = (
                    "🟢" if pinfo.get("status") == "online" else "⚪"
                )
                item = QListWidgetItem(
                    f"{status_icon} {pinfo.get('username', 'PC')} — {ip}"
                )
                item.setData(Qt.ItemDataRole.UserRole, ip)
                self.list_widget.addItem(item)

    def _open_tailscale_popup(self):
        dlg = TailscaleHelpDialog(self)
        if dlg.exec():
            self.ip_input.setFocus()

    def _on_manual_add(self):
        ip = self.ip_input.text().strip()
        parts = ip.split(".")
        if len(parts) != 4 or not all(
            p.isdigit() and 0 <= int(p) <= 255 for p in parts
        ):
            QMessageBox.warning(
                self,
                "Invalid IP",
                "Please enter a valid IPv4 address (e.g. 192.168.7.12 or Tailscale 100.x.x.x)",
            )
            return

        if self.engine:
            self.engine.add_manual_peer(ip)

        self.sig_peer_selected.emit(ip)
        self.accept()

    def _on_scan_clicked(self):
        self.btn_scan.setEnabled(False)
        self.btn_scan.setText("Scanning...")
        self.lbl_scan_status.setText("Scanning 500 IPs across both subnets...")

        if self.engine:
            self.engine.sig_sweep_completed.connect(self._on_sweep_done)
            self.engine.scan_subnets()

    def _on_sweep_done(self, count: int):
        self.btn_scan.setEnabled(True)
        self.btn_scan.setText("⚡ Scan LAN")
        self.lbl_scan_status.setText(f"Scan finished! Found {count} device(s).")

        self.list_widget.clear()
        if self.engine:
            for ip, pinfo in self.engine.peers.items():
                if ip == "BROADCAST":
                    continue
                status_icon = (
                    "🟢" if pinfo.get("status") == "online" else "⚪"
                )
                item = QListWidgetItem(
                    f"{status_icon} {pinfo.get('username', 'PC')} — {ip}"
                )
                item.setData(Qt.ItemDataRole.UserRole, ip)
                self.list_widget.addItem(item)

    def _on_item_double_clicked(self, item: QListWidgetItem):
        ip = item.data(Qt.ItemDataRole.UserRole)
        if ip:
            self.sig_peer_selected.emit(ip)
            self.accept()
