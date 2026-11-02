import asyncio
import time
from typing import Dict, Any, Optional, Callable
from .protocol import (
    TYPE_HANDSHAKE,
    TYPE_HANDSHAKE_ACK,
    TYPE_HEARTBEAT,
    TYPE_TEXT_MSG,
    TYPE_FILE_START,
    TYPE_FILE_CHUNK,
    TYPE_FILE_ACK,
    TYPE_FILE_CANCEL,
    TYPE_CALL_REQUEST,
    TYPE_CALL_ACCEPT,
    TYPE_CALL_REJECT,
    TYPE_CALL_END,
    TYPE_CALL_AUDIO_FRAME,
    TYPE_SCREEN_START,
    TYPE_SCREEN_FRAME,
    TYPE_SCREEN_STOP,
    encode_frame,
    encode_json_packet,
    decode_json_payload,
    decode_file_chunk,
    read_frame,
)
from .transfer import TransferManager


class PeerConnection:
    """Manages an active bidirectional TCP connection with a single peer."""

    def __init__(
        self,
        peer_ip: str,
        reader: asyncio.StreamReader,
        writer: asyncio.StreamWriter,
        local_username: str,
        transfer_mgr: TransferManager,
        on_text_msg: Callable[[str, str, float], None],  # (peer_ip, text, timestamp)
        on_peer_info: Callable[[str, str], None],  # (peer_ip, username)
        on_disconnected: Callable[[str], None],  # (peer_ip)
        on_media_event: Optional[Callable[[str, str, Any], None]] = None,  # (peer_ip, event_type, data)
    ):
        self.peer_ip = peer_ip
        self.reader = reader
        self.writer = writer
        self.local_username = local_username
        self.transfer_mgr = transfer_mgr
        self.on_text_msg = on_text_msg
        self.on_peer_info = on_peer_info
        self.on_disconnected = on_disconnected
        self.on_media_event = on_media_event

        self.peer_username: str = f"Peer @ {peer_ip}"
        self.is_active = True
        self.write_lock = asyncio.Lock()
        self.last_activity = time.time()
        self._read_task: Optional[asyncio.Task] = None
        self._heartbeat_task: Optional[asyncio.Task] = None

    def start(self, loop: asyncio.AbstractEventLoop):
        self._read_task = loop.create_task(self._read_loop())
        self._heartbeat_task = loop.create_task(self._heartbeat_loop())

    async def send_handshake(self, is_ack: bool = False):
        """Sends initial identity handshake."""
        msg_type = TYPE_HANDSHAKE_ACK if is_ack else TYPE_HANDSHAKE
        payload = {"username": self.local_username, "timestamp": time.time()}
        async with self.write_lock:
            self.writer.write(encode_json_packet(msg_type, payload))
            await self.writer.drain()

    async def send_text(self, text: str):
        """Sends a text message to the peer."""
        payload = {
            "text": text,
            "timestamp": time.time(),
            "sender": self.local_username,
        }
        async with self.write_lock:
            self.writer.write(encode_json_packet(TYPE_TEXT_MSG, payload))
            await self.writer.drain()

    async def send_file(self, filepath: str) -> bool:
        """Sends a file using chunked binary stream with write lock protection."""
        async with self.write_lock:
            return await self.transfer_mgr.send_file(
                self.writer, filepath, self.peer_ip
            )

    async def send_call_request(self):
        async with self.write_lock:
            self.writer.write(
                encode_json_packet(
                    TYPE_CALL_REQUEST, {"caller": self.local_username}
                )
            )
            await self.writer.drain()

    async def send_call_accept(self):
        async with self.write_lock:
            self.writer.write(encode_json_packet(TYPE_CALL_ACCEPT, {}))
            await self.writer.drain()

    async def send_call_reject(self):
        async with self.write_lock:
            self.writer.write(encode_json_packet(TYPE_CALL_REJECT, {}))
            await self.writer.drain()

    async def send_call_end(self):
        async with self.write_lock:
            self.writer.write(encode_json_packet(TYPE_CALL_END, {}))
            await self.writer.drain()

    async def send_audio_frame(self, pcm_bytes: bytes):
        async with self.write_lock:
            self.writer.write(encode_frame(TYPE_CALL_AUDIO_FRAME, pcm_bytes))
            await self.writer.drain()

    async def send_screen_start(self):
        async with self.write_lock:
            self.writer.write(
                encode_json_packet(
                    TYPE_SCREEN_START, {"sharer": self.local_username}
                )
            )
            await self.writer.drain()

    async def send_screen_frame(self, jpeg_bytes: bytes):
        async with self.write_lock:
            self.writer.write(encode_frame(TYPE_SCREEN_FRAME, jpeg_bytes))
            await self.writer.drain()

    async def send_screen_stop(self):
        async with self.write_lock:
            self.writer.write(encode_json_packet(TYPE_SCREEN_STOP, {}))
            await self.writer.drain()

    async def _heartbeat_loop(self):
        """Sends periodic ping frames to maintain NAT state and detect dead connections."""
        while self.is_active:
            try:
                await asyncio.sleep(10.0)
                if not self.is_active:
                    break
                async with self.write_lock:
                    self.writer.write(encode_frame(TYPE_HEARTBEAT, b"PING"))
                    await self.writer.drain()
            except Exception:
                await self.close()
                break

    async def _read_loop(self):
        """Continuously reads incoming framed packets from the TCP stream."""
        try:
            while self.is_active:
                msg_type, flags, payload = await read_frame(self.reader)
                self.last_activity = time.time()

                if msg_type == TYPE_HANDSHAKE or msg_type == TYPE_HANDSHAKE_ACK:
                    data = decode_json_payload(payload)
                    self.peer_username = data.get("username", self.peer_username)
                    self.on_peer_info(self.peer_ip, self.peer_username)
                    if msg_type == TYPE_HANDSHAKE:
                        await self.send_handshake(is_ack=True)

                elif msg_type == TYPE_TEXT_MSG:
                    data = decode_json_payload(payload)
                    text = data.get("text", "")
                    ts = data.get("timestamp", time.time())
                    self.on_text_msg(self.peer_ip, text, ts)

                elif msg_type == TYPE_FILE_START:
                    data = decode_json_payload(payload)
                    self.transfer_mgr.handle_file_start(data, self.peer_ip)

                elif msg_type == TYPE_FILE_CHUNK:
                    tid, offset, chunk_data = decode_file_chunk(payload)
                    res = self.transfer_mgr.handle_file_chunk(tid, offset, chunk_data)
                    if res:
                        # File completed, send ACK back
                        async with self.write_lock:
                            self.writer.write(
                                encode_json_packet(
                                    TYPE_FILE_ACK, {"transfer_id": tid, "status": "ok"}
                                )
                            )
                            await self.writer.drain()

                elif msg_type == TYPE_FILE_CANCEL:
                    data = decode_json_payload(payload)
                    self.transfer_mgr.cancel_transfer(data.get("transfer_id", ""))

                elif msg_type == TYPE_CALL_REQUEST:
                    data = decode_json_payload(payload)
                    if self.on_media_event:
                        self.on_media_event(self.peer_ip, "call_request", data)

                elif msg_type == TYPE_CALL_ACCEPT:
                    if self.on_media_event:
                        self.on_media_event(self.peer_ip, "call_accept", {})

                elif msg_type == TYPE_CALL_REJECT:
                    if self.on_media_event:
                        self.on_media_event(self.peer_ip, "call_reject", {})

                elif msg_type == TYPE_CALL_END:
                    if self.on_media_event:
                        self.on_media_event(self.peer_ip, "call_end", {})

                elif msg_type == TYPE_CALL_AUDIO_FRAME:
                    if self.on_media_event:
                        self.on_media_event(
                            self.peer_ip, "audio_frame", payload
                        )

                elif msg_type == TYPE_SCREEN_START:
                    data = decode_json_payload(payload)
                    if self.on_media_event:
                        self.on_media_event(self.peer_ip, "screen_start", data)

                elif msg_type == TYPE_SCREEN_FRAME:
                    if self.on_media_event:
                        self.on_media_event(
                            self.peer_ip, "screen_frame", payload
                        )

                elif msg_type == TYPE_SCREEN_STOP:
                    if self.on_media_event:
                        self.on_media_event(self.peer_ip, "screen_stop", {})

                elif msg_type == TYPE_HEARTBEAT:
                    pass  # keepalive received

        except (asyncio.IncompleteReadError, ConnectionResetError, BrokenPipeError):
            pass
        except Exception as e:
            print(f"Connection read error with {self.peer_ip}: {e}")
        finally:
            await self.close()

    async def close(self):
        if not self.is_active:
            return
        self.is_active = False
        if self._heartbeat_task:
            self._heartbeat_task.cancel()
        if self._read_task:
            self._read_task.cancel()

        try:
            self.writer.close()
            await self.writer.wait_closed()
        except Exception:
            pass

        self.on_disconnected(self.peer_ip)

