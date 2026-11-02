import os
import time
import uuid
import hashlib
import asyncio
from pathlib import Path
from typing import Dict, Any, Optional, Callable
from .protocol import (
    TYPE_FILE_START,
    TYPE_FILE_CHUNK,
    TYPE_FILE_ACK,
    TYPE_FILE_CANCEL,
    encode_json_packet,
    encode_file_chunk,
)
from ..utils.file_helper import get_unique_filepath, compute_file_sha256

CHUNK_SIZE = 256 * 1024  # 256 KB standard chunk
BUFFERED_IO_SIZE = 4 * 1024 * 1024  # 4 MB disk buffer for high-speed sequential writes


class TransferManager:
    def __init__(self, download_dir: str):
        self.download_dir = Path(download_dir)
        self.download_dir.mkdir(parents=True, exist_ok=True)

        # Active incoming transfers: transfer_id -> dict
        self.incoming_transfers: Dict[str, Dict[str, Any]] = {}

        # Callbacks
        self.on_progress: Optional[Callable[[str, int, int, float, bool], None]] = (
            None  # (transfer_id, done, total, mbps, is_upload)
        )
        self.on_file_received: Optional[
            Callable[[str, str, str, int], None]
        ] = None  # (peer_ip, filepath, filename, size)
        self.on_file_sent: Optional[
            Callable[[str, str, str, int], None]
        ] = None  # (peer_ip, filepath, filename, size)

    async def send_file(
        self,
        writer: asyncio.StreamWriter,
        filepath: str,
        peer_ip: str,
        cancel_event: Optional[asyncio.Event] = None,
    ) -> bool:
        """
        Streams a file to the peer over the existing TCP stream using chunked binary frames.
        Provides real-time speed calculation and backpressure flow control.
        """
        path = Path(filepath)
        if not path.is_file():
            raise FileNotFoundError(f"File not found: {filepath}")

        filesize = path.stat().st_size
        filename = path.name
        transfer_id = str(uuid.uuid4())

        # Notify start
        start_payload = {
            "transfer_id": transfer_id,
            "filename": filename,
            "filesize": filesize,
        }
        writer.write(encode_json_packet(TYPE_FILE_START, start_payload))
        await writer.drain()

        sent_bytes = 0
        start_time = time.time()
        last_progress_time = start_time

        try:
            with open(path, "rb", buffering=BUFFERED_IO_SIZE) as f:
                while sent_bytes < filesize:
                    if cancel_event and cancel_event.is_set():
                        writer.write(
                            encode_json_packet(
                                TYPE_FILE_CANCEL, {"transfer_id": transfer_id}
                            )
                        )
                        await writer.drain()
                        return False

                    chunk = f.read(CHUNK_SIZE)
                    if not chunk:
                        break

                    chunk_packet = encode_file_chunk(transfer_id, sent_bytes, chunk)
                    writer.write(chunk_packet)
                    await writer.drain()

                    sent_bytes += len(chunk)

                    now = time.time()
                    if (
                        now - last_progress_time >= 0.1
                        or sent_bytes >= filesize
                    ):
                        elapsed = max(now - start_time, 0.001)
                        speed_mbps = (sent_bytes / (1024 * 1024)) / elapsed
                        if self.on_progress:
                            self.on_progress(
                                transfer_id, sent_bytes, filesize, speed_mbps, True
                            )
                        last_progress_time = now

            if self.on_file_sent:
                self.on_file_sent(peer_ip, str(path), filename, filesize)
            return True

        except Exception as e:
            print(f"Error during file send: {e}")
            raise

    def handle_file_start(self, data: Dict[str, Any], peer_ip: str) -> str:
        """Initializes incoming file reception."""
        transfer_id = data["transfer_id"]
        filename = data["filename"]
        filesize = data["filesize"]

        # Ensure unique destination path in download directory
        dest_path = get_unique_filepath(self.download_dir, filename)
        part_path = dest_path.with_name(f"{dest_path.name}.part")

        # Buffered write handle optimizes slow mechanical Hard Drives and high-speed NVMe
        f_handle = open(part_path, "wb", buffering=BUFFERED_IO_SIZE)

        self.incoming_transfers[transfer_id] = {
            "transfer_id": transfer_id,
            "filename": filename,
            "dest_path": str(dest_path),
            "part_path": str(part_path),
            "filesize": filesize,
            "received_bytes": 0,
            "file_handle": f_handle,
            "peer_ip": peer_ip,
            "start_time": time.time(),
            "last_progress_time": time.time(),
        }
        return transfer_id

    def handle_file_chunk(
        self, transfer_id: str, offset: int, data: bytes
    ) -> Optional[Dict[str, Any]]:
        """
        Writes received chunk directly to disk.
        Returns transfer result dict if finished, otherwise None.
        """
        transfer = self.incoming_transfers.get(transfer_id)
        if not transfer:
            return None

        f_handle = transfer["file_handle"]
        f_handle.write(data)
        transfer["received_bytes"] += len(data)

        now = time.time()
        received = transfer["received_bytes"]
        total = transfer["filesize"]

        if now - transfer["last_progress_time"] >= 0.1 or received >= total:
            elapsed = max(now - transfer["start_time"], 0.001)
            speed_mbps = (received / (1024 * 1024)) / elapsed
            if self.on_progress:
                self.on_progress(transfer_id, received, total, speed_mbps, False)
            transfer["last_progress_time"] = now

        # Check if complete
        if received >= total:
            f_handle.close()
            # Atomically rename .part -> final filename
            part_path = Path(transfer["part_path"])
            dest_path = Path(transfer["dest_path"])
            if part_path.exists():
                part_path.rename(dest_path)

            completed_info = {
                "transfer_id": transfer_id,
                "peer_ip": transfer["peer_ip"],
                "filepath": str(dest_path),
                "filename": transfer["filename"],
                "filesize": total,
            }

            del self.incoming_transfers[transfer_id]

            if self.on_file_received:
                self.on_file_received(
                    completed_info["peer_ip"],
                    completed_info["filepath"],
                    completed_info["filename"],
                    completed_info["filesize"],
                )

            return completed_info

        return None

    def cancel_transfer(self, transfer_id: str):
        """Cancels and cleans up partial file transfer."""
        transfer = self.incoming_transfers.pop(transfer_id, None)
        if transfer:
            try:
                transfer["file_handle"].close()
                part_path = Path(transfer["part_path"])
                if part_path.exists():
                    part_path.unlink()
            except Exception:
                pass

