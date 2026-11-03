"""Modern WhatsApp Desktop, Telegram & Dribbble 4-Column Messenger Stylesheet.
Palette: Midnight Violet (#1E1338 / #221643) + Soft Lilac (#E0DAFD / #DDD7FB) + Clean White (#FFFFFF / #F5F6FA) + Royal Purple Accent (#7C5CFC).
"""

DARK_THEME_QSS = """
/* ===================================================================
   GLOBAL APPLICATION RESETS & BASE STYLING
   =================================================================== */
QWidget {
    font-family: "Segoe UI", -apple-system, BlinkMacSystemFont, "SF Pro Text", Roboto, "Helvetica Neue", sans-serif;
    font-size: 13px;
    border: none;
    outline: none;
}

QMainWindow {
    background-color: #1E1338;
}

/* ===================================================================
   COLUMN 1: DEEP MIDNIGHT VIOLET NAVIGATION RAIL (68px)
   =================================================================== */
#navRail {
    background-color: #1E1338;
    border-right: 1px solid rgba(255, 255, 255, 0.06);
    min-width: 68px;
    max-width: 68px;
}

QPushButton.navRailBtn {
    background-color: transparent;
    color: #8E7FA8;
    font-size: 18px;
    border-radius: 14px;
    min-width: 48px;
    max-width: 48px;
    min-height: 48px;
    max-height: 48px;
    padding: 0px;
    margin: 3px 10px;
    border: none;
}

QPushButton.navRailBtn:hover {
    background-color: #2D1D54;
    color: #FFFFFF;
}

QPushButton.navRailBtnActive {
    background-color: #7C5CFC;
    color: #FFFFFF;
    border-radius: 14px;
    box-shadow: 0 4px 12px rgba(124, 92, 252, 0.4);
}

QPushButton.navRailUserAvatar {
    background: qlineargradient(x1:0, y1:0, x2:1, y2:1, stop:0 #7C5CFC, stop:1 #5136B7);
    color: #FFFFFF;
    font-size: 24px;
    border-radius: 24px;
    min-width: 48px;
    max-width: 48px;
    min-height: 48px;
    max-height: 48px;
    margin: 12px 10px 10px 10px;
    border: 2px solid rgba(255, 255, 255, 0.15);
}

/* ===================================================================
   COLUMN 2: CLEAN WHITE CHATS SIDEBAR (300px)
   =================================================================== */
#sidebar {
    background-color: #FFFFFF;
    border-right: 1px solid #E8EAF2;
}

#sidebarHeader {
    background-color: #FFFFFF;
    padding: 16px 16px 8px 16px;
}

#sidebarTitle {
    font-size: 22px;
    font-weight: 800;
    color: #1E1338;
    letter-spacing: -0.4px;
}

/* Rounded Pill Search Bar */
#searchContainer {
    background-color: #FFFFFF;
    padding: 6px 14px 10px 14px;
}

QLineEdit#searchBox {
    background-color: #F4F5FB;
    color: #1E1338;
    border: 1px solid #E8EAF2;
    border-radius: 12px;
    padding: 9px 14px 9px 34px;
    font-size: 13px;
}

QLineEdit#searchBox:focus {
    background-color: #FFFFFF;
    border: 1px solid #7C5CFC;
}

QLineEdit#searchBox::placeholder {
    color: #9494B8;
}

/* Filter Tag Chips (Todos, No leídos, Grupos) */
#filterBar {
    background-color: #FFFFFF;
    padding: 0px 14px 10px 14px;
}

QPushButton.filterChip {
    background-color: #F4F5FB;
    color: #6C5FA7;
    font-size: 11px;
    font-weight: 700;
    border-radius: 12px;
    padding: 5px 12px;
    border: none;
    margin-right: 4px;
}

QPushButton.filterChip:hover {
    background-color: #ECE8FE;
    color: #7C5CFC;
}

QPushButton.filterChipActive {
    background-color: #7C5CFC;
    color: #FFFFFF;
    font-weight: 800;
}

/* Peer List View */
QListWidget#peerList {
    background-color: #FFFFFF;
    border: none;
    outline: none;
    padding: 4px 6px;
}

QListWidget#peerList::item {
    background-color: transparent;
    border-radius: 14px;
    margin: 2px 2px;
    padding: 0px;
    border: none;
}

QListWidget#peerList::item:hover {
    background-color: #F7F7FD;
}

QListWidget#peerList::item:selected {
    background-color: #ECE8FE;
}

/* Floating Action Button (Nuevo Chat / IP Connect) */
QPushButton#btnNewChat {
    background: qlineargradient(x1:0, y1:0, x2:1, y2:1, stop:0 #7C5CFC, stop:1 #5B3AE0);
    color: #FFFFFF;
    font-size: 12px;
    font-weight: 700;
    border-radius: 16px;
    padding: 8px 16px;
    border: none;
    margin: 8px 14px 12px 14px;
}

QPushButton#btnNewChat:hover {
    background: qlineargradient(x1:0, y1:0, x2:1, y2:1, stop:0 #8E74FD, stop:1 #6B49F0);
}

/* ===================================================================
   COLUMN 3: MAIN CHAT CANVAS (#F5F6FA)
   =================================================================== */
#chatContainer {
    background-color: #F5F6FA;
}

#chatHeader {
    background-color: #FFFFFF;
    padding: 10px 20px;
    border-bottom: 1px solid #E8EAF2;
    min-height: 54px;
    max-height: 54px;
}

#chatScrollArea {
    background-color: #F5F6FA;
    border: none;
}

#chatContent {
    background-color: #F5F6FA;
}

QPushButton.chatHeaderBtn {
    background-color: #F4F5FB;
    color: #584B7A;
    border: none;
    border-radius: 18px;
    min-width: 36px;
    max-width: 36px;
    min-height: 36px;
    max-height: 36px;
    font-size: 15px;
    padding: 0px;
}

QPushButton.chatHeaderBtn:hover {
    background-color: #ECE8FE;
    color: #7C5CFC;
}

/* Floating Bottom Input Bar (WhatsApp / Reference Style Pill) */
#inputContainer {
    background-color: transparent;
    padding: 8px 18px 14px 18px;
}

#floatingInputPill {
    background-color: #FFFFFF;
    border-radius: 20px;
    border: 1px solid #E8EAF2;
    padding: 4px 8px;
    box-shadow: 0 4px 16px rgba(30, 19, 56, 0.06);
}

#messageInput {
    background-color: transparent;
    color: #1E1338;
    border: none;
    padding: 8px 10px;
    font-size: 14px;
}

#messageInput::placeholder {
    color: #9494B8;
}

QPushButton#btnSend {
    background: qlineargradient(x1:0, y1:0, x2:1, y2:1, stop:0 #7C5CFC, stop:1 #5B3AE0);
    color: #FFFFFF;
    font-size: 15px;
    font-weight: bold;
    border-radius: 18px;
    min-width: 36px;
    max-width: 36px;
    min-height: 36px;
    max-height: 36px;
    padding: 0px;
    border: none;
}

QPushButton#btnSend:hover {
    background: qlineargradient(x1:0, y1:0, x2:1, y2:1, stop:0 #8E74FD, stop:1 #6B49F0);
}

QPushButton.inputActionBtn {
    background-color: transparent;
    color: #7D7398;
    border: none;
    border-radius: 16px;
    min-width: 32px;
    max-width: 32px;
    min-height: 32px;
    max-height: 32px;
    font-size: 17px;
    padding: 0px;
}

QPushButton.inputActionBtn:hover {
    background-color: #F4F5FB;
    color: #7C5CFC;
}

/* ===================================================================
   COLUMN 4: RIGHT PEER DETAILS PANEL (#1E1338 / #221643)
   =================================================================== */
#rightInfoPanel {
    background-color: #1E1338;
    border-left: 1px solid rgba(255, 255, 255, 0.08);
    min-width: 310px;
    max-width: 330px;
}

#infoPanelHeader {
    background-color: #1E1338;
    padding: 16px 18px 12px 18px;
}

#infoPanelTitle {
    font-size: 16px;
    font-weight: 700;
    color: #FFFFFF;
}

QPushButton#btnCloseInfo {
    background-color: rgba(255, 255, 255, 0.06);
    color: #A599C8;
    font-size: 14px;
    border-radius: 14px;
    min-width: 28px;
    max-width: 28px;
    min-height: 28px;
    max-height: 28px;
    border: none;
}

QPushButton#btnCloseInfo:hover {
    background-color: rgba(255, 255, 255, 0.15);
    color: #FFFFFF;
}

/* Details Panel Action Chips */
QPushButton.infoActionChip {
    background-color: rgba(255, 255, 255, 0.08);
    color: #FFFFFF;
    font-size: 16px;
    border-radius: 16px;
    min-width: 44px;
    max-width: 44px;
    min-height: 44px;
    max-height: 44px;
    border: 1px solid rgba(255, 255, 255, 0.06);
}

QPushButton.infoActionChip:hover {
    background-color: #7C5CFC;
    border-color: #7C5CFC;
}

/* Details Section Cards (Photos, Docs, Links) */
.infoSectionCard {
    background-color: #271A4A;
    border-radius: 14px;
    padding: 12px 14px;
    margin: 4px 14px;
    border: 1px solid rgba(255, 255, 255, 0.04);
}

.infoSectionCard:hover {
    background-color: #2E1F57;
}

.infoSectionHeader {
    color: #E0DAFD;
    font-size: 13px;
    font-weight: 700;
}

.infoSectionLink {
    color: #7C5CFC;
    font-size: 11px;
    font-weight: 700;
}

/* ===================================================================
   GENERIC FORM CONTROLS & POPUPS
   =================================================================== */
QLineEdit {
    background-color: #271A4A;
    color: #FFFFFF;
    border: 1px solid #3D2C6F;
    border-radius: 10px;
    padding: 8px 12px;
    font-size: 13px;
}

QLineEdit:focus {
    border: 1px solid #7C5CFC;
}

QPushButton {
    background-color: #271A4A;
    color: #FFFFFF;
    border: 1px solid #3D2C6F;
    border-radius: 10px;
    padding: 8px 16px;
    font-size: 13px;
    font-weight: 600;
}

QPushButton:hover {
    background-color: #382669;
    border-color: #7C5CFC;
}

QPushButton#primaryAction {
    background: qlineargradient(x1:0, y1:0, x2:1, y2:1, stop:0 #7C5CFC, stop:1 #5B3AE0);
    color: #FFFFFF;
    font-weight: 700;
    font-size: 13px;
    border: none;
    padding: 10px 18px;
    border-radius: 10px;
}

QPushButton#primaryAction:hover {
    background: qlineargradient(x1:0, y1:0, x2:1, y2:1, stop:0 #8E74FD, stop:1 #6B49F0);
}

/* Progress Bars */
QProgressBar {
    background-color: rgba(0, 0, 0, 0.08);
    border: none;
    border-radius: 5px;
    text-align: center;
    color: #1E1338;
    font-size: 10px;
    font-weight: 700;
    height: 10px;
}

QProgressBar::chunk {
    background: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #7C5CFC, stop:1 #9F8BFD);
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
    background-color: rgba(124, 92, 252, 0.25);
    min-height: 25px;
    border-radius: 3px;
}

QScrollBar::handle:vertical:hover {
    background-color: #7C5CFC;
}

QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {
    height: 0px;
}

QScrollBar:horizontal {
    height: 0px;
}

/* Modern Status Bar */
QStatusBar {
    background-color: #1E1338;
    color: #9F8BFD;
    border-top: 1px solid rgba(255, 255, 255, 0.06);
    font-size: 11px;
    padding: 2px 12px;
}

/* Dialogs */
QDialog {
    background-color: #1E1338;
    color: #FFFFFF;
}
"""
