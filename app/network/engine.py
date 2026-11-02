import asyncio
import threading
import time
from typing import Dict, Any, Optional, List
from PyQt6.QtCore import QObject, pyqtSignal

from .protocol import (
    TYPE_HANDSHAKE,
    encode_json_packet,
    decode_json_payload,
)
from .discovery import PeerDiscovery, get_local_ip_addresses
from .transfer import TransferManager
from .connection import PeerConnection
from .web_portal import WebPortalManager
from ..config import config


class NetworkEngine(QObject):
    """
    Master networking engine running an asyncio event loop in a dedicated background thread.
    Emits thread-safe PyQt signals to update the UI without ever blocking the GUI.
    """

    # PyQt Signals for UI Updates
    sig_peer_discovered = pyqtSignal(dict)  # peer dict
    sig_peer_status = pyqtSignal(str, str)  # ip, status ("online" / "offline")
    sig_text_received = pyqtSignal(str, str, float)  # ip, text, timestamp
    sig_file_progress = pyqtSignal(
        str, int, int, float, bool
    )  # tid, done, total, mbps, is_upload
    sig_file_received = pyqtSignal(
        str, str, str, int
    )  # ip, filepath, filename, filesize
    sig_file_sent = pyqtSignal(
        str, str, str, int
    )  # ip, filepath, filename, filesize
    sig_engine_ready = pyqtSignal(str, int)  # local_ip, port
    sig_sweep_completed = pyqtSignal(int)  # found_count

    # Voice Call and Screen Share Signals
    sig_call_request = pyqtSignal(str, dict)  # ip, data
    sig_call_accepted = pyqtSignal(str)  # ip
    sig_call_rejected = pyqtSignal(str)  # ip
    sig_call_ended = pyqtSignal(str)  # ip
    sig_audio_frame = pyqtSignal(str, bytes)  # ip, pcm
    sig_screen_started = pyqtSignal(str, dict)  # ip, data
    sig_screen_frame = pyqtSignal(str, bytes)  # ip, jpeg
    sig_screen_stopped = pyqtSignal(str)  # ip

    def __init__(self):
        super().__init__()
        self.tcp_port = config.tcp_port
        self.udp_port = config.udp_port
        self.username = config.username

        self.transfer_mgr = TransferManager(config.download_dir)
        self.transfer_mgr.on_progress = self._on_transfer_progress
        self.transfer_mgr.on_file_received = self._on_file_received
        self.transfer_mgr.on_file_sent = self._on_file_sent

        self.connections: Dict[str, PeerConnection] = {}  # ip -> PeerConnection
        self.peers: Dict[str, Dict[str, Any]] = {}  # ip -> peer_info

        self.web_portal = WebPortalManager(
            port=9878,
            on_mobile_text=self._on_mobile_text_received,
            on_mobile_file=self._on_mobile_file_received,
        )

        self._loop: Optional[asyncio.AbstractEventLoop] = None
        self._thread: Optional[threading.Thread] = None
        self._server: Optional[asyncio.Server] = None
        self._discovery: Optional[PeerDiscovery] = None
        self._running = False

    def start(self):
        """Starts the background network thread and asyncio loop."""
        self._running = True
        self._thread = threading.Thread(
            target=self._run_network_loop, daemon=True, name="NetworkEngineThread"
        )
        self._thread.start()

    def _run_network_loop(self):
        """Worker thread entry point."""
        self._loop = asyncio.new_event_loop()
        asyncio.set_event_loop(self._loop)
        self._loop.run_until_complete(self._main_async())

    async def _main_async(self):
        """Initializes TCP server and UDP discovery inside the asyncio loop."""
        local_ips = get_local_ip_addresses()
        primary_ip = local_ips[0] if local_ips else "127.0.0.1"

        # 1. Start TCP Server
        try:
            self._server = await asyncio.start_server(
                self._handle_incoming_client, "0.0.0.0", self.tcp_port
            )
            print(f"TCP Server listening on 0.0.0.0:{self.tcp_port}")
            self.sig_engine_ready.emit(primary_ip, self.tcp_port)
        except Exception as e:
            print(f"Error starting TCP server on port {self.tcp_port}: {e}")

        # 2. Start UDP Discovery
        self._discovery = PeerDiscovery(
            username=self.username,
            tcp_port=self.tcp_port,
            udp_port=self.udp_port,
            custom_subnets=config.custom_subnets,
            on_peer_found=self._on_peer_discovered_callback,
            on_peer_lost=self._on_peer_lost_callback,
        )
        self._discovery.start(self._loop)

        # 3. Start Mobile Web Portal
        try:
            await self.web_portal.start()
        except Exception as e:
            print(f"Error starting mobile web portal: {e}")

        # 4. Add saved peers from config
        for ip in config.saved_peers:
            if ip not in local_ips:
                self._discovery.record_peer(ip, f"Saved @ {ip}", self.tcp_port)

        # 4. Run initial background sweep
        asyncio.create_task(self._auto_sweep())

        # Keep loop running
        while self._running:
            await asyncio.sleep(1.0)

    async def _auto_sweep(self):
        """Performs initial quick sweep of dual subnets (Huawei & Tenda)."""
        await asyncio.sleep(1.0)
        await self.async_sweep_subnets()

    async def _handle_incoming_client(
        self, reader: asyncio.StreamReader, writer: asyncio.StreamWriter
    ):
        """Handles an incoming TCP connection from a peer."""
        peer_addr = writer.get_extra_info("peername")
        peer_ip = peer_addr[0] if peer_addr else "unknown"

        # If we already have an active connection with this peer, close the older one
        old_conn = self.connections.get(peer_ip)
        if old_conn and old_conn.is_active:
            await old_conn.close()

        conn = PeerConnection(
            peer_ip=peer_ip,
            reader=reader,
            writer=writer,
            local_username=self.username,
            transfer_mgr=self.transfer_mgr,
            on_text_msg=self._on_text_received,
            on_peer_info=self._on_peer_info,
            on_disconnected=self._on_peer_disconnected,
            on_media_event=self._on_media_event,
        )
        self.connections[peer_ip] = conn
        conn.start(self._loop)

        # Update peer record
        if peer_ip in self.peers:
            self.peers[peer_ip]["status"] = "online"
            self.sig_peer_status.emit(peer_ip, "online")

    async def _get_or_create_connection(
        self, peer_ip: str
    ) -> Optional[PeerConnection]:
        """Returns existing connection or establishes a new outbound one."""
        conn = self.connections.get(peer_ip)
        if conn and conn.is_active:
            return conn

        # Connect outbound
        try:
            reader, writer = await asyncio.open_connection(peer_ip, self.tcp_port)
            new_conn = PeerConnection(
                peer_ip=peer_ip,
                reader=reader,
                writer=writer,
                local_username=self.username,
                transfer_mgr=self.transfer_mgr,
                on_text_msg=self._on_text_received,
                on_peer_info=self._on_peer_info,
                on_disconnected=self._on_peer_disconnected,
                on_media_event=self._on_media_event,
            )
            self.connections[peer_ip] = new_conn
            new_conn.start(self._loop)
            await new_conn.send_handshake(is_ack=False)

            if peer_ip in self.peers:
                self.peers[peer_ip]["status"] = "online"
                self.sig_peer_status.emit(peer_ip, "online")

            return new_conn
        except Exception as e:
            print(f"Could not connect to {peer_ip}:{self.tcp_port} - {e}")
            if peer_ip in self.peers:
                self.peers[peer_ip]["status"] = "offline"
                self.sig_peer_status.emit(peer_ip, "offline")
            return None

    def _on_mobile_text_received(
        self, client_ip: str, text: str, timestamp: float, sender_name: str
    ):
        """Called when a message arrives from a connected mobile phone."""
        peer_data = {
            "ip": client_ip,
            "username": sender_name,
            "port": 9878,
            "status": "online",
            "is_mobile": True,
        }
        self.peers[client_ip] = peer_data
        self.sig_peer_discovered.emit(peer_data)
        self.sig_text_received.emit(client_ip, text, timestamp)

    def _on_mobile_file_received(
        self,
        client_ip: str,
        filepath: str,
        filename: str,
        filesize: int,
        sender_name: str,
    ):
        """Called when a file is uploaded from a mobile phone."""
        peer_data = {
            "ip": client_ip,
            "username": sender_name,
            "port": 9878,
            "status": "online",
            "is_mobile": True,
        }
        self.peers[client_ip] = peer_data
        self.sig_peer_discovered.emit(peer_data)
        self.sig_file_received.emit(client_ip, filepath, filename, filesize)

    # UI-facing Thread-Safe Invocation Methods
    def send_text(self, peer_ip: str, text: str):
        """Thread-safe call from UI to send a text message."""
        if self._loop and self._loop.is_running():
            if peer_ip == "BROADCAST":
                asyncio.run_coroutine_threadsafe(
                    self._async_send_text_broadcast(text), self._loop
                )
            else:
                asyncio.run_coroutine_threadsafe(
                    self._async_send_text(peer_ip, text), self._loop
                )

    async def _async_send_text_broadcast(self, text: str):
        """Broadcasts text message to all online peers and mobile devices."""
        await self.web_portal.broadcast_to_mobiles(text, self.username)
        for ip in list(self.peers.keys()):
            if ip != "BROADCAST" and not self.peers[ip].get("is_mobile"):
                try:
                    conn = await self._get_or_create_connection(ip)
                    if conn:
                        await conn.send_text(text)
                except Exception:
                    pass

    async def _async_send_text(self, peer_ip: str, text: str):
        # Broadcast to mobile if target is mobile or connected
        await self.web_portal.broadcast_to_mobiles(text, self.username)
        conn = await self._get_or_create_connection(peer_ip)
        if conn:
            await conn.send_text(text)

    def send_file(self, peer_ip: str, filepath: str):
        """Thread-safe call from UI to send a file."""
        if self._loop and self._loop.is_running():
            if peer_ip == "BROADCAST":
                asyncio.run_coroutine_threadsafe(
                    self._async_send_file_broadcast(filepath), self._loop
                )
            else:
                asyncio.run_coroutine_threadsafe(
                    self._async_send_file(peer_ip, filepath), self._loop
                )

    async def _async_send_file_broadcast(self, filepath: str):
        """Broadcasts file to all online peers and mobile devices."""
        path = Path(filepath)
        await self.web_portal.broadcast_file_to_mobiles(path.name, path.stat().st_size)
        for ip in list(self.peers.keys()):
            if ip != "BROADCAST" and not self.peers[ip].get("is_mobile"):
                try:
                    conn = await self._get_or_create_connection(ip)
                    if conn:
                        await conn.send_file(filepath)
                except Exception:
                    pass

    async def _async_send_file(self, peer_ip: str, filepath: str):
        path = Path(filepath)
        await self.web_portal.broadcast_file_to_mobiles(path.name, path.stat().st_size)
        conn = await self._get_or_create_connection(peer_ip)
        if conn:
            await conn.send_file(filepath)

    def scan_subnets(self):
        """Thread-safe call from UI to trigger quick subnet sweep."""
        if self._loop and self._loop.is_running():
            asyncio.run_coroutine_threadsafe(self.async_sweep_subnets(), self._loop)

    async def async_sweep_subnets(self):
        if self._discovery:
            found = await self._discovery.fast_sweep_subnets()
            self.sig_sweep_completed.emit(len(found))

    def add_manual_peer(self, ip: str):
        """Adds peer IP manually and initiates connection test."""
        config.add_saved_peer(ip)
        if self._discovery:
            self._discovery.record_peer(ip, f"Peer @ {ip}", self.tcp_port)
        if self._loop and self._loop.is_running():
            asyncio.run_coroutine_threadsafe(
                self._get_or_create_connection(ip), self._loop
            )

    def update_username(self, new_name: str):
        self.username = new_name
        config.username = new_name
        if self._discovery:
            self._discovery.username = new_name

    # Internal Callbacks bridging to PyQt Signals
    def _on_peer_discovered_callback(self, peer_info: Dict[str, Any]):
        ip = peer_info["ip"]
        self.peers[ip] = peer_info
        self.sig_peer_discovered.emit(peer_info)
        # Attempt proactive reverse connection to establish duplex NAT tunnel
        if self._loop and self._loop.is_running():
            asyncio.run_coroutine_threadsafe(
                self._get_or_create_connection(ip), self._loop
            )

    def _on_peer_lost_callback(self, ip: str):
        if ip in self.peers:
            self.peers[ip]["status"] = "offline"
            self.sig_peer_status.emit(ip, "offline")

    def _on_peer_info(self, peer_ip: str, username: str):
        if peer_ip in self.peers:
            self.peers[peer_ip]["username"] = username
        peer_data = self.peers.get(
            peer_ip, {"ip": peer_ip, "username": username, "status": "online"}
        )
        self.sig_peer_discovered.emit(peer_data)

    def _on_media_event(self, peer_ip: str, event_type: str, data: Any):
        """Dispatches media events from connection to PyQt signals."""
        if event_type == "call_request":
            self.sig_call_request.emit(peer_ip, data)
        elif event_type == "call_accept":
            self.sig_call_accepted.emit(peer_ip)
        elif event_type == "call_reject":
            self.sig_call_rejected.emit(peer_ip)
        elif event_type == "call_end":
            self.sig_call_ended.emit(peer_ip)
        elif event_type == "audio_frame":
            self.sig_audio_frame.emit(peer_ip, data)
        elif event_type == "screen_start":
            self.sig_screen_started.emit(peer_ip, data)
        elif event_type == "screen_frame":
            self.sig_screen_frame.emit(peer_ip, data)
        elif event_type == "screen_stop":
            self.sig_screen_stopped.emit(peer_ip)

    # Thread-Safe Voice Call & Screen Share Methods
    def request_call(self, peer_ip: str):
        if self._loop and self._loop.is_running():
            asyncio.run_coroutine_threadsafe(
                self._async_request_call(peer_ip), self._loop
            )

    async def _async_request_call(self, peer_ip: str):
        conn = await self._get_or_create_connection(peer_ip)
        if conn:
            await conn.send_call_request()

    def accept_call(self, peer_ip: str):
        if self._loop and self._loop.is_running():
            asyncio.run_coroutine_threadsafe(
                self._async_accept_call(peer_ip), self._loop
            )

    async def _async_accept_call(self, peer_ip: str):
        conn = await self._get_or_create_connection(peer_ip)
        if conn:
            await conn.send_call_accept()

    def reject_call(self, peer_ip: str):
        if self._loop and self._loop.is_running():
            asyncio.run_coroutine_threadsafe(
                self._async_reject_call(peer_ip), self._loop
            )

    async def _async_reject_call(self, peer_ip: str):
        conn = await self._get_or_create_connection(peer_ip)
        if conn:
            await conn.send_call_reject()

    def end_call(self, peer_ip: str):
        if self._loop and self._loop.is_running():
            asyncio.run_coroutine_threadsafe(
                self._async_end_call(peer_ip), self._loop
            )

    async def _async_end_call(self, peer_ip: str):
        conn = await self._get_or_create_connection(peer_ip)
        if conn:
            await conn.send_call_end()

    def send_audio_chunk(self, peer_ip: str, pcm_bytes: bytes):
        if self._loop and self._loop.is_running():
            asyncio.run_coroutine_threadsafe(
                self._async_send_audio(peer_ip, pcm_bytes), self._loop
            )

    async def _async_send_audio(self, peer_ip: str, pcm_bytes: bytes):
        conn = await self._get_or_create_connection(peer_ip)
        if conn:
            await conn.send_audio_frame(pcm_bytes)

    def start_screen_share(self, peer_ip: str):
        if self._loop and self._loop.is_running():
            asyncio.run_coroutine_threadsafe(
                self._async_start_screen(peer_ip), self._loop
            )

    async def _async_start_screen(self, peer_ip: str):
        conn = await self._get_or_create_connection(peer_ip)
        if conn:
            await conn.send_screen_start()

    def send_screen_chunk(self, peer_ip: str, jpeg_bytes: bytes):
        if self._loop and self._loop.is_running():
            asyncio.run_coroutine_threadsafe(
                self._async_send_screen(peer_ip, jpeg_bytes), self._loop
            )

    async def _async_send_screen(self, peer_ip: str, jpeg_bytes: bytes):
        conn = await self._get_or_create_connection(peer_ip)
        if conn:
            await conn.send_screen_frame(jpeg_bytes)

    def stop_screen_share(self, peer_ip: str):
        if self._loop and self._loop.is_running():
            asyncio.run_coroutine_threadsafe(
                self._async_stop_screen(peer_ip), self._loop
            )

    async def _async_stop_screen(self, peer_ip: str):
        conn = await self._get_or_create_connection(peer_ip)
        if conn:
            await conn.send_screen_stop()

    def _on_text_received(self, peer_ip: str, text: str, timestamp: float):
        self.sig_text_received.emit(peer_ip, text, timestamp)

    def _on_transfer_progress(
        self,
        transfer_id: str,
        done: int,
        total: int,
        speed_mbps: float,
        is_upload: bool,
    ):
        self.sig_file_progress.emit(transfer_id, done, total, speed_mbps, is_upload)

    def _on_file_received(
        self, peer_ip: str, filepath: str, filename: str, filesize: int
    ):
        self.sig_file_received.emit(peer_ip, filepath, filename, filesize)

    def _on_file_sent(
        self, peer_ip: str, filepath: str, filename: str, filesize: int
    ):
        self.sig_file_sent.emit(peer_ip, filepath, filename, filesize)

    def stop(self):
        """Gracefully shuts down network server, discovery, web portal, and connections."""
        self._running = False
        if self._discovery:
            self._discovery.stop()
        if self._loop and self._loop.is_running():
            asyncio.run_coroutine_threadsafe(self.web_portal.stop(), self._loop)
            # Close all active connections
            for conn in list(self.connections.values()):
                asyncio.run_coroutine_threadsafe(conn.close(), self._loop)
            if self._server:
                self._server.close()
            self._loop.call_soon_threadsafe(self._loop.stop)

