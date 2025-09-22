import os
import sys
import time
import json
import socket
import argparse
import threading
from datetime import datetime
from concurrent.futures import ThreadPoolExecutor

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from logger import Logger, log_session
from threaded_server import ThreadedServer
from threaded_client import ThreadedClient

LIVE_FILE = "live_threading_metrics.json"

class ThreadedSimulation:
    def __init__(self, num_clients=1000, num_servers=3, duration=300):
        self.num_clients = num_clients
        self.num_servers = num_servers
        self.duration = duration
        self.servers = []
        self.clients = []
        self.logger = Logger("ThreadedSimulation")
        self.start_time = None
        self.end_time = None
        self.metrics = {
            'total_clients_served': 0,
            'total_lost_clients': 0,
            'average_response_time': 0,
            'server_utilization': 0,
            'throughput': 0,
            'max_concurrent_clients': 0,
            'simulation_time': 0,
            'approach': 'threading'
        }
        self.RESULT_FILE = 'threading_simulation_results.json'
        self.live_writer_running = True

    def create_servers(self):
        base_port = 8000
        for i in range(self.num_servers):
            server_name = f"Server_{chr(65 + i)}"
            server = ThreadedServer(server_name, base_port + i, self.num_clients)
            self.servers.append(server)
        self.logger.log_info(f"Created {self.num_servers} threaded servers")

    def create_clients(self):
        for i in range(self.num_clients):
            client_id = f"client_{i:04d}"
            server_port = 8000 + (i % self.num_servers)
            client = ThreadedClient(client_id, server_port)
            self.clients.append(client)
        self.logger.log_info(f"Created {self.num_clients} clients")

    def client_worker(self, client):
        try:
            if client.connect_to_server():
                client.chat_with_server()
                client.provide_rating()
                client.disconnect()
        except Exception as e:
            self.logger.log_error(f"Error in client worker {client.client_id}: {e}")

    def run_live_writer(self):
        while self.live_writer_running:
            try:
                with open(LIVE_FILE, "w") as f:
                    json.dump({"throughput": self.metrics["throughput"]}, f)
                time.sleep(1)
            except Exception as e:
                print(f"[Live Writer Error] {e}")
                break

    def run_simulation(self):
        self.logger.log_info("\U0001F680 Starting threaded simulation")
        self.start_time = time.time()

        self.create_servers()
        self.create_clients()

        server_threads = []
        for server in self.servers:
            thread = threading.Thread(target=server.start_server)
            thread.daemon = True
            thread.start()
            server_threads.append(thread)

        time.sleep(2)

        writer_thread = threading.Thread(target=self.run_live_writer, daemon=True)
        writer_thread.start()

        max_client_threads = 100
        with ThreadPoolExecutor(max_workers=max_client_threads) as executor:
            futures = []
            for client in self.clients:
                if time.time() - self.start_time > self.duration:
                    break
                futures.append(executor.submit(self.client_worker, client))
                time.sleep(0.01)

            for future in futures:
                try:
                    future.result(timeout=30)
                except Exception as e:
                    self.logger.log_error(f"Client thread error: {e}")

        for server in self.servers:
            server.stop_server()

        for thread in server_threads:
            thread.join(timeout=10)

        self.end_time = time.time()
        self.live_writer_running = False
        writer_thread.join()
        self.calculate_metrics()
        self.logger.log_info("\U0001F3AF Threaded simulation completed")

    def calculate_metrics(self):
        total_clients_served = sum(s.clients_served for s in self.servers)
        total_lost_clients = sum(s.lost_clients for s in self.servers)
        total_processing_time = sum(s.stats['total_processing_time'] for s in self.servers)
        max_concurrent_clients = max(s.stats['max_concurrent_clients'] for s in self.servers)
        simulation_time = self.end_time - self.start_time

        self.metrics.update({
            'total_clients_served': total_clients_served,
            'total_lost_clients': total_lost_clients,
            'average_response_time': round(total_processing_time / max(total_clients_served, 1), 4),
            'server_utilization': round((total_processing_time / (simulation_time * self.num_servers)) * 100, 2),
            'throughput': round(total_clients_served / simulation_time, 2),
            'max_concurrent_clients': max_concurrent_clients,
            'simulation_time': round(simulation_time, 2)
        })

        self.logger.log_info(f"Simulation metrics: {self.metrics}")

    def get_results(self):
        return {
            'approach': 'threading',
            'metrics': self.metrics,
            'server_stats': [s.get_stats() for s in self.servers],
            'simulation_time': self.metrics['simulation_time'],
            'total_clients': self.num_clients,
            'total_servers': self.num_servers
        }

def main():
    parser = argparse.ArgumentParser(description='Run threaded server simulation')
    parser.add_argument('--clients', type=int, default=1000)
    parser.add_argument('--servers', type=int, default=3)
    parser.add_argument('--duration', type=int, default=300)

    args = parser.parse_args()
    sim = ThreadedSimulation(args.clients, args.servers, args.duration)

    try:
        sim.run_simulation()
        results = sim.get_results()

        print("\n" + "="*50)
        print("THREADED SIMULATION RESULTS")
        print("="*50)
        print(f"Approach: {results['approach']}")
        print(f"Total clients served: {results['metrics']['total_clients_served']}")
        print(f"Total lost clients: {results['metrics']['total_lost_clients']}")
        print(f"Avg response time: {results['metrics']['average_response_time']:.2f}s")
        print(f"Server utilization: {results['metrics']['server_utilization']:.2f}%")
        print(f"Throughput: {results['metrics']['throughput']:.2f} req/sec")
        print(f"Max concurrent clients: {results['metrics']['max_concurrent_clients']}")
        print(f"Simulation time: {results['metrics']['simulation_time']:.2f}s")

        print("\nServer Breakdown:")
        for s in results['server_stats']:
            print(f"  {s['server_name']}: {s['clients_served']} served, avg rating: {s['average_rating']:.2f}")

        with open(sim.RESULT_FILE, 'w') as f:
            json.dump(results, f, indent=2)

        print(f"\n✅ Results saved to {sim.RESULT_FILE}")

    except KeyboardInterrupt:
        print("\n❌ Interrupted")
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    main()
