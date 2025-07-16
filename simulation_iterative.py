import socket
import time
import json
import threading
from datetime import datetime
import logging

# Configuration
NUM_CLIENTS = 100
NUM_SERVERS = 3
SIMULATION_DURATION = 60
SERVER_PORTS = [8000 + i for i in range(NUM_SERVERS)]
SERVER_NAMES = [f"Server_{chr(65+i)}" for i in range(NUM_SERVERS)]
RESULT_FILE = "iterative_simulation_results.json"

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(message)s')
logger = logging.getLogger("IterativeSimulation")

metrics_lock = threading.Lock()
metrics = {
    "total_clients_served": 0,
    "total_lost_clients": 0,
    "average_response_time": 0.0,
    "server_utilization": 0.0,
    "throughput": 0.0,
    "simulation_time": 0.0,
    "approach": "iterative"
}

server_stats_lock = threading.Lock()
server_stats = {
    name: {
        "clients_served": 0,
        "lost_clients": 0,
        "ratings": [],
        "current_client": None
    } for name in SERVER_NAMES
}

active_servers = []
waiting_queue = []
queue_lock = threading.Lock()
MAX_WAIT_SECONDS = 5

# Live Metrics

def write_live_metrics():
    with open(RESULT_FILE, "w") as f:
        json.dump({"metrics": {"throughput": metrics.get("throughput", 0.0)}}, f)

def periodic_writer(client_threads):
    while True:
        time.sleep(1)
        with metrics_lock:
            write_live_metrics()
        if not any(t.is_alive() for t in client_threads):
            break

class TestServer:
    def __init__(self, name, port):
        self.name = name
        self.port = port
        self.socket = None
        self.running = False

    def start(self):
        try:
            self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            self.socket.bind(("127.0.0.1", self.port))
            self.socket.listen(50)
            self.running = True
            logger.info(f"🚀 {self.name} started on port {self.port}")

            while self.running:
                try:
                    self.socket.settimeout(1)
                    client_socket, _ = self.socket.accept()
                    threading.Thread(target=self.handle_client, args=(client_socket,), daemon=True).start()
                except socket.timeout:
                    continue
        except Exception as e:
            logger.error(f"❌ {self.name} failed to start: {e}")

    def handle_client(self, client_socket):
        try:
            client_socket.settimeout(5)
            data = client_socket.recv(1024)
            if data:
                message = json.loads(data.decode())
                time.sleep(0.01)
                response = {
                    "type": "response",
                    "message": f"Echo from {self.name}: {message.get('message', '')}",
                    "timestamp": datetime.now().isoformat(),
                    "server": self.name
                }
                client_socket.sendall(json.dumps(response).encode())
        except Exception as e:
            logger.warning(f"⚠️ Error handling client: {e}")
        finally:
            try:
                client_socket.close()
            except:
                pass

    def stop(self):
        self.running = False
        if self.socket:
            try:
                self.socket.close()
            except:
                pass

def start_servers():
    threads = []
    for i in range(NUM_SERVERS):
        server = TestServer(SERVER_NAMES[i], SERVER_PORTS[i])
        active_servers.append(server)
        t = threading.Thread(target=server.start, daemon=True)
        t.start()
        threads.append(t)
    return threads

def client_simulation(client_id, sim_start):
    start_wait = time.time()
    assigned = False
    while not assigned and (time.time() - start_wait < MAX_WAIT_SECONDS):
        server_index = client_id % NUM_SERVERS
        port = SERVER_PORTS[server_index]
        server_name = SERVER_NAMES[server_index]
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(3)
            sock.connect(("127.0.0.1", port))
            message = {
                "type": "chat",
                "message": f"Hello from client {client_id}",
                "timestamp": datetime.now().isoformat()
            }
            msg_start = time.time()
            sock.sendall(json.dumps(message).encode())
            response_data = sock.recv(1024)
            msg_end = time.time()

            if response_data:
                response_time = msg_end - msg_start
                with metrics_lock:
                    metrics["average_response_time"] += response_time
                    metrics["total_clients_served"] += 1
                with server_stats_lock:
                    server_stats[server_name]["clients_served"] += 1
                    server_stats[server_name]["ratings"].append(1 + (client_id % 5))
                assigned = True

            sock.close()
            break

        except Exception as e:
            time.sleep(0.3)  # wait before retry

    if not assigned:
        logger.warning(f"❌ Client {client_id} timed out after waiting")
        with metrics_lock:
            metrics["total_lost_clients"] += 1
        with server_stats_lock:
            server_stats[server_name]["lost_clients"] += 1

def cleanup_servers():
    for server in active_servers:
        server.stop()

def run_simulation():
    logger.info("🚀 Starting iterative simulation...")
    start_servers()
    time.sleep(2)
    sim_start = time.time()
    client_threads = []

    for i in range(NUM_CLIENTS):
        t = threading.Thread(target=client_simulation, args=(i, sim_start))
        t.start()
        client_threads.append(t)
        if i % 10 == 0:
            time.sleep(0.1)

    writer_thread = threading.Thread(target=periodic_writer, args=(client_threads,), daemon=True)
    writer_thread.start()

    for t in client_threads:
        t.join(timeout=30)
    writer_thread.join()

    sim_end = time.time()
    sim_time = sim_end - sim_start

    with metrics_lock:
        metrics["simulation_time"] = sim_time
        total = max(metrics["total_clients_served"], 1)
        metrics["average_response_time"] = round(metrics["average_response_time"] / total, 4)
        metrics["throughput"] = round(metrics["total_clients_served"] / sim_time, 2)
        metrics["server_utilization"] = 100.0

    result = {
        "approach": "iterative",
        "metrics": metrics.copy(),
        "server_stats": [],
        "simulation_time": sim_time,
        "total_clients": NUM_CLIENTS,
        "total_servers": NUM_SERVERS
    }

    with server_stats_lock:
        for name in SERVER_NAMES:
            stat = server_stats[name]
            avg_rating = round(sum(stat["ratings"]) / len(stat["ratings"]) if stat["ratings"] else 0.0, 1)
            result["server_stats"].append({
                "server_name": name,
                "clients_served": stat["clients_served"],
                "lost_clients": stat["lost_clients"],
                "average_rating": avg_rating
            })

    with open(RESULT_FILE, 'w') as f:
        json.dump(result, f, indent=2)

    logger.info(f"✅ Simulation completed. Results written to {RESULT_FILE}")
    cleanup_servers()

if __name__ == "__main__":
    run_simulation()
