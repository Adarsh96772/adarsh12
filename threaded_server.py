# threaded_server.py

import socket
import threading
import time

class ThreadedServer:
    def __init__(self, name, port, max_clients):
        self.name = name
        self.port = port
        self.max_clients = max_clients
        self.running = False
        self.clients_served = 0
        self.lost_clients = 0
        self.stats = {
            "total_processing_time": 0,
            "max_concurrent_clients": 0
        }

    def start_server(self):
        self.running = True
        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.server_socket.bind(("127.0.0.1", self.port))
        self.server_socket.listen(100)

        print(f"{self.name} started on port {self.port}")
        while self.running:
            try:
                self.server_socket.settimeout(1.0)
                client_sock, addr = self.server_socket.accept()
                thread = threading.Thread(target=self.handle_client, args=(client_sock,))
                thread.daemon = True
                thread.start()
            except socket.timeout:
                continue
            except Exception:
                break

    def handle_client(self, client_sock):
        start = time.time()
        try:
            data = client_sock.recv(1024)
            if data:
                msg = data.decode()
                client_sock.sendall(f"Hello from {self.name}".encode())
                self.clients_served += 1
        except:
            self.lost_clients += 1
        finally:
            client_sock.close()
            self.stats["total_processing_time"] += (time.time() - start)

    def stop_server(self):
        self.running = False
        try:
            self.server_socket.close()
        except:
            pass

    def get_stats(self):
        return {
            "server_name": self.name,
            "clients_served": self.clients_served,
            "average_rating": 3.5  # stubbed
        }