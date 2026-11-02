from PyQt6.QtWidgets import (
    QDialog,
    QVBoxLayout,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QTabWidget,
    QTextBrowser,
    QWidget,
)
from PyQt6.QtCore import Qt


class UserGuideDialog(QDialog):
    """Interactive, easy-to-understand User Guide and Documentation popup."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("📖 LAN Messenger — Complete User Guide (Aasan Tareeqa)")
        self.setFixedSize(700, 560)
        self.setWindowFlags(self.windowFlags() & ~Qt.WindowType.WindowContextHelpButtonHint)
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 18, 20, 18)
        layout.setSpacing(12)

        # Title
        title_row = QHBoxLayout()
        lbl_title = QLabel("📖 LAN Messenger — User Guide")
        lbl_title.setStyleSheet("font-size: 18px; font-weight: bold; color: #00a884;")
        title_row.addWidget(lbl_title)
        title_row.addStretch()
        layout.addLayout(title_row)

        sub = QLabel(
            "Ghar ke tamam PCs, Laptops aur Mobiles pr high-speed data share karne ka aasan tareeqa:"
        )
        sub.setStyleSheet("color: #8696a0; font-size: 13px;")
        layout.addWidget(sub)

        # Tabs for different features
        tabs = QTabWidget()
        tabs.setStyleSheet("""
            QTabWidget::pane { border: 1px solid #2a3942; background: #111b21; border-radius: 8px; }
            QTabBar::tab { background: #202c33; color: #8696a0; padding: 8px 16px; border-top-left-radius: 6px; border-top-right-radius: 6px; margin-right: 2px; }
            QTabBar::tab:selected { background: #00a884; color: #111b21; font-weight: bold; }
        """)

        # Tab 1: Quick Start
        t1 = self._create_browser("""
            <h3 style="color:#00a884;">🚀 1. Pehli Dafa Chalane Ka Tareeqa (Quick Start)</h3>
            <ol style="line-height:1.7;">
                <li><b>App Open Karein:</b> <code>LANMessenger.exe</code> pr double-click karein ya Setup install karein.</li>
                <li><b>Apna Naam & Avatar Chunein:</b> Pehli dafa apna display name (e.g. <i>Abid Laptop</i>) aur 20 avatars mein se pasandeeda avatar select karein.</li>
                <li><b>Windows Firewall:</b> Pehli dafa Windows ka popup aaye to <b>"Private Networks"</b> tick kar ke <b>"Allow access"</b> karein.</li>
                <li><b>Doosray PCs Auto Show Hon Ge:</b> Jese hi ghar ka doosra PC app chalaye ga, left side pr uska naam aur green dot 🟢 khud ba khud aa jaye ga.</li>
                <li><b>Chat Shuru Karein:</b> Kisi bhi device pr click karein aur WhatsApp ki tarah chat karein!</li>
            </ol>
        """)
        tabs.addTab(t1, "🚀 Pehla Step")

        # Tab 2: File Sharing & Drag-Drop
        t2 = self._create_browser("""
            <h3 style="color:#00a884;">📁 2. Heavy Files, 4K Videos & Photos Share Karna</h3>
            <ul style="line-height:1.7;">
                <li><b>🖱️ Mouse Se Drag & Drop:</b> Windows Explorer se koi bhi file, photo ya heavy 4K video mouse se utha kar direct chat screen pr chhor dein — foran send hona shuru ho jaye gi!</li>
                <li><b>📎 Attach Button:</b> Neeche 📎 button daba kar bhi koi bhi file pick kar sakte hain.</li>
                <li><b>⚡ Full Wire Speed (Zero Quality Loss):</b> Data compress nahi hota, 100% original HD quality mein wire limit (up to 170+ MB/s) pr deliver hota hai.</li>
                <li><b>🖼️ In-Chat Photo Preview:</b> Photos ka chhota thumbnail chat ke andar hi nazar aa jata hai.</li>
                <li><b>📂 Kahan Save Hoti Hain Files?</b> Sabhi received files aap ke <code>Downloads/LANMessenger</code> folder mein auto save hoti hain. Chat bubble mein mojood <b>"Open File"</b> ya <b>"Show in Folder"</b> dabayein.</li>
            </ul>
        """)
        tabs.addTab(t2, "📁 File Sharing")

        # Tab 3: Mobile Phone via QR Code
        t3 = self._create_browser("""
            <h3 style="color:#00a884;">📱 3. Mobile Phone Connect Karna (Bina App Install Kiye)</h3>
            <ol style="line-height:1.7;">
                <li><b>Mobile Wi-Fi:</b> Apna Android ya iPhone ghar ke usi Wi-Fi (Huawei ya Tenda) se connect karein.</li>
                <li><b>PC Pr Button Dabayein:</b> Toolbar mein <b>"📱 Connect Mobile"</b> button pr click karein. Screen pr QR Code show hoga.</li>
                <li><b>Phone Se Scan Karein:</b> Mobile ke camera ya Chrome browser se QR Code scan karein (ya browser mein <code>http://192.168.x.x:9878</code> likhein).</li>
                <li><b>Mobile Screen Khul Jaye Gi:</b> Mobile pr WhatsApp jaisi web screen khul jaye gi!</li>
                <li><b>Gallery Se Send Karein:</b> Mobile se photos, videos, PDFs direct PC pr send karein aur PC se files phone mein download karein!</li>
            </ol>
        """)
        tabs.addTab(t3, "📱 Mobile QR")

        # Tab 4: Voice Call & Screen Sharing
        t4 = self._create_browser("""
            <h3 style="color:#00a884;">📞 4. Free LAN Voice Call & 🖥️ Live Screen Share</h3>
            <ul style="line-height:1.7;">
                <li><b>📞 Free Voice Call:</b>
                    <ul>
                        <li>Chat ke upar <b>"📞 Call"</b> dabayein. Doosray PC pr ring bajay gi: [Accept 🟢] [Decline 🔴].</li>
                        <li>Accept hotay hi <b>Crystal HD Voice Call</b> shuru ho jaye gi. Zero balance, zero internet data cost!</li>
                        <li>Mic mute/unmute (🎙️) aur live call duration timer bhi sath chalta hai.</li>
                    </ul>
                </li>
                <li><b>🖥️ Live Screen Share:</b>
                    <ul>
                        <li>Chat ke upar <b>"🖥️ Screen"</b> button dabayein.</li>
                        <li>Doosray PC pr aik <b>Dedicated Live Viewer Window</b> khul jaye gi aur woh aap ki screen live (15-20 FPS) dekh sake ga.</li>
                        <li>Gaming, office presentation, ya PC troubleshooting ke liye behtareen hai!</li>
                    </ul>
                </li>
            </ul>
        """)
        tabs.addTab(t4, "📞 Call & Screen")

        # Tab 5: Broadcast & Clipboard
        t5 = self._create_browser("""
            <h3 style="color:#00a884;">📢 5. Group Broadcast & 📋 Instant Clipboard Sync</h3>
            <ul style="line-height:1.7;">
                <li><b>📢 All Devices (Broadcast):</b>
                    <ul>
                        <li>Left sidebar mein sab se upar permanent <b>"📢 All Devices (Broadcast)"</b> channel mojood hai.</li>
                        <li>Is mein koi bhi message ya file bhejne se poore ghar ke <b>tamam PCs aur mobiles ko aik sath</b> deliver ho jati hai!</li>
                    </ul>
                </li>
                <li><b>📋 Instant Clipboard Sync:</b>
                    <ul>
                        <li>Input bar mein <b>📋</b> button pr click karein.</li>
                        <li>Agar aap ne koi text copy kiya hua hai to 1 click mein send ho jaye ga.</li>
                        <li><b>Screenshot Feature:</b> Agar aap ne Windows Snipping Tool (<code>Win + Shift + S</code>) se koi screenshot copy kiya hai, to 📋 dabate hi woh direct image file ban kar foran send ho jaye ga!</li>
                    </ul>
                </li>
            </ul>
        """)
        tabs.addTab(t5, "📢 Group & Clipboard")

        # Tab 6: Remote Friend (Tailscale)
        t6 = self._create_browser("""
            <h3 style="color:#00a884;">🌍 6. Shehar / Ghar Se Bahar Dost Se Connect Hona (Tailscale / Playit)</h3>
            <ul style="line-height:1.7;">
                <li>Agar dost kisi doosray ghar ya doosray shehar mein baitha hai to dono <b>100% FREE</b> connect ho sakte hain:</li>
                <ol>
                    <li>Aap aur aap ka dost dono <b>Tailscale</b> (free app: <code>tailscale.com</code>) download karein aur Google se sign in karein.</li>
                    <li>Tailscale dono ko aik Virtual LAN IP (starts with <b>100.x.x.x</b>) de dega.</li>
                    <li>Hamare software mein <b>"➕ Connect IP"</b> dabayein aur dost ka <b>100.x.x.x</b> IP likhein.</li>
                    <li>Ya Playit.gg par Free Minecraft Java tunnel (Port 9876) bana kar link share karein!</li>
                </ol>
            </ul>
        """)
        tabs.addTab(t6, "🌍 Out of Home")

        # Tab 7: Developer & Remote Hub
        t7 = self._create_browser("""
            <h3 style="color:#53bdeb;">👨‍💻 7. Developer & Official Remote Hub</h3>
            <div style="background:#202c33; padding:12px; border-radius:8px; line-height:1.8;">
                <p><b>Developed by:</b> <span style="color:#00a884; font-size:15px; font-weight:bold;">Abid Developer</span></p>
                <p><b>GitHub Profile:</b> <a href="https://github.com/abidalidevv" style="color:#53bdeb;">https://github.com/abidalidevv</a></p>
                <p><b>Source Repository:</b> <a href="https://github.com/abidalidevv/LAN-Messenger" style="color:#53bdeb;">https://github.com/abidalidevv/LAN-Messenger</a></p>
                <hr style="border: 1px solid #2a3942; margin: 10px 0;">
                <p><b>🌐 Official Remote Server / Hub Link:</b></p>
                <p style="font-family: Consolas, monospace; background:#111b21; padding:8px 12px; border-radius:6px; color:#e9edef; font-size:14px;"><b>shrimp-cigars.tun.ply.gg</b></p>
                <p style="color:#8696a0; font-size:12px;">Is address ko 'Connect IP' mein daal kar Abid Developer ke sath direct connect ho sakte hain.</p>
            </div>
        """)
        tabs.addTab(t7, "👨‍💻 Developer")

        layout.addWidget(tabs, 1)

        # Close button
        btn_close = QPushButton("Samajh Aa Gaya (Got It)")
        btn_close.setObjectName("primaryAction")
        btn_close.clicked.connect(self.accept)
        layout.addWidget(btn_close)

    def _create_browser(self, html_content: str) -> QTextBrowser:
        browser = QTextBrowser()
        browser.setStyleSheet(
            "background-color: #111b21; border: none; padding: 10px; color: #e9edef; font-size: 13px;"
        )
        browser.setHtml(html_content)
        return browser

