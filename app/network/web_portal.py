import os
import io
import time
import json
from pathlib import Path
from typing import Dict, Any, Optional, Set
import asyncio
from aiohttp import web, WSMsgType
import qrcode

from ..config import config
from ..utils.file_helper import get_unique_filepath, format_size
from ..utils.paths import get_asset_path

# HTML for Mobile Web App (Responsive WhatsApp Dark Theme)
MOBILE_HTML = """<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=no">
    <title>LAN Messenger Mobile</title>
    <style>
        * { box-sizing: border-box; margin: 0; padding: 0; font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif; }
        body { background-color: #0b141a; color: #e9edef; display: flex; flex-direction: column; height: 100vh; height: 100dvh; }
        
        /* Header */
        header { background-color: #202c33; padding: 12px 16px; display: flex; align-items: center; justify-content: space-between; border-bottom: 1px solid #222d34; }
        .peer-info { display: flex; align-items: center; gap: 10px; }
        .avatar { width: 40px; height: 40px; border-radius: 50%; background: #00a884; display: flex; align-items: center; justify-content: center; font-weight: bold; font-size: 18px; color: #fff; }
        .peer-name { font-weight: 600; font-size: 16px; }
        .peer-status { font-size: 12px; color: #8696a0; }
        
        /* Chat Box */
        #chat { flex: 1; overflow-y: auto; padding: 14px; display: flex; flex-direction: column; gap: 8px; }
        .msg { max-width: 82%; padding: 8px 12px; border-radius: 10px; font-size: 14px; line-height: 1.4; word-break: break-word; }
        .msg.out { align-self: flex-end; background-color: #005c4b; color: #e9edef; }
        .msg.in { align-self: flex-start; background-color: #202c33; color: #e9edef; }
        .time { font-size: 10px; color: #8696a0; text-align: right; margin-top: 4px; }
        
        .file-card { display: flex; align-items: center; gap: 10px; background: rgba(0,0,0,0.2); padding: 8px; border-radius: 8px; margin-top: 4px; }
        .file-icon { font-size: 24px; }
        .file-name { font-weight: 600; font-size: 13px; }
        .file-size { font-size: 11px; color: #8696a0; }
        .btn-dl { background: #00a884; color: #111b21; border: none; padding: 6px 12px; border-radius: 6px; font-weight: bold; font-size: 12px; text-decoration: none; margin-left: auto; }

        /* Upload Progress Banner */
        #uploadBanner { display: none; background: #202c33; padding: 10px 16px; border-top: 1px solid #222d34; font-size: 13px; }
        .prog-bar { height: 6px; background: #182229; border-radius: 3px; overflow: hidden; margin-top: 6px; }
        .prog-fill { height: 100%; width: 0%; background: #00a884; transition: width 0.1s; }

        /* Bottom Input */
        footer { background-color: #202c33; padding: 8px 12px; display: flex; align-items: center; gap: 8px; border-top: 1px solid #222d34; }
        .btn-attach { background: none; border: none; font-size: 24px; color: #8696a0; padding: 6px; cursor: pointer; }
        #textInput { flex: 1; background: #2a3942; border: none; outline: none; color: #e9edef; padding: 10px 14px; border-radius: 20px; font-size: 15px; }
        .btn-send { background: #00a884; border: none; width: 40px; height: 40px; border-radius: 50%; color: #111b21; font-weight: bold; font-size: 16px; display: flex; align-items: center; justify-content: center; cursor: pointer; }
        
        /* Modal for Name */
        #nameModal { position: fixed; inset: 0; background: rgba(0,0,0,0.85); display: flex; align-items: center; justify-content: center; padding: 20px; z-index: 100; }
        .modal-box { background: #202c33; padding: 24px; border-radius: 12px; width: 100%; max-width: 360px; text-align: center; }
        .modal-box h3 { color: #00a884; margin-bottom: 8px; }
        .modal-box p { font-size: 13px; color: #8696a0; margin-bottom: 16px; }
        .modal-box input { width: 100%; padding: 10px 12px; background: #111b21; border: 1px solid #2a3942; border-radius: 8px; color: #fff; margin-bottom: 16px; font-size: 14px; }
        .modal-box button { width: 100%; padding: 10px; background: #00a884; color: #111b21; border: none; border-radius: 8px; font-weight: bold; font-size: 15px; }
    </style>
</head>
<body>

    <div id="nameModal">
        <div class="modal-box">
            <h3>📱 Connect Mobile</h3>
            <p>Enter your name or phone model so the PC recognizes you:</p>
            <input type="text" id="phoneName" placeholder="e.g. Abid Phone, Galaxy S23">
            <button onclick="startSession()">Join Chat</button>
        </div>
    </div>

    <header>
        <div class="peer-info">
            <div class="avatar" id="hostAvatar">🖥️</div>
            <div>
                <div class="peer-name" id="hostName">Host PC</div>
                <div class="peer-status">🟢 Online on Home Wi-Fi</div>
            </div>
        </div>
    </header>

    <div id="chat"></div>

    <div id="uploadBanner">
        <div id="uploadText">Uploading file...</div>
        <div class="prog-bar"><div class="prog-fill" id="uploadFill"></div></div>
    </div>

    <footer>
        <button class="btn-attach" onclick="document.getElementById('fileInput').click()">📎</button>
        <input type="file" id="fileInput" style="display:none" onchange="uploadFile(this.files[0])">
        <input type="text" id="textInput" placeholder="Type a message..." onkeydown="if(event.key==='Enter') sendText()">
        <button class="btn-send" onclick="sendText()">➤</button>
    </footer>

    <script>
        let ws;
        let myName = localStorage.getItem('lan_phone_name') || '';
        const hostName = window.location.hostname;

        if (myName) {
            document.getElementById('nameModal').style.display = 'none';
            connectWS();
        }

        function startSession() {
            const val = document.getElementById('phoneName').value.trim();
            if (!val) return alert('Please enter your name');
            myName = val;
            localStorage.setItem('lan_phone_name', myName);
            document.getElementById('nameModal').style.display = 'none';
            connectWS();
        }

        function connectWS() {
            const proto = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
            ws = new WebSocket(`${proto}//${window.location.host}/ws?name=${encodeURIComponent(myName)}`);

            ws.onopen = () => {
                console.log('Connected to PC');
            };

            ws.onmessage = (e) => {
                const data = JSON.parse(e.data);
                if (data.type === 'host_info') {
                    document.getElementById('hostName').innerText = data.username;
                    document.getElementById('hostAvatar').innerText = data.username[0].toUpperCase();
                } else if (data.type === 'text') {
                    addBubble(data.text, false, data.sender);
                } else if (data.type === 'file_notify') {
                    addFileBubble(data.filename, data.filesize, false, data.download_url);
                }
            };

            ws.onclose = () => {
                setTimeout(connectWS, 2000);
            };
        }

        function sendText() {
            const input = document.getElementById('textInput');
            const text = input.value.trim();
            if (!text || !ws) return;
            ws.send(JSON.stringify({ type: 'text', text: text, sender: myName }));
            addBubble(text, true);
            input.value = '';
        }

        function addBubble(text, isOut, sender) {
            const chat = document.getElementById('chat');
            const b = document.createElement('div');
            b.className = 'msg ' + (isOut ? 'out' : 'in');
            const time = new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
            b.innerHTML = (sender && !isOut ? `<div style="font-size:11px; font-weight:bold; color:#00a884; margin-bottom:2px;">${sender}</div>` : '') +
                          `<div>${escapeHtml(text)}</div><div class="time">${time}</div>`;
            chat.appendChild(b);
            chat.scrollTop = chat.scrollHeight;
        }

        function addFileBubble(name, size, isOut, dlUrl) {
            const chat = document.getElementById('chat');
            const b = document.createElement('div');
            b.className = 'msg ' + (isOut ? 'out' : 'in');
            const time = new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
            b.innerHTML = `<div class="file-card">
                <div class="file-icon">📁</div>
                <div>
                    <div class="file-name">${escapeHtml(name)}</div>
                    <div class="file-size">${formatBytes(size)}</div>
                </div>
                ${dlUrl ? `<a href="${dlUrl}" class="btn-dl" download>Download</a>` : ''}
            </div><div class="time">${time}</div>`;
            chat.appendChild(b);
            chat.scrollTop = chat.scrollHeight;
        }

        function uploadFile(file) {
            if (!file) return;
            const banner = document.getElementById('uploadBanner');
            const fill = document.getElementById('uploadFill');
            const text = document.getElementById('uploadText');
            banner.style.display = 'block';

            const xhr = new XMLHttpRequest();
            xhr.open('POST', `/api/upload?sender=${encodeURIComponent(myName)}&filename=${encodeURIComponent(file.name)}`, true);

            xhr.upload.onprogress = (e) => {
                if (e.lengthComputable) {
                    const pct = Math.round((e.loaded / e.total) * 100);
                    fill.style.width = pct + '%';
                    text.innerText = `Uploading ${file.name}: ${pct}%`;
                }
            };

            xhr.onload = () => {
                banner.style.display = 'none';
                fill.style.width = '0%';
                if (xhr.status === 200) {
                    addFileBubble(file.name, file.size, true, null);
                } else {
                    alert('Upload failed: ' + xhr.responseText);
                }
            };

            xhr.onerror = () => {
                banner.style.display = 'none';
                alert('Upload error. Please check Wi-Fi connection.');
            };

            const formData = new FormData();
            formData.append('file', file);
            xhr.send(formData);
        }

        function formatBytes(bytes) {
            if (!bytes) return '0 B';
            const k = 1024, dm = 1, sizes = ['B', 'KB', 'MB', 'GB'];
            const i = Math.floor(Math.log(bytes) / Math.log(k));
            return parseFloat((bytes / Math.pow(k, i)).toFixed(dm)) + ' ' + sizes[i];
        }

        function escapeHtml(str) {
            return str.replace(/[&<>"']/g, m => ({ '&':'&amp;', '<':'&lt;', '>':'&gt;', '"':'&quot;', "'":'&#39;' }[m]));
        }
    </script>
</body>
</html>
"""


