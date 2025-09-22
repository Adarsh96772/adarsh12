# threaded_client.py

import socket
import time

class ThreadedClient:
    def __init__(self, client_id, server_port):
        self.client_id = client_id
        self.server_port = server_port

    def connect_to_server(self):
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        try:
            self.sock.connect(("127.0.0.1", self.server_port))
            return True
        except Exception as e:
            return False

    def chat_with_server(self):
        try:
            message = f"Hello from {self.client_id}"
            self.sock.sendall(message.encode())
            data = self.sock.recv(1024)
            return data
        except:
            return None

    def provide_rating(self):
        pass  # stubbed

    def disconnect(self):
        try:
            self.sock.close()
        except:
            pass