import socket
import select
import threading
import subprocess
import sys

DNS_MAP = {
    "github.com": "20.207.73.82",
    "api.github.com": "20.207.73.85",
}

def resolve_host(host):
    if host in DNS_MAP:
        return DNS_MAP[host]
    try:
        return socket.gethostbyname(host)
    except Exception:
        return host

def handle_client(client_sock):
    try:
        req = client_sock.recv(4096).decode('latin1', errors='ignore')
        first_line = req.split('\r\n')[0]
        method, target, _ = first_line.split()

        if method == "CONNECT":
            host, port = target.split(":")
            port = int(port)
            remote_ip = resolve_host(host)

            remote_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            remote_sock.connect((remote_ip, port))

            client_sock.sendall(b"HTTP/1.1 200 Connection Established\r\n\r\n")

            sockets = [client_sock, remote_sock]
            while True:
                r, _, _ = select.select(sockets, [], [], 30)
                if not r:
                    break
                for s in r:
                    data = s.recv(16384)
                    if not data:
                        return
                    if s is client_sock:
                        remote_sock.sendall(data)
                    else:
                        client_sock.sendall(data)
    except Exception:
        pass
    finally:
        try:
            client_sock.close()
        except Exception:
            pass

def run_proxy(server_sock):
    server_sock.listen(10)
    while True:
        try:
            client, _ = server_sock.accept()
            threading.Thread(target=handle_client, args=(client,), daemon=True).start()
        except Exception:
            break

def main():
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.bind(('127.0.0.1', 0))
    port = server.getsockname()[1]
    
    t = threading.Thread(target=run_proxy, args=(server,), daemon=True)
    t.start()
    
    proxy_url = f"http://127.0.0.1:{port}"
    print(f"Proxy started on {proxy_url}. Running git push...")

    cmd = ["git", "-c", f"http.proxy={proxy_url}", "push", "origin", "main"]
    ret = subprocess.run(cmd)
    
    server.close()
    sys.exit(ret.returncode)

if __name__ == '__main__':
    main()