class WebPortalManager:
    """Runs a lightweight local web server enabling instant mobile connection via QR code."""

    def __init__(self, port: int = 9878, on_mobile_text=None, on_mobile_file=None):
        self.port = port
        self.on_mobile_text = on_mobile_text
        self.on_mobile_file = on_mobile_file
        self.active_websockets: Set[web.WebSocketResponse] = set()
        self.mobile_users: Dict[web.WebSocketResponse, str] = {}
        self.app = web.Application()
        self.runner: Optional[web.AppRunner] = None
        self.site: Optional[web.TCPSite] = None
        self.setup_routes()

    def setup_routes(self):
        self.app.router.add_get("/", self.handle_index)
        self.app.router.add_get("/ws", self.handle_websocket)
        self.app.router.add_post("/api/upload", self.handle_upload)
        self.app.router.add_get("/api/download/{filename}", self.handle_download)
        self.app.router.add_get("/api/qr", self.handle_qr)

    async def handle_index(self, request):
        return web.Response(text=MOBILE_HTML, content_type="text/html")

    async def handle_qr(self, request):
        """Generates QR code image for scanning."""
        host_ip = request.query.get("ip", request.host.split(":")[0])
        url = f"http://{host_ip}:{self.port}"
        img = qrcode.make(url)
        buf = io.BytesIO()
        img.save(buf, format="PNG")
        buf.seek(0)
        return web.Response(body=buf.read(), content_type="image/png")

    async def handle_websocket(self, request):
        ws = web.WebSocketResponse()
        await ws.prepare(request)

        phone_name = request.query.get("name", "Mobile Phone")
        client_ip = request.remote
        self.active_websockets.add(ws)
        self.mobile_users[ws] = phone_name

        # Notify PC that a mobile connected
        if self.on_mobile_text:
            self.on_mobile_text(
                client_ip,
                f"📱 {phone_name} connected from mobile!",
                time.time(),
                phone_name,
            )

        # Send host info to mobile
        await ws.send_json({"type": "host_info", "username": config.username})

        try:
            async for msg in ws:
                if msg.type == WSMsgType.TEXT:
                    data = json.loads(msg.data)
                    if data.get("type") == "text":
                        text = data.get("text", "")
                        sender = data.get("sender", phone_name)
                        if self.on_mobile_text:
                            self.on_mobile_text(
                                client_ip, text, time.time(), f"📱 {sender}"
                            )
                elif msg.type == WSMsgType.ERROR:
                    break
        finally:
            self.active_websockets.discard(ws)
            self.mobile_users.pop(ws, None)

        return ws

    async def handle_upload(self, request):
        """Streaming file upload from phone."""
        reader = await request.multipart()
        field = await reader.next()
        if not field:
            return web.Response(status=400, text="No file uploaded")

        filename = request.query.get("filename", field.filename or "mobile_file")
        sender = request.query.get("sender", "Mobile Phone")
        client_ip = request.remote

        download_dir = Path(config.download_dir)
        dest_path = get_unique_filepath(download_dir, filename)

        size = 0
        with open(dest_path, "wb") as f:
            while chunk := await field.read_chunk():
                f.write(chunk)
                size += len(chunk)

        if self.on_mobile_file:
            self.on_mobile_file(
                client_ip, str(dest_path), filename, size, f"📱 {sender}"
            )

        return web.Response(text="OK")

    async def handle_download(self, request):
        filename = request.match_info["filename"]
        target_path = Path(config.download_dir) / filename
        if target_path.exists() and target_path.is_file():
            return web.FileResponse(target_path)
        return web.Response(status=404, text="File not found")

    async def broadcast_to_mobiles(self, text: str, sender: str):
        """Sends message from PC to all connected mobile browsers."""
        msg = json.dumps({"type": "text", "text": text, "sender": sender})
        for ws in list(self.active_websockets):
            try:
                await ws.send_str(msg)
            except Exception:
                pass

    async def broadcast_file_to_mobiles(self, filename: str, filesize: int):
        """Notifies mobile phones of a new file ready for download."""
        msg = json.dumps(
            {
                "type": "file_notify",
                "filename": filename,
                "filesize": filesize,
                "download_url": f"/api/download/{filename}",
            }
        )
        for ws in list(self.active_websockets):
            try:
                await ws.send_str(msg)
            except Exception:
                pass

    async def start(self):
        self.runner = web.AppRunner(self.app)
        await self.runner.setup()
        self.site = web.TCPSite(self.runner, "0.0.0.0", self.port)
        await self.site.start()
        print(f"Mobile Web Portal active on http://0.0.0.0:{self.port}")

    async def stop(self):
        if self.runner:
            await self.runner.cleanup()

