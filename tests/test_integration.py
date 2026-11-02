import os
import time
import tempfile
import asyncio
import unittest
from pathlib import Path

from app.network.connection import PeerConnection
from app.network.transfer import TransferManager
from app.utils.file_helper import compute_file_sha256


class TestIntegration(unittest.TestCase):
    def test_two_peer_communication_and_file_transfer(self):
        async def run_scenario():
            alice_dir = tempfile.TemporaryDirectory()
            bob_dir = tempfile.TemporaryDirectory()

            alice_mgr = TransferManager(alice_dir.name)
            bob_mgr = TransferManager(bob_dir.name)

            received_messages = []
            files_received = []

            def bob_on_text(peer_ip, text, ts):
                received_messages.append((peer_ip, text))

            def bob_on_file(peer_ip, filepath, filename, size):
                files_received.append((filepath, filename, size))

            bob_mgr.on_file_received = bob_on_file

            # Start Bob's server on 127.0.0.1:9955
            server_ready = asyncio.Event()
            bob_conn_future = asyncio.get_event_loop().create_future()

            async def handle_alice_client(reader, writer):
                b_conn = PeerConnection(
                    peer_ip="127.0.0.1",
                    reader=reader,
                    writer=writer,
                    local_username="Bob PC",
                    transfer_mgr=bob_mgr,
                    on_text_msg=bob_on_text,
                    on_peer_info=lambda ip, u: None,
                    on_disconnected=lambda ip: None,
                )
                b_conn.start(asyncio.get_event_loop())
                bob_conn_future.set_result(b_conn)

            server = await asyncio.start_server(
                handle_alice_client, "127.0.0.1", 9955
            )

            # Alice connects to Bob
            a_reader, a_writer = await asyncio.open_connection("127.0.0.1", 9955)
            alice_conn = PeerConnection(
                peer_ip="127.0.0.1",
                reader=a_reader,
                writer=a_writer,
                local_username="Alice Laptop",
                transfer_mgr=alice_mgr,
                on_text_msg=lambda ip, t, ts: None,
                on_peer_info=lambda ip, u: None,
                on_disconnected=lambda ip: None,
            )
            alice_conn.start(asyncio.get_event_loop())
            await alice_conn.send_handshake()

            bob_conn = await bob_conn_future

            # 1. Text Message Test
            test_texts = [
                "Hello Bob!",
                "Kese ho bhai?",
                "Sending you high quality file now...",
            ]
            for msg in test_texts:
                await alice_conn.send_text(msg)
                await asyncio.sleep(0.05)

            await asyncio.sleep(0.2)
            self.assertEqual(len(received_messages), 3)
            self.assertEqual(received_messages[0][1], "Hello Bob!")
            self.assertEqual(received_messages[1][1], "Kese ho bhai?")
            self.assertEqual(
                received_messages[2][1], "Sending you high quality file now..."
            )

            # 2. High Speed Binary File Transfer Test (5 MB random payload)
            test_file_size = 5 * 1024 * 1024  # 5 MB
            test_file_path = Path(alice_dir.name) / "sample_video.mp4"
            original_bytes = os.urandom(test_file_size)
            with open(test_file_path, "wb") as f:
                f.write(original_bytes)

            original_sha256 = compute_file_sha256(str(test_file_path))

            t0 = time.time()
            success = await alice_conn.send_file(str(test_file_path))
            self.assertTrue(success)

            # Wait for file reception
            for _ in range(100):
                if files_received:
                    break
                await asyncio.sleep(0.05)

            elapsed = max(time.time() - t0, 0.001)
            mbps = (test_file_size / (1024 * 1024)) / elapsed
            print(f"\n[Benchmark] Transferred 5 MB in {elapsed:.3f}s -> {mbps:.2f} MB/s")

            self.assertEqual(len(files_received), 1)
            received_path, r_name, r_size = files_received[0]
            self.assertEqual(r_name, "sample_video.mp4")
            self.assertEqual(r_size, test_file_size)

            # 3. Checksum Verification
            received_sha256 = compute_file_sha256(received_path)
            self.assertEqual(
                received_sha256,
                original_sha256,
                "SHA256 checksum mismatch! Data corruption detected.",
            )

            # Cleanup
            await alice_conn.close()
            await bob_conn.close()
            server.close()
            await server.wait_closed()
            alice_dir.cleanup()
            bob_dir.cleanup()

        asyncio.run(run_scenario())


if __name__ == "__main__":
    unittest.main()

