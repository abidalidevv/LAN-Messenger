"""Modern WhatsApp/Telegram inspired Dark Theme stylesheet."""

DARK_THEME_QSS = """
/* Global Window & Font */
QWidget {
    background-color: #111b21;
    color: #e9edef;
    font-family: "Segoe UI", -apple-system, BlinkMacSystemFont, Roboto, sans-serif;
    font-size: 14px;
    border: none;
}

/* Main Splitter */
QSplitter::handle {
    background-color: #222d34;
    width: 1px;
}

/* Sidebar Container */
#sidebar {
    background-color: #111b21;
    border-right: 1px solid #222d34;
}

/* Sidebar Header & Search */
#sidebarHeader {
    background-color: #202c33;
    padding: 12px;
    border-bottom: 1px solid #222d34;
}

QLineEdit {
    background-color: #202c33;
    color: #e9edef;
    border: 1px solid #2a3942;
    border-radius: 8px;
    padding: 8px 12px;
    font-size: 13px;
}

QLineEdit:focus {
    border: 1px solid #00a884;
}

/* Peer List View */
QListWidget {
    background-color: #111b21;
    border: none;
    outline: none;
}

QListWidget::item {
    background-color: transparent;
    padding: 10px 14px;
    border-bottom: 1px solid #1f2c34;
    border-radius: 8px;
    margin: 2px 6px;
}

QListWidget::item:hover {
    background-color: #202c33;
}

QListWidget::item:selected {
    background-color: #2a3942;
}

/* Chat Panel Area */
#chatContainer {
    background-color: #0b141a;
}

#chatHeader {
    background-color: #202c33;
    padding: 10px 16px;
    border-bottom: 1px solid #222d34;
}

#chatScrollArea {
    background-color: #0b141a;
    border: none;
}

#chatContent {
    background-color: #0b141a;
}

/* Input Area */
#inputContainer {
    background-color: #202c33;
    padding: 10px 16px;
    border-top: 1px solid #222d34;
}

#messageInput {
    background-color: #2a3942;
    color: #e9edef;
    border: 1px solid #2a3942;
    border-radius: 12px;
    padding: 10px 14px;
    font-size: 14px;
}

#messageInput:focus {
    border: 1px solid #00a884;
}

/* Action Buttons */
QPushButton {
    background-color: #202c33;
    color: #e9edef;
    border: 1px solid #2a3942;
    border-radius: 8px;
    padding: 8px 14px;
    font-weight: 500;
}

QPushButton:hover {
    background-color: #2a3942;
    border-color: #00a884;
}

QPushButton:pressed {
    background-color: #1f2c34;
}

QPushButton#btnSend {
    background-color: #00a884;
    color: #111b21;
    font-weight: bold;
    border-radius: 20px;
    min-width: 40px;
    min-height: 40px;
    max-width: 40px;
    max-height: 40px;
    padding: 0px;
}

QPushButton#btnSend:hover {
    background-color: #06cf9c;
}

QPushButton#btnAttach {
    background-color: transparent;
    color: #8696a0;
    border: none;
    font-size: 18px;
    min-width: 38px;
    min-height: 38px;
}

QPushButton#btnAttach:hover {
    color: #00a884;
    background-color: #2a3942;
    border-radius: 19px;
}

QPushButton#primaryAction {
    background-color: #00a884;
    color: #111b21;
    font-weight: bold;
    border: none;
    padding: 10px 18px;
    border-radius: 8px;
}

QPushButton#primaryAction:hover {
    background-color: #06cf9c;
}

/* Progress Bars */
QProgressBar {
    background-color: #182229;
    border: 1px solid #2a3942;
    border-radius: 6px;
    text-align: center;
    color: #e9edef;
    font-size: 12px;
    height: 16px;
}

QProgressBar::chunk {
    background-color: #00a884;
    border-radius: 5px;
}

/* Scrollbars */
QScrollBar:vertical {
    border: none;
    background-color: #111b21;
    width: 8px;
    margin: 0px;
}

QScrollBar::handle:vertical {
    background-color: #374248;
    min-height: 25px;
    border-radius: 4px;
}

QScrollBar::handle:vertical:hover {
    background-color: #00a884;
}

QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {
    height: 0px;
}

QScrollBar:horizontal {
    height: 0px;
}

/* Status Bar */
QStatusBar {
    background-color: #202c33;
    color: #8696a0;
    border-top: 1px solid #222d34;
    font-size: 12px;
    padding: 4px 8px;
}

/* Dialogs */
QDialog {
    background-color: #111b21;
    color: #e9edef;
}
"""

