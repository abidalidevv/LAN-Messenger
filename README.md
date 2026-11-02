# 💬 LAN Messenger (Local Home Network & Remote WhatsApp / Telegram Alternative)

> **No Phone Number • No Accounts • Zero Cloud Dependency • 100% Local LAN Speed & HD Quality**

[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)
[![Platform](https://img.shields.io/badge/Platform-Windows%2010%20%7C%2011-0078D6.svg)](https://microsoft.com)
[![Python](https://img.shields.io/badge/Python-3.10%2B-brightgreen.svg)](https://python.org)
[![PyQt6](https://img.shields.io/badge/UI-PyQt6-darkgreen.svg)](https://riverbankcomputing.com)
[![Speed](https://img.shields.io/badge/Speed-215%2B%20MB%2Fs-orange.svg)](#-benchmark--stress-test-results)

---

## 🌟 Key Features

1. **Pure Speed & Zero Quality Loss (Up to 215+ MB/s):**
   - Files, 4K HD videos, RAW photos, zip archives, audio, and documents transfer in **original bit-for-bit quality** without any compression.
   - High-performance 4 MB sequential disk I/O write buffering prevents disk thrashing on HDDs and SSDs.
2. **Dual-Router & Multi-Subnet Architecture:**
   - Specially architected for multi-router home & office networks: **Huawei (`192.168.100.x`) + Tenda (`192.168.7.x`) + Ethernet Hub / Wi-Fi**.
   - Dual directed UDP broadcast auto-discovers peers across subnets.
   - Built-in multi-threaded fast subnet sweeper checks 500 IPs in under 1.5 seconds.
3. **📞 LAN Voice Calling & 🖥️ 15 FPS Screen Sharing:**
   - Real-time low-latency voice calling using 16kHz PCM audio (`QAudioSource` / `QAudioSink`).
   - Live desktop screen sharing with adaptive frame skipping for smooth viewing even on congested 2.4 GHz Wi-Fi.
4. **📱 Mobile Web QR Code Portal (Zero Phone App Needed):**
   - Click the **📱 Mobile QR** button to generate a QR code.
   - Scan with your iPhone or Android camera to open a lightweight web app in Safari/Chrome.
   - Send and receive messages and upload photos/files from mobile directly to your PC with zero phone installations!
5. **🌐 Remote Friends & Playit.gg / Tailscale Support:**
   - Connect to friends outside your home over the Internet.
   - Built-in Playit.gg manager and Tailscale setup guides for seamless NAT hole-punching without requiring static public IPs.
6. **WhatsApp / Telegram Modern Dark UI:**
   - Sleek Emerald & Slate dark theme.
   - Drag-and-drop files directly from Windows Explorer into chat bubbles.
   - In-chat image thumbnails and previews.
   - 20 prebuilt stylish avatars (Gamer, Developer, Hacker, Rocket, Lion, Ninja, etc.).
   - Broadcast channel to message all online peers simultaneously.
   - Clipboard synchronization (send clipboard text or screenshots in one click).
7. **Windows Setup Installer + Portable EXE:**
   - `LANMessenger_Setup.exe`: User-friendly installer wizard with desktop & start-menu shortcuts and automatic Windows Defender Firewall rules.
   - `LANMessenger.exe`: 100% portable standalone executable.

---

## 🚀 How to Run on Any PC / Laptop (Urdu & English Guide)

### Urdu:
1. **Har PC ya Laptop pr copy karein:**
   - `LANMessenger_Setup.exe` ko double-click kr k install karein, ya `LANMessenger.exe` portable ko chalayein.
2. **Pehli martaba Setup:**
   - Apna naam aur 20 avatars mein se koi pasandeeda avatar select karein.
   - Windows Defender Firewall ka popup aye tu **"Private Networks"** tick kr k **"Allow Access"** dabayein (ya installer khud configure kr dega).
3. **Auto Connect & LAN Scan:**
   - Sabhi PCs jo same Wi-Fi / Router se connected hain foran left list mein green dot `🟢` k sath nazar ayen gy.
   - Agar doosra router ho tu **"⚡ Scan LAN"** dabayein.
4. **Internet se doston ko add krna:**
   - Agar dost kisi doosray shehar ya internet pr hai, tu **Playit.gg** ya **Tailscale** ka link paste kr k foran connect karein.

---

## 🛠️ Project Structure

```
Tool/
├── LANMessenger.py          # Main entry point (single-instance lock & taskbar ID)
├── LANMessenger.exe         # Standalone compiled portable executable
├── LANMessenger_Setup.exe   # Complete Windows setup installer wizard
├── installer.py             # PyQt6 custom setup installer wizard source
├── installer.iss            # Inno Setup compilation script
├── build_exe.py             # Automated PyInstaller build script for portable app
├── build_installer.py       # Automated build script for installer executable
├── Allow_Firewall.bat       # 1-Click Windows Defender firewall configuration
├── Create_Desktop_Shortcut.bat # 1-Click desktop shortcut creator
├── app/
│   ├── config.py            # Settings, avatars, ports, and subnets persistence
│   ├── network/
│   │   ├── protocol.py      # Binary framing protocol with 8-byte header
│   │   ├── discovery.py     # Dual-subnet UDP broadcast & fast subnet sweeper
│   │   ├── transfer.py      # High-speed file engine with 4MB sequential write buffer
│   │   ├── connection.py    # Bidirectional full-duplex TCP socket handler
│   │   ├── engine.py        # Background asyncio worker thread bridging to PyQt6
│   │   ├── media_engine.py  # 16kHz PCM voice calling & 15 FPS screen sharing
│   │   ├── web_portal.py    # Mobile QR web portal (aiohttp HTTP server)
│   │   └── playit_manager.py# Playit.gg local agent management & tunnel status
│   ├── ui/
│   │   ├── styles.py        # WhatsApp/Telegram dark theme stylesheet
│   │   ├── main_window.py   # Main window layout & tab management
│   │   ├── peer_list.py     # Sidebar with avatars, online dots & Broadcast channel
│   │   ├── chat_panel.py    # Chat bubbles, image previews, speed meters & drag-and-drop
│   │   ├── call_dialog.py   # Voice call incoming / active dialog
│   │   ├── screen_viewer.py # Live screen share viewer dialog
│   │   ├── qr_dialog.py     # Mobile QR web portal dialog
│   │   ├── help_dialog.py   # Built-in tabbed user manual & FAQ
│   │   ├── playit_dialog.py # Playit.gg automated internet tunnel setup dialog
│   │   ├── setup_dialog.py  # Initial user profile & 20-avatar picker
│   │   ├── add_peer_dialog.py # Manual IP & remote internet peer connector
│   │   ├── network_dialog.py# Network diagnostics dialog
│   │   ├── tray.py          # Windows System Tray & toast notifications
│   │   └── sound.py         # Audio chime synthesizers
│   └── utils/
│       ├── avatars.py       # 20 prebuilt avatar definitions & badges
│       ├── paths.py         # Path locator for standalone EXEs & development
│       ├── file_helper.py   # SHA256 integrity checker, buffer I/O & naming
│       └── history.py       # Persistent chat & file history
├── assets/
│   ├── app_icon.png         # High-resolution application icon
│   └── app_icon.ico         # Multi-size Windows EXE icon
├── tests/
│   ├── test_protocol.py     # Binary framing & partial TCP read simulation
│   ├── test_transfer.py     # High-speed chunking & file integrity tests
│   ├── test_integration.py  # 2-peer end-to-end communication tests
│   ├── test_stress.py       # 50 MB transfer & 100 burst messages test
│   └── test_heavy_stress.py # 100 MB transfer & 500 burst messages stress test
└── run_tests.py             # Test suite runner
```

---

## 🧪 Benchmark & Stress Test Results

| Metric | Result | Status |
| :--- | :--- | :--- |
| **Max Transfer Throughput** | **215.47 MB/s** | ✅ Passed |
| **Message Burst Rate** | **978.2 messages / sec** (500 burst) | ✅ 0 Dropped |
| **File Integrity** | **100% SHA256 Hash Match** | ✅ Zero Corruption |
| **Idle Memory Consumption**| **~32 MB RAM** | ✅ Ultra-Light |
| **Subnet Discovery** | **< 1.5 seconds for 500 IPs** | ✅ Instant |

---

## 🌐 Connecting Friends Across the Internet (Free Playit.gg Guide)

1. Open **"🌐 Internet Link"** in LAN Messenger or go to [Playit.gg](https://playit.gg/).
2. On the Playit.gg dashboard, click **Add Tunnel**.
3. Select **"Minecraft (Java Edition)"** (or any free TCP option).
   - *Note: Minecraft Java uses raw TCP transport. Playit forwards standard TCP packets without any restriction!*
4. Set **Local Port** to `9876`.
5. Click **Create Tunnel**. Playit will give you an address like `yourname.gl.joinmc.link:12345` or `xyz.ply.gg:12345`.
6. Share this link with your friend. In their LAN Messenger, they click **"➕ Connect IP"** and paste the link. You are now instantly connected across the Internet!

---

## 📄 License
MIT License. Free for personal, home, and commercial use.
