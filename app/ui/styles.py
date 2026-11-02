"""Modern WhatsApp Desktop & Telegram inspired Dark Theme stylesheet.
Crafted to Dribbble / Modern Desktop Messenger design standards.
"""

DARK_THEME_QSS = """
/* ===================================================================
   GLOBAL APPLICATION STYLING & TYPOGRAPHY
   =================================================================== */
QWidget {
    background-color: #111b21;
    color: #e9edef;
    font-family: "Segoe UI", -apple-system, BlinkMacSystemFont, "SF Pro Text", Roboto, "Helvetica Neue", sans-serif;
    font-size: 13px;
    border: none;
    outline: none;
}

QMainWindow {
    background-color: #0c1317;
}

/* ===================================================================
   NAVIGATION RAIL (FAR LEFT SLIM ICON BAR)
   =================================================================== */
#navRail {
    background-color: #111b21;
    border-right: 1px solid #202c33;
    min-width: 62px;
    max-width: 62px;
}

QPushButton.navBtn {
    background-color: transparent;
    color: #8696a0;
    font-size: 20px;
    border-radius: 12px;
    min-width: 44px;
    max-width: 44px;
    min-height: 44px;
    max-height: 44px;
    padding: 0px;
    margin: 4px 9px;
    border: none;
}

QPushButton.navBtn:hover {
    background-color: #202c33;
    color: #00a884;
}

QPushButton.navBtn:pressed {
    background-color: #2a3942;
}

QPushButton.navBtnActive {
    background-color: #202c33;
    color: #00a884;
    border-left: 3px solid #00a884;
    border-radius: 4px 12px 12px 4px;
}

QPushButton.navBtnBrand {
    background: qlineargradient(x1:0, y1:0, x2:1, y2:1, stop:0 #00a884, stop:1 #005c4b);
    color: #ffffff;
    font-size: 22px;
    border-radius: 14px;
    min-width: 46px;
    max-width: 46px;
    min-height: 46px;
    max-height: 46px;
    margin: 10px 8px 6px 8px;
}

/* ===================================================================
   SIDEBAR & CHAT LIST (MIDDLE COLUMN)
   =================================================================== */
#sidebar {
    background-color: #111b21;
    border-right: 1px solid #202c33;
}

#sidebarHeader {
    background-color: #111b21;
    padding: 12px 14px 10px 14px;
    border-bottom: 1px solid #202c33;
}

#sidebarTitle {
    font-size: 20px;
    font-weight: 700;
    color: #e9edef;
    letter-spacing: -0.3px;
}

#searchContainer {
    background-color: #111b21;
    padding: 8px 12px;
    border-bottom: 1px solid #1f2c34;
}

QLineEdit#searchBox {
    background-color: #202c33;
    color: #e9edef;
    border: 1px solid transparent;
    border-radius: 8px;
    padding: 8px 12px 8px 34px;
    font-size: 13px;
}

QLineEdit#searchBox:focus {
    background-color: #202c33;
    border: 1px solid #00a884;
}

QLineEdit#searchBox::placeholder {
    color: #8696a0;
}

/* Peer List View */
QListWidget#peerList {
    background-color: #111b21;
    border: none;
    outline: none;
    padding: 4px 0px;
}

QListWidget#peerList::item {
    background-color: transparent;
    border-radius: 10px;
    margin: 2px 8px;
    padding: 0px;
    border: none;
}

QListWidget#peerList::item:hover {
    background-color: #202c33;
}

QListWidget#peerList::item:selected {
    background-color: #2a3942;
}

/* ===================================================================
   MAIN SPLITTER & DIVIDERS
   =================================================================== */
QSplitter::handle {
    background-color: #202c33;
    width: 1px;
}

/* ===================================================================
   CHAT PANEL (RIGHT COLUMN)
   =================================================================== */
#chatContainer {
    background-color: #0b141a;
}

#chatHeader {
    background-color: #202c33;
    padding: 8px 16px;
    border-bottom: 1px solid #222d34;
    min-height: 52px;
    max-height: 52px;
}

#chatScrollArea {
    background-color: #0b141a;
    border: none;
}

#chatContent {
    background-color: #0b141a;
}

/* Header Buttons (Call, Screen, Info) */
QPushButton.chatHeaderBtn {
    background-color: transparent;
    color: #aebac1;
    border: none;
    border-radius: 20px;
    min-width: 40px;
    max-width: 40px;
    min-height: 40px;
    max-height: 40px;
    font-size: 16px;
    padding: 0px;
}

QPushButton.chatHeaderBtn:hover {
    background-color: #2a3942;
    color: #00a884;
}

QPushButton.chatHeaderBtn:pressed {
    background-color: #1f2c34;
}

/* ===================================================================
   CHAT INPUT FOOTER (WHATSAPP FLOATING PILL)
   =================================================================== */
#inputContainer {
    background-color: #202c33;
    padding: 8px 16px;
    border-top: 1px solid #222d34;
}

#messageInput {
    background-color: #2a3942;
    color: #e9edef;
    border: 1px solid #2a3942;
    border-radius: 10px;
    padding: 9px 14px;
    font-size: 14px;
    line-height: 1.4;
}

#messageInput:focus {
    border: 1px solid #00a884;
}

#messageInput::placeholder {
    color: #8696a0;
}

/* Circular Send Button */
QPushButton#btnSend {
    background: qlineargradient(x1:0, y1:0, x2:1, y2:1, stop:0 #00a884, stop:1 #008f6f);
    color: #111b21;
    font-size: 16px;
    font-weight: bold;
    border-radius: 20px;
    min-width: 40px;
    max-width: 40px;
    min-height: 40px;
    max-height: 40px;
    padding: 0px;
    border: none;
}

QPushButton#btnSend:hover {
    background: qlineargradient(x1:0, y1:0, x2:1, y2:1, stop:0 #06cf9c, stop:1 #00a884);
}

QPushButton#btnSend:pressed {
    background-color: #007a5e;
}

/* Attach & Clipboard Buttons */
QPushButton.inputActionBtn {
    background-color: transparent;
    color: #8696a0;
    border: none;
    border-radius: 18px;
    min-width: 36px;
    max-width: 36px;
    min-height: 36px;
    max-height: 36px;
    font-size: 18px;
    padding: 0px;
}

QPushButton.inputActionBtn:hover {
    background-color: #2a3942;
    color: #00a884;
}

/* ===================================================================
   GENERIC FORM CONTROLS & POPUPS
   =================================================================== */
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

QPushButton {
    background-color: #202c33;
    color: #e9edef;
    border: 1px solid #2a3942;
    border-radius: 8px;
    padding: 8px 16px;
    font-size: 13px;
    font-weight: 500;
}

QPushButton:hover {
    background-color: #2a3942;
    border-color: #00a884;
    color: #ffffff;
}

QPushButton:pressed {
    background-color: #1f2c34;
}

QPushButton#primaryAction {
    background: qlineargradient(x1:0, y1:0, x2:1, y2:1, stop:0 #00a884, stop:1 #008f6f);
    color: #111b21;
    font-weight: 700;
    font-size: 13px;
    border: none;
    padding: 9px 18px;
    border-radius: 8px;
}

QPushButton#primaryAction:hover {
    background: qlineargradient(x1:0, y1:0, x2:1, y2:1, stop:0 #06cf9c, stop:1 #00a884);
}

QPushButton#primaryAction:pressed {
    background-color: #007a5e;
}

/* Progress Bars */
QProgressBar {
    background-color: #182229;
    border: 1px solid #2a3942;
    border-radius: 6px;
    text-align: center;
    color: #e9edef;
    font-size: 11px;
    font-weight: 600;
    height: 14px;
}

QProgressBar::chunk {
    background: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #00a884, stop:1 #06cf9c);
    border-radius: 5px;
}

/* Ultra-Clean Modern Scrollbars */
QScrollBar:vertical {
    border: none;
    background-color: transparent;
    width: 6px;
    margin: 0px;
}

QScrollBar::handle:vertical {
    background-color: rgba(134, 150, 160, 0.25);
    min-height: 30px;
    border-radius: 3px;
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

/* Modern Status Bar */
QStatusBar {
    background-color: #111b21;
    color: #8696a0;
    border-top: 1px solid #202c33;
    font-size: 11px;
    padding: 2px 10px;
}

/* Dialogs */
QDialog {
    background-color: #111b21;
    color: #e9edef;
}
"""
