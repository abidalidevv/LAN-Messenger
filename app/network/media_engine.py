import io
import time
from typing import Optional, Callable
from PyQt6.QtCore import QObject, pyqtSignal, QTimer, QIODevice, QByteArray
from PyQt6.QtGui import QPixmap, QImage
from PyQt6.QtWidgets import QApplication
from PyQt6.QtMultimedia import (
    QAudioFormat,
    QAudioSource,
    QAudioSink,
    QMediaDevices,
)


class AudioCallManager(QObject):
    """Manages real-time 16kHz PCM audio capture from microphone and playback to speakers."""

    sig_audio_frame_ready = pyqtSignal(bytes)  # audio PCM chunk ready to send

    def __init__(self, parent=None):
        super().__init__(parent)
        self.is_calling = False
        self.is_muted = False

        # Audio Format: 16,000 Hz, 1 Channel (Mono), 16-bit PCM
        self.audio_format = QAudioFormat()
        self.audio_format.setSampleRate(16000)
        self.audio_format.setChannelCount(1)
        self.audio_format.setSampleFormat(QAudioFormat.SampleFormat.Int16)

        self.audio_source: Optional[QAudioSource] = None
        self.audio_sink: Optional[QAudioSink] = None
        self.input_device_io: Optional[QIODevice] = None
        self.output_device_io: Optional[QIODevice] = None

    def start_call(self):
        """Starts microphone capture and speaker playback."""
        if self.is_calling:
            return
        self.is_calling = True

        # Input (Microphone)
        input_dev = QMediaDevices.defaultAudioInput()
        if not input_dev.isFormatSupported(self.audio_format):
            self.audio_format = input_dev.preferredFormat()

        self.audio_source = QAudioSource(input_dev, self.audio_format, self)
        self.input_device_io = self.audio_source.start()
        if self.input_device_io:
            self.input_device_io.readyRead.connect(self._on_mic_ready_read)

        # Output (Speakers)
        output_dev = QMediaDevices.defaultAudioOutput()
        self.audio_sink = QAudioSink(output_dev, self.audio_format, self)
        self.output_device_io = self.audio_sink.start()

    def _on_mic_ready_read(self):
        if not self.is_calling or not self.input_device_io:
            return
        data = self.input_device_io.readAll()
        if data and not self.is_muted:
            self.sig_audio_frame_ready.emit(data.data())

    def play_audio_chunk(self, pcm_bytes: bytes):
        """Streams incoming remote audio chunk to local speakers."""
        if self.is_calling and self.output_device_io:
            self.output_device_io.write(pcm_bytes)

    def set_muted(self, muted: bool):
        self.is_muted = muted

    def stop_call(self):
        self.is_calling = False
        if self.audio_source:
            self.audio_source.stop()
            self.audio_source = None
        if self.audio_sink:
            self.audio_sink.stop()
            self.audio_sink = None
        self.input_device_io = None
        self.output_device_io = None


class ScreenShareManager(QObject):
    """Captures desktop screen frames at 15 FPS with adaptive frame skipping to prevent network lag."""

    sig_screen_frame_ready = pyqtSignal(bytes)  # JPEG buffer

    def __init__(self, fps: int = 15, parent=None):
        super().__init__(parent)
        self.fps = fps
        self.is_sharing = False
        self.is_transmitting = False  # Flow control flag

        self.timer = QTimer(self)
        self.timer.setInterval(int(1000 / fps))
        self.timer.timeout.connect(self._capture_frame)

    def start_sharing(self):
        if self.is_sharing:
            return
        self.is_sharing = True
        self.is_transmitting = False
        self.timer.start()

    def stop_sharing(self):
        self.is_sharing = False
        self.timer.stop()

    def frame_sent(self):
        """Called when socket drain is finished to allow next frame."""
        self.is_transmitting = False

    def _capture_frame(self):
        if not self.is_sharing or self.is_transmitting:
            # Skip frame if previous frame is still draining (Prevents Wi-Fi bufferbloat)
            return
        screen = QApplication.primaryScreen()
        if not screen:
            return

        pixmap = screen.grabWindow(0)
        if pixmap.isNull():
            return

        # Adaptive resolution: Scale to max 1280 width with smooth scaling
        if pixmap.width() > 1280:
            pixmap = pixmap.scaledToWidth(
                1280, Qt.TransformationMode.FastTransformation
            )

        # Compress to JPEG
        byte_arr = QByteArray()
        qimg = pixmap.toImage()
        qimg.save(byte_arr, "JPG", quality=60)
        self.is_transmitting = True
        self.sig_screen_frame_ready.emit(byte_arr.data())

