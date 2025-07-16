# iterative_server.py

import time
from utils import generate_rating
from logger import log_session

class IterativeServer:
    def __init__(self, name):
        self.name = name
        self.clients_served = 0
        self.total_rating = 0
        self.total_clients = 0
        self.lost_clients = 0
        self.current_client = None

    def serve_client(self, client, max_wait_time=300):
        self.total_clients += 1

        if client.get('wait_time', 0) > max_wait_time:
            self.lost_clients += 1
            log_session(self.name, client['name'], None, lost=True)
            print(f"[{self.name}] LOST client {client['name']} (waited too long)")
            return

        self.current_client = client['name']
        print(f"[{self.name}] Serving {client['name']}...")
        time.sleep(client.get('chat_duration', 2))  # simulate chat duration

        rating = generate_rating()
        self.clients_served += 1
        self.total_rating += rating

        log_session(self.name, client['name'], rating)
        print(f"[{self.name}] Finished {client['name']} with rating {rating}")
        self.current_client = None

    def average_rating(self):
        if self.clients_served == 0:
            return 0.0
        return round(self.total_rating / self.clients_served, 2)

    def stats(self):
        return {
            'server_name': self.name,
            'clients_served': self.clients_served,
            'total_clients': self.total_clients,
            'lost_clients': self.lost_clients,
            'average_rating': self.average_rating(),
            'current_client': self.current_client or "None"
        }


class IterativeClient:
    def __init__(self, client_dict):
        self.name = client_dict['name']
        self.chat_duration = client_dict.get('chat_duration', 2)
        self.wait_time = client_dict.get('wait_time', 0)

    def to_dict(self):
        return {
            'name': self.name,
            'chat_duration': self.chat_duration,
            'wait_time': self.wait_time
        }