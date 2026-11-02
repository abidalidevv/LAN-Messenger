import struct
import json
import asyncio
from typing import Tuple, Dict, Any, Optional

MAGIC = b"LM"  # LAN Messenger magic bytes
HEADER_FORMAT = "!2sBBI"  # Magic (2s), Type (B), Flags (B), Length (I)
HEADER_SIZE = struct.calcsize(HEADER_FORMAT)  # 8 bytes

# Message Types
TYPE_HANDSHAKE = 0x01
TYPE_HANDSHAKE_ACK = 0x02
TYPE_HEARTBEAT = 0x03
TYPE_TEXT_MSG = 0x10
TYPE_FILE_START = 0x20
TYPE_FILE_CHUNK = 0x21
TYPE_FILE_ACK = 0x22
TYPE_FILE_CANCEL = 0x23

# Voice Call Types
TYPE_CALL_REQUEST = 0x30
TYPE_CALL_ACCEPT = 0x31
TYPE_CALL_REJECT = 0x32
TYPE_CALL_END = 0x33
TYPE_CALL_AUDIO_FRAME = 0x34

# Screen Share Types
TYPE_SCREEN_START = 0x40
TYPE_SCREEN_FRAME = 0x41
TYPE_SCREEN_STOP = 0x42


def encode_frame(msg_type: int, payload: bytes = b"", flags: int = 0) -> bytes:
    """Encodes a payload into a framed binary packet with standard 8-byte header."""
    header = struct.pack(HEADER_FORMAT, MAGIC, msg_type, flags, len(payload))
    return header + payload


async def read_exact(reader: asyncio.StreamReader, n: int) -> bytes:
    """Reads exactly n bytes from the stream, handling partial TCP reads."""
    data = bytearray()
    while len(data) < n:
        packet = await reader.read(n - len(data))
        if not packet:
            raise ConnectionResetError("Connection closed before reading expected bytes")
        data.extend(packet)
    return bytes(data)


async def read_frame(reader: asyncio.StreamReader) -> Tuple[int, int, bytes]:
    """
    Reads one complete framed packet from the stream.
    Returns: (msg_type, flags, payload)
    """
    header_data = await read_exact(reader, HEADER_SIZE)
    magic, msg_type, flags, payload_len = struct.unpack(HEADER_FORMAT, header_data)
    if magic != MAGIC:
        raise ValueError(f"Invalid packet magic: {magic}")

    if payload_len > 0:
        payload = await read_exact(reader, payload_len)
    else:
        payload = b""

    return msg_type, flags, payload


# Helper Encoders / Decoders for JSON-based control packets
def encode_json_packet(msg_type: int, data: Dict[str, Any]) -> bytes:
    payload = json.dumps(data).encode("utf-8")
    return encode_frame(msg_type, payload)


def decode_json_payload(payload: bytes) -> Dict[str, Any]:
    return json.loads(payload.decode("utf-8"))


# Binary File Chunk Encoding / Decoding
CHUNK_HEADER_FORMAT = "!36sQI"  # TransferID (36s string), Offset (Q uint64), ChunkLen (I uint32)
CHUNK_HEADER_SIZE = struct.calcsize(CHUNK_HEADER_FORMAT)


def encode_file_chunk(transfer_id: str, offset: int, data: bytes) -> bytes:
    """
    Encodes raw binary file chunk with zero base64 overhead.
    transfer_id: UUID string up to 36 chars
    offset: byte offset in file
    data: raw bytes
    """
    tid_bytes = transfer_id.encode("utf-8").ljust(36, b"\x00")[:36]
    chunk_header = struct.pack(CHUNK_HEADER_FORMAT, tid_bytes, offset, len(data))
    payload = chunk_header + data
    return encode_frame(TYPE_FILE_CHUNK, payload)


def decode_file_chunk(payload: bytes) -> Tuple[str, int, bytes]:
    """Decodes raw binary file chunk into (transfer_id, offset, data)."""
    if len(payload) < CHUNK_HEADER_SIZE:
        raise ValueError("Payload too small for file chunk header")
    tid_bytes, offset, chunk_len = struct.unpack(
        CHUNK_HEADER_FORMAT, payload[:CHUNK_HEADER_SIZE]
    )
    transfer_id = tid_bytes.decode("utf-8").rstrip("\x00")
    data = payload[CHUNK_HEADER_SIZE : CHUNK_HEADER_SIZE + chunk_len]
    return transfer_id, offset, data

