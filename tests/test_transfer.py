import os
import tempfile
import unittest
from pathlib import Path
from app.network.transfer import TransferManager
from app.utils.file_helper import compute_file_sha256


class TestTransferManager(unittest.TestCase):
    def setUp(self):
        self.temp_dir = tempfile.TemporaryDirectory()
        self.transfer_mgr = TransferManager(self.temp_dir.name)

    def tearDown(self):
        self.temp_dir.cleanup()

    def test_direct_chunk_reception(self):
        # Create a test file payload of 1 MB
        original_data = os.urandom(1024 * 1024)
        hasher = compute_file_sha256

        tid = "transfer-unit-test-1"
        start_payload = {
            "transfer_id": tid,
            "filename": "test_sample.bin",
            "filesize": len(original_data),
        }

        self.transfer_mgr.handle_file_start(start_payload, "192.168.100.8")

        # Feed in chunks of 256 KB
        chunk_size = 256 * 1024
        result = None
        for offset in range(0, len(original_data), chunk_size):
            chunk = original_data[offset : offset + chunk_size]
            result = self.transfer_mgr.handle_file_chunk(tid, offset, chunk)

        self.assertIsNotNone(result)
        dest_path = result["filepath"]
        self.assertTrue(os.path.exists(dest_path))

        # Verify content
        with open(dest_path, "rb") as f:
            received_data = f.read()
        self.assertEqual(len(received_data), len(original_data))
        self.assertEqual(received_data, original_data)


if __name__ == "__main__":
    unittest.main()

