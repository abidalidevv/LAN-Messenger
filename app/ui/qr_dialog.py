import io
import qrcode
from PyQt6.QtWidgets import (
    QDialog,
    QVBoxLayout,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QApplication,
    QMessageBox,
)
from PyQt6.QtGui import QPixmap, QImage
from PyQt6.QtCore import Qt
from ..network.discovery import get_local_ip_addresses


class QRCodeDialog(QDialog):
    """Dialog displaying QR Code and Web Portal link for mobile phone pairing."""

    def __init__(self, port: int = 9878, parent=None):
        super().__init__(parent)
        self.port = port
        self.setWindowTitle("Connect Mobile Phone — LAN Messenger")
        self.setFixedSize(450, 520)
        self.setWindowFlags(self.windowFlags() & ~Qt.WindowType.WindowContextHelpButtonHint)
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(28, 24, 28, 24)
        layout.setSpacing(14)

        # Title
        title = QLabel("📱 Connect Phone via QR Code")
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title.setStyleSheet("font-size: 18px; font-weight: bold; color: #00a884;")
        layout.addWidget(title)

        sub = QLabel(
            "Scan this QR code with your Android or iPhone camera.<br>"
            "No app installation required!"
        )
        sub.setAlignment(Qt.AlignmentFlag.AlignCenter)
        sub.setWordWrap(True)
        sub.setStyleSheet("color: #8696a0; font-size: 13px;")
        layout.addWidget(sub)

        # Local IP determination
        local_ips = get_local_ip_addresses()
        primary_ip = local_ips[0] if local_ips else "127.0.0.1"
        self.url = f"http://{primary_ip}:{self.port}"

        # QR Code Display
        qr_img = qrcode.make(self.url)
        buf = io.BytesIO()
        qr_img.save(buf, format="PNG")
        qimage = QImage.fromData(buf.getvalue())
        pixmap = QPixmap.fromImage(qimage).scaled(
            220,
            220,
            Qt.AspectRatioMode.KeepAspectRatio,
            Qt.TransformationMode.SmoothTransformation,
        )

        lbl_qr = QLabel()
        lbl_qr.setAlignment(Qt.AlignmentFlag.AlignCenter)
        lbl_qr.setPixmap(pixmap)
        lbl_qr.setStyleSheet(
            "background-color: #ffffff; padding: 12px; border-radius: 12px;"
        )
        layout.addWidget(lbl_qr, alignment=Qt.AlignmentFlag.AlignCenter)

        # URL Box
        url_box = QHBoxLayout()
        lbl_url = QLabel(f"<b>URL:</b> <a href='{self.url}' style='color:#00a884;'>{self.url}</a>")
        lbl_url.setTextInteractionFlags(Qt.TextInteractionFlag.TextSelectableByMouse)
        lbl_url.setStyleSheet("font-size: 13px; color: #e9edef;")
        btn_copy = QPushButton("Copy Link")
        btn_copy.clicked.connect(self._copy_link)
        url_box.addWidget(lbl_url)
        url_box.addStretch()
        url_box.addWidget(btn_copy)
        layout.addLayout(url_box)

        # Note
        note = QLabel(
            "💡 <i>Tip: Ensure your phone is connected to the same home Wi-Fi (Huawei or Tenda).</i>"
        )
        note.setAlignment(Qt.AlignmentFlag.AlignCenter)
        note.setStyleSheet("color: #8696a0; font-size: 11px;")
        layout.addWidget(note)

        layout.addStretch()

        btn_close = QPushButton("Done")
        btn_close.setObjectName("primaryAction")
        btn_close.clicked.connect(self.accept)
        layout.addWidget(btn_close)

    def _copy_link(self):
        clipboard = QApplication.clipboard()
        clipboard.setText(self.url)
        QMessageBox.information(
            self, "Copied", f"Link copied to clipboard:\n{self.url}"
        )

