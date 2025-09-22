import socket
import threading
import time
from datetime import datetime
from queue import Queue, Empty
from logger import Logger, log_session, archive_lock
from config import Config

class Server:
    def __init__(self, name="Server", host="127.0.0.1", port=8000, max_concurrent_clients=5):
        self.name = name
        self.host = host
        self.port = port
        self.logger = Logger(self.name)
        self.running = True

        self.total_clients_today = 0
        self.total_clients_month = 0
        self.total_clients_approached = 0
        self.total_lost_clients = 0
        self.total_rating = 0
        self.rating_count = 0

        self.lock = threading.Lock()
        self.client_queue = Queue()
        self.max_concurrent_clients = max_concurrent_clients
        self.active_clients = 0

    def start(self):
        self.logger.log_info(f"Starting {self.name} on {self.host}:{self.port}")
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as server_socket:
            server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            server_socket.bind((self.host, self.port))
            server_socket.listen(100)
            server_socket.settimeout(1.0)
            self.logger.log_info(f"{self.name} listening on {self.host}:{self.port}")

            threading.Thread(target=self.queue_handler, daemon=True).start()

            while self.running:
                try:
                    client_socket, addr = server_socket.accept()
                    self.logger.log_info(f"Client approached: {addr}")
                    with self.lock:
                        self.total_clients_approached += 1

                    self.client_queue.put((client_socket, addr, time.time()))

                except socket.timeout:
                    continue
                except Exception as e:
                    self.logger.log_error(f"Server error: {e}")

    def queue_handler(self):
        while self.running:
            if self.active_clients < self.max_concurrent_clients:
                try:
                    client_socket, addr, timestamp = self.client_queue.get(timeout=1)
                    wait_time = time.time() - timestamp
                    if wait_time > 300:
                        self.logger.log_warning(f"Client {addr} waited too long. Marked as lost.")
                        with self.lock:
                            self.total_lost_clients += 1
                        client_socket.close()
                        continue

                    threading.Thread(target=self.handle_client, args=(client_socket, addr), daemon=True).start()
                except Empty:
                    continue

    def handle_client(self, sock, addr):
        with self.lock:
            self.active_clients += 1
        try:
            with sock:
                client_name = f"Client-{addr[1]}"
                self.logger.log_info(f"{self.name} serving {client_name}")

                with self.lock:
                    self.total_clients_today += 1
                    self.total_clients_month += 1

                session_log = []

                while True:
                    data = sock.recv(1024)
                    if not data:
                        break

                    message = data.decode()

                    if message.startswith("RATING:"):
                        try:
                            rating = int(message.split(":")[1])
                            with self.lock:
                                self.total_rating += rating
                                self.rating_count += 1

                            self.logger.log_info(f"{client_name} rated {rating}")
                            with archive_lock:
                                log_session(self.name, client_name, rating)
                            session_log.append("\u2B50" * rating)

                        except:
                            self.logger.log_warning(f"Invalid rating from {client_name}")
                        break
                    else:
                        self.logger.log_info(f"{client_name} says: {message}")
                        session_log.append(f"{client_name}: {message}")
                        sock.sendall(f"ECHO: {message}".encode())

        except (ConnectionResetError, BrokenPipeError):
            self.logger.log_error(f"Connection lost with {addr}")
            with self.lock:
                self.total_lost_clients += 1
        except Exception as e:
            self.logger.log_error(f"Error with client {addr}: {e}")
        finally:
            with self.lock:
                self.active_clients -= 1
            self.logger.log_info(f"Client disconnected: {addr}")

    def shutdown(self):
        self.logger.log_info("Shutting down server")
        self.running = False

    def get_metrics(self):
        with self.lock:
            return {
                "server": self.name,
                "total_clients_today": self.total_clients_today,
                "total_clients_month": self.total_clients_month,
                "total_clients_approached": self.total_clients_approached,
                "lost_clients": self.total_lost_clients,
                "average_rating": (self.total_rating / self.rating_count) if self.rating_count > 0 else 0
            }