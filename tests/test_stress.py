import os
import time
import tempfile
import asyncio
import unittest
from pathlib import Path

from app.network.connection import PeerConnection
from app.network.transfer import TransferManager
from app.utils.file_helper import compute_file_sha256


class TestStressBenchmark(unittest.TestCase):
    def test_50mb_file_and_rapid_messages_stress(self):
        async def run_stress():
            alice_dir = tempfile.TemporaryDirectory()
            bob_dir = tempfile.TemporaryDirectory()

            alice_mgr = TransferManager(alice_dir.name)
            bob_mgr = TransferManager(bob_dir.name)

            received_messages = []
            files_received = []

            def bob_on_text(peer_ip, text, ts):
                received_messages.append(text)

            def bob_on_file(peer_ip, filepath, filename, size):
                files_received.append((filepath, filename, size))

            bob_mgr.on_file_received = bob_on_file

            # Setup server
            bob_conn_future = asyncio.get_event_loop().create_future()

            async def handle_client(reader, writer):
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

            server = await asyncio.start_server(handle_client, "127.0.0.1", 9977)

            # Connect Alice
            a_reader, a_writer = await asyncio.open_connection("127.0.0.1", 9977)
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
            bob_conn = await bob_conn_future

            # 1. Stress Test: 100 rapid sequential messages
            msg_count = 100
            t_msgs_start = time.time()
            for i in range(msg_count):
                await alice_conn.send_text(f"Rapid packet #{i} - ultra speed test")
            await asyncio.sleep(0.3)

            self.assertEqual(len(received_messages), msg_count)
            print(
                f"\n[Stress] 100 rapid messages received in {time.time() - t_msgs_start:.3f}s (100% delivered)"
            )

            # 2. Stress Test: 50 MB Large File Transfer (Simulating 4K HD Video Clip)
            file_size_bytes = 50 * 1024 * 1024  # 50 MB
            stress_file = Path(alice_dir.name) / "4k_sample_video.mp4"
            # Write 50MB in chunks to avoid high RAM spike during test setup
            with open(stress_file, "wb") as f:
                chunk = b"H" * (1024 * 1024)  # 1MB
                for _ in range(50):
                    f.write(chunk)

            expected_sha256 = compute_file_sha256(str(stress_file))

            t_transfer_start = time.time()
            success = await alice_conn.send_file(str(stress_file))
            self.assertTrue(success)

            # Wait for transfer completion
            for _ in range(200):
                if files_received:
                    break
                await asyncio.sleep(0.05)

            transfer_duration = max(time.time() - t_transfer_start, 0.001)
            throughput = (file_size_bytes / (1024 * 1024)) / transfer_duration
            print(
                f"[Stress] 50 MB File transferred in {transfer_duration:.3f}s -> {throughput:.2f} MB/s"
            )

            self.assertEqual(len(files_received), 1)
            rec_path, rec_name, rec_size = files_received[0]
            self.assertEqual(rec_size, file_size_bytes)

            # Verify integrity
            rec_sha256 = compute_file_sha256(rec_path)
            self.assertEqual(
                rec_sha256,
                expected_sha256,
                "50 MB File SHA256 checksum mismatch! Data corruption.",
            )

            # Cleanup
            await alice_conn.close()
            await bob_conn.close()
            server.close()
            await server.wait_closed()
            alice_dir.cleanup()
            bob_dir.cleanup()

        asyncio.run(run_stress())


if __name__ == "__main__":
    unittest.main()

