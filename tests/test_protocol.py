import unittest
import asyncio
from app.network.protocol import (
    TYPE_HANDSHAKE,
    TYPE_TEXT_MSG,
    TYPE_FILE_CHUNK,
    encode_frame,
    read_frame,
    encode_json_packet,
    decode_json_payload,
    encode_file_chunk,
    decode_file_chunk,
)


class TestProtocol(unittest.TestCase):
    def test_encode_decode_json_packet(self):
        sample_data = {"username": "Ali Laptop", "ip": "192.168.100.8", "port": 9876}
        encoded = encode_json_packet(TYPE_HANDSHAKE, sample_data)

        async def parse():
            reader = asyncio.StreamReader()
            reader.feed_data(encoded)
            reader.feed_eof()
            msg_type, flags, payload = await read_frame(reader)
            self.assertEqual(msg_type, TYPE_HANDSHAKE)
            decoded = decode_json_payload(payload)
            self.assertEqual(decoded, sample_data)

        asyncio.run(parse())

    def test_encode_decode_file_chunk(self):
        transfer_id = "test-uuid-1234-5678-abcdef"
        offset = 1048576
        raw_data = b"X" * 65536  # 64 KB binary data

        encoded_packet = encode_file_chunk(transfer_id, offset, raw_data)

        async def parse():
            reader = asyncio.StreamReader()
            reader.feed_data(encoded_packet)
            reader.feed_eof()
            msg_type, flags, payload = await read_frame(reader)
            self.assertEqual(msg_type, TYPE_FILE_CHUNK)
            dec_tid, dec_offset, dec_data = decode_file_chunk(payload)
            self.assertEqual(dec_tid, transfer_id)
            self.assertEqual(dec_offset, offset)
            self.assertEqual(dec_data, raw_data)

        asyncio.run(parse())

    def test_partial_tcp_reads(self):
        """Simulates fragmented TCP packets arriving byte-by-byte."""
        sample_data = {"message": "Hello from segmented TCP stream!"}
        encoded = encode_json_packet(TYPE_TEXT_MSG, sample_data)

        async def parse():
            reader = asyncio.StreamReader()
            # Feed packet 3 bytes at a time
            for i in range(0, len(encoded), 3):
                reader.feed_data(encoded[i : i + 3])
                await asyncio.sleep(0.001)
            reader.feed_eof()

            msg_type, flags, payload = await read_frame(reader)
            self.assertEqual(msg_type, TYPE_TEXT_MSG)
            decoded = decode_json_payload(payload)
            self.assertEqual(decoded["message"], sample_data["message"])

        asyncio.run(parse())


if __name__ == "__main__":
    unittest.main()

