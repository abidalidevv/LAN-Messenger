import socket
import json
import time
import asyncio
from typing import Dict, Any, List, Set, Callable, Optional


def get_local_ip_addresses() -> List[str]:
    """Retrieves all non-loopback IPv4 addresses assigned to this PC."""
    ip_list = []
    try:
        hostname = socket.gethostname()
        for info in socket.getaddrinfo(hostname, None):
            ip = info[4][0]
            if ":" not in ip and not ip.startswith("127.") and ip not in ip_list:
                ip_list.append(ip)
    except Exception as e:
        print(f"Error enumerating local IPs: {e}")

    # Fallback method: connect dummy socket to router/external
    if not ip_list:
        try:
            s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            s.connect(("192.168.100.1", 80))
            ip = s.getsockname()[0]
            s.close()
            if ip not in ip_list:
                ip_list.append(ip)
        except Exception:
            pass

    return ip_list or ["127.0.0.1"]


def get_broadcast_addresses(custom_subnets: Optional[List[str]] = None) -> List[str]:
    """
    Computes broadcast addresses for all active network interfaces,
    plus directed broadcast addresses for dual-subnets (192.168.100.255 and 192.168.7.255).
    """
    addresses = {"255.255.255.255"}

    # Include common subnets specified in user config
    default_subnets = ["192.168.100", "192.168.7"]
    all_subnets = set(default_subnets)
    if custom_subnets:
        all_subnets.update(custom_subnets)

    for sub in all_subnets:
        addresses.add(f"{sub}.255")

    # Compute broadcast based on active local IPs
    for ip in get_local_ip_addresses():
        parts = ip.split(".")
        if len(parts) == 4:
            addresses.add(f"{parts[0]}.{parts[1]}.{parts[2]}.255")

    return list(addresses)


