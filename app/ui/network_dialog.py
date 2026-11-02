import socket
from PyQt6.QtWidgets import (
    QDialog,
    QVBoxLayout,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QTextBrowser,
)
from PyQt6.QtCore import Qt
from ..config import config
from ..network.discovery import get_local_ip_addresses


class NetworkStatusDialog(QDialog):
    """Displays local network parameters and dual router configuration tips."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Network Info & Dual-Router Guide")
        self.setFixedSize(540, 480)
        self.setWindowFlags(self.windowFlags() & ~Qt.WindowType.WindowContextHelpButtonHint)
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(24, 24, 24, 24)
        layout.setSpacing(14)

        title = QLabel("🌐 Network Diagnostics & Guide")
        title.setStyleSheet("font-size: 18px; font-weight: bold; color: #00a884;")
        layout.addWidget(title)

        local_ips = get_local_ip_addresses()
        ip_str = ", ".join(local_ips) if local_ips else "127.0.0.1"

        info_box = QLabel(
            f"<b>PC Name:</b> {socket.gethostname()}<br>"
            f"<b>Local IP:</b> <span style='color: #00a884;'>{ip_str}</span><br>"
            f"<b>TCP Port:</b> {config.tcp_port} &nbsp;|&nbsp; <b>UDP Port:</b> {config.udp_port}<br>"
            f"<b>Monitored Subnets:</b> {', '.join(config.custom_subnets)}"
        )
        info_box.setStyleSheet(
            "background-color: #202c33; padding: 12px; border-radius: 8px; font-size: 13px;"
        )
        layout.addWidget(info_box)

        guide_label = QLabel("Huawei + Tenda Router Setup Tips:")
        guide_label.setStyleSheet("font-weight: 600; color: #e9edef;")
        layout.addWidget(guide_label)

        browser = QTextBrowser()
        browser.setStyleSheet(
            "background-color: #111b21; border: 1px solid #2a3942; border-radius: 8px; font-size: 12px; color: #8696a0;"
        )
        browser.setHtml(
            """
            <h4 style="color: #00a884; margin-top: 0;">1. How Cross-Subnet Works Here:</h4>
            <p>Our app automatically broadcasts to both <b>192.168.100.255</b> (Huawei) and <b>192.168.7.255</b> (Tenda). 
            Even if your laptop is on Huawei Wi-Fi and PCs are on Tenda wired hub, the background sweep scans both subnets and establishes an instant reverse tunnel.</p>

            <h4 style="color: #00a884;">2. Best Practice (Single Subnet - Optional):</h4>
            <p>If you ever want maximum seamless performance across all devices without NAT:</p>
            <ul>
              <li>Plug Huawei router's LAN cable into a <b>LAN port</b> on Tenda (not the blue WAN port).</li>
              <li>Turn off DHCP server on Tenda router.</li>
              <li>Now all PCs and laptops receive 192.168.100.x IPs automatically!</li>
            </ul>

            <h4 style="color: #00a884;">3. Windows Firewall:</h4>
            <p>When running LAN Messenger for the first time, click <b>'Allow access'</b> on the Windows Defender Firewall prompt for Private Networks so other PCs can connect to you.</p>
            """
        )
        layout.addWidget(browser)

        btn_close = QPushButton("Got It")
        btn_close.setObjectName("primaryAction")
        btn_close.clicked.connect(self.accept)
        layout.addWidget(btn_close)

