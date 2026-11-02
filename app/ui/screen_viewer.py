from PyQt6.QtWidgets import (
    QMainWindow,
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QFrame,
)
from PyQt6.QtGui import QPixmap, QImage
from PyQt6.QtCore import Qt, pyqtSignal


class ScreenShareViewer(QMainWindow):
    """Live desktop screen share viewer window."""

    sig_viewer_closed = pyqtSignal()

    def __init__(self, sharer_name: str, parent=None):
        super().__init__(parent)
        self.sharer_name = sharer_name
        self.setWindowTitle(f"🖥️ Live Screen: {sharer_name} — LAN Messenger")
        self.resize(1000, 650)

        central = QWidget()
        self.setCentralWidget(central)
        layout = QVBoxLayout(central)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        # Header bar
        header = QFrame()
        header.setStyleSheet("background-color: #202c33; padding: 6px 14px;")
        h_layout = QHBoxLayout(header)
        h_layout.setContentsMargins(0, 0, 0, 0)

        lbl_info = QLabel(
            f"🖥️ <b>{sharer_name}</b> is sharing their screen in real time"
        )
        lbl_info.setStyleSheet("color: #e9edef; font-size: 13px;")
        h_layout.addWidget(lbl_info)
        h_layout.addStretch()

        self.btn_fs = QPushButton("⛶ Fullscreen")
        self.btn_fs.clicked.connect(self._toggle_fullscreen)
        h_layout.addWidget(self.btn_fs)

        btn_close = QPushButton("Close")
        btn_close.clicked.connect(self.close)
        h_layout.addWidget(btn_close)

        layout.addWidget(header)

        # Screen Display Area
        self.lbl_screen = QLabel("Waiting for first video frame...")
        self.lbl_screen.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.lbl_screen.setStyleSheet("background-color: #0b141a; color: #8696a0;")
        layout.addWidget(self.lbl_screen, 1)

    def update_frame(self, jpeg_bytes: bytes):
        """Renders received JPEG screen frame."""
        image = QImage.fromData(jpeg_bytes, "JPG")
        if not image.isNull():
            pix = QPixmap.fromImage(image)
            scaled = pix.scaled(
                self.lbl_screen.size(),
                Qt.AspectRatioMode.KeepAspectRatio,
                Qt.TransformationMode.FastTransformation,
            )
            self.lbl_screen.setPixmap(scaled)

    def _toggle_fullscreen(self):
        if self.isFullScreen():
            self.showNormal()
            self.btn_fs.setText("⛶ Fullscreen")
        else:
            self.showFullScreen()
            self.btn_fs.setText("Exit Fullscreen")

    def closeEvent(self, event):
        self.sig_viewer_closed.emit()
        event.accept()