class PeerDiscovery:
    def __init__(
        self,
        username: str,
        tcp_port: int,
        udp_port: int = 9877,
        custom_subnets: Optional[List[str]] = None,
        on_peer_found: Optional[Callable[[Dict[str, Any]], None]] = None,
        on_peer_lost: Optional[Callable[[str], None]] = None,
    ):
        self.username = username
        self.tcp_port = tcp_port
        self.udp_port = udp_port
        self.custom_subnets = custom_subnets or ["192.168.100", "192.168.7"]
        self.on_peer_found = on_peer_found
        self.on_peer_lost = on_peer_lost

        self.peers: Dict[str, Dict[str, Any]] = {}  # ip -> peer_info
        self._running = False
        self._udp_socket: Optional[socket.socket] = None
        self._loop: Optional[asyncio.AbstractEventLoop] = None
        self._broadcast_task: Optional[asyncio.Task] = None
        self._listen_task: Optional[asyncio.Task] = None
        self._cleanup_task: Optional[asyncio.Task] = None

    def start(self, loop: asyncio.AbstractEventLoop):
        self._loop = loop
        self._running = True

        try:
            self._udp_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            self._udp_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            self._udp_socket.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
            self._udp_socket.bind(("", self.udp_port))
            self._udp_socket.setblocking(False)
        except Exception as e:
            print(f"Warning: could not bind UDP discovery socket: {e}")
            self._udp_socket = None

        self._broadcast_task = self._loop.create_task(self._broadcast_loop())
        if self._udp_socket:
            self._listen_task = self._loop.create_task(self._listen_loop())
        self._cleanup_task = self._loop.create_task(self._cleanup_loop())

    def stop(self):
        self._running = False
        if self._broadcast_task:
            self._broadcast_task.cancel()
        if self._listen_task:
            self._listen_task.cancel()
        if self._cleanup_task:
            self._cleanup_task.cancel()
        if self._udp_socket:
            try:
                self._udp_socket.close()
            except Exception:
                pass
            self._udp_socket = None

    async def _broadcast_loop(self):
        """Sends UDP presence beacons periodically to all broadcast addresses."""
        while self._running:
            try:
                local_ips = get_local_ip_addresses()
                my_ip = local_ips[0] if local_ips else "127.0.0.1"

                payload = json.dumps(
                    {
                        "type": "lan_beacon",
                        "username": self.username,
                        "ip": my_ip,
                        "all_ips": local_ips,
                        "port": self.tcp_port,
                        "hostname": socket.gethostname(),
                    }
                ).encode("utf-8")

                targets = get_broadcast_addresses(self.custom_subnets)
                sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
                sock.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
                sock.setblocking(False)

                for bcast_ip in targets:
                    try:
                        sock.sendto(payload, (bcast_ip, self.udp_port))
                    except Exception:
                        pass
                sock.close()
            except Exception as e:
                print(f"Broadcast error: {e}")

            await asyncio.sleep(4.0)

    async def _listen_loop(self):
        """Listens for UDP presence beacons from peers on the LAN."""
        while self._running and self._udp_socket:
            try:
                data, addr = await self._loop.sock_recvfrom(self._udp_socket, 2048)
                msg = json.loads(data.decode("utf-8"))
                if msg.get("type") == "lan_beacon":
                    sender_ip = addr[0]
                    # Ignore self-beacons
                    local_ips = get_local_ip_addresses()
                    if sender_ip in local_ips and msg.get("port") == self.tcp_port:
                        continue

                    self.record_peer(
                        ip=sender_ip,
                        username=msg.get("username", "Unknown"),
                        port=msg.get("port", self.tcp_port),
                        hostname=msg.get("hostname", ""),
                    )
            except asyncio.CancelledError:
                break
            except Exception as e:
                await asyncio.sleep(0.5)

    def record_peer(self, ip: str, username: str, port: int, hostname: str = ""):
        """Adds or updates a peer in the registry and triggers callback."""
        is_new = ip not in self.peers
        peer_data = {
            "ip": ip,
            "username": username,
            "port": port,
            "hostname": hostname,
            "last_seen": time.time(),
            "status": "online",
        }
        self.peers[ip] = peer_data
        if self.on_peer_found:
            self.on_peer_found(peer_data)

    async def _cleanup_loop(self):
        """Marks peers offline if not seen for 16 seconds."""
        while self._running:
            try:
                now = time.time()
                lost = []
                for ip, info in list(self.peers.items()):
                    if now - info["last_seen"] > 16.0:
                        if info["status"] == "online":
                            info["status"] = "offline"
                            lost.append(ip)

                for ip in lost:
                    if self.on_peer_lost:
                        self.on_peer_lost(ip)
            except Exception as e:
                print(f"Cleanup error: {e}")

            await asyncio.sleep(5.0)

    async def fast_sweep_subnets(
        self, subnets: Optional[List[str]] = None, timeout: float = 0.25
    ) -> List[Dict[str, Any]]:
        """
        Rapidly sweeps all IPs in target subnets to find online peers
        bypassing any UDP broadcast or router filtering.
        Scans ~500 IPs in ~1.5 seconds using asyncio.
        """
        target_subnets = subnets or self.custom_subnets
        local_ips = get_local_ip_addresses()
        found_peers = []

        semaphore = asyncio.Semaphore(60)  # max concurrent socket attempts

        async def probe_ip(ip_str: str):
            if ip_str in local_ips:
                return
            async with semaphore:
                try:
                    conn = asyncio.open_connection(ip_str, self.tcp_port)
                    reader, writer = await asyncio.wait_for(conn, timeout=timeout)
                    writer.close()
                    await writer.wait_closed()
                    # Port is open! Record peer
                    peer_info = {
                        "ip": ip_str,
                        "username": f"Peer @ {ip_str}",
                        "port": self.tcp_port,
                        "last_seen": time.time(),
                        "status": "online",
                    }
                    found_peers.append(peer_info)
                    self.record_peer(ip_str, peer_info["username"], self.tcp_port)
                except Exception:
                    pass

        tasks = []
        for subnet in target_subnets:
            for host_idx in range(1, 255):
                target_ip = f"{subnet}.{host_idx}"
                tasks.append(probe_ip(target_ip))

        await asyncio.gather(*tasks, return_exceptions=True)
        return found_peers

