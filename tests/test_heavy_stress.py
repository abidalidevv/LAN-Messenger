import os
import time
import tempfile
import asyncio
import unittest
from pathlib import Path

from app.network.connection import PeerConnection
from app.network.transfer import TransferManager
from app.utils.file_helper import compute_file_sha256


class TestHeavyStressAndConcurrency(unittest.TestCase):
    def test_100mb_transfer_and_500_burst_messages(self):
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

            # Start Bob's server on port 9988
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

            server = await asyncio.start_server(handle_client, "127.0.0.1", 9988)

            # Connect Alice
            a_reader, a_writer = await asyncio.open_connection("127.0.0.1", 9988)
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

            # STRESS TEST 1: 500 Rapid Burst Messages
            total_burst_msgs = 500
            t_burst_start = time.time()
            for i in range(total_burst_msgs):
                await alice_conn.send_text(
                    f"Message #{i} - Ultra-rapid stress burst payload"
                )
            await asyncio.sleep(0.5)

            self.assertEqual(len(received_messages), total_burst_msgs)
            burst_duration = time.time() - t_burst_start
            print(
                f"\n[Stress Test 1] 500 Rapid Messages: {burst_duration:.3f}s -> {total_burst_msgs/burst_duration:.1f} msgs/sec (100% delivered, 0 dropped)"
            )

            # STRESS TEST 2: 100 MB Heavy File Transfer (Simulating 4K UHD Video / Large Zip)
            file_size_bytes = 100 * 1024 * 1024  # 100 MB
            stress_file = Path(alice_dir.name) / "ultra_hd_movie_100mb.bin"

            chunk_block = b"Z" * (1024 * 1024)  # 1 MB blocks
            with open(stress_file, "wb") as f:
                for _ in range(100):
                    f.write(chunk_block)

            original_sha256 = compute_file_sha256(str(stress_file))

            t_transfer_start = time.time()
            success = await alice_conn.send_file(str(stress_file))
            self.assertTrue(success)

            for _ in range(300):
                if files_received:
                    break
                await asyncio.sleep(0.05)

            transfer_duration = max(time.time() - t_transfer_start, 0.001)
            throughput = (file_size_bytes / (1024 * 1024)) / transfer_duration
            print(
                f"[Stress Test 2] 100 MB Heavy File Transfer: {transfer_duration:.3f}s -> {throughput:.2f} MB/s (Throughput)"
            )

            self.assertEqual(len(files_received), 1)
            rec_path, rec_name, rec_size = files_received[0]
            self.assertEqual(rec_size, file_size_bytes)

            # SHA256 Integrity Check
            rec_sha256 = compute_file_sha256(rec_path)
            self.assertEqual(
                rec_sha256,
                original_sha256,
                "100 MB File SHA256 checksum mismatch! Data corruption detected.",
            )
            print("[Stress Test 2] SHA256 Integrity: 100% Match (Zero Corruption)")

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

