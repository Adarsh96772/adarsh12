import threading
from queue import Queue
from server import Server
from config import Config
from logger import log_info, log_error, log_server_status
from database import DatabaseManager

class ServerPool:
    def __init__(self, num_servers=None, server_names=None):
        self.num_servers = num_servers or Config.NUM_SERVERS
        self.server_names = server_names or Config.SERVER_NAMES
        self.servers = []
        self.client_queue = Queue()
        self.lock = threading.Lock()
        self.db_manager = DatabaseManager()
        self.running = False
        self.server_threads = []
        
        # Initialize servers
        for i in range(self.num_servers):
            server_name = self.server_names[i] if i < len(self.server_names) else f"Server {i+1}"
            server = Server(server_name)
            self.servers.append(server)
        
        log_info(f"Initialized server pool with {self.num_servers} servers")
    
    def start_servers(self):
        """Start all servers in separate threads"""
        with self.lock:
            if self.running:
                log_warning("Server pool already running")
                return
            
            self.running = True
            
            for server in self.servers:
                thread = threading.Thread(target=server.serve, args=(self.client_queue,))
                thread.daemon = True
                thread.start()
                self.server_threads.append(thread)
                log_server_status(server.name, "STARTED")
        
        log_info("All servers started")
    
    def stop_servers(self):
        """Stop all servers"""
        with self.lock:
            if not self.running:
                log_warning("Server pool not running")
                return
            
            self.running = False
            
            # Add poison pills to stop servers
            for _ in self.servers:
                self.client_queue.put(None)
        
        log_info("All servers stopped")
    
    def add_client(self, client):
        """Add a client to the queue"""
        if not self.running:
            log_error("Cannot add client - server pool not running")
            return False
        
        self.client_queue.put(client)
        log_info(f"Client {client.name} added to queue")
        return True
    
    def get_server_status(self):
        """Get status of all servers"""
        status = []
        for server in self.servers:
            with server.lock:
                server_info = {
                    "name": server.name,
                    "daily_count": server.daily_count,
                    "monthly_count": server.monthly_count,
                    "total_clients": server.total_clients,
                    "lost_clients": server.lost_clients,
                    "average_rating": server.average_rating(),
                    "current_client": server.current_client.name if server.current_client else None,
                    "status": "BUSY" if server.current_client else "IDLE"
                }
                status.append(server_info)
                
                # Save to database
                self.db_manager.insert_server_metrics(
                    server.name, server.daily_count, server.monthly_count,
                    server.total_clients, server.lost_clients, server.rating_sum,
                    server.rating_count, server.current_client.name if server.current_client else None
                )
        
        return status
    
    def get_pool_statistics(self):
        """Get overall pool statistics"""
        total_clients = sum(server.total_clients for server in self.servers)
        total_lost = sum(server.lost_clients for server in self.servers)
        total_rating_sum = sum(server.rating_sum for server in self.servers)
        total_rating_count = sum(server.rating_count for server in self.servers)
        
        avg_rating = total_rating_sum / total_rating_count if total_rating_count > 0 else 0
        
        return {
            "total_servers": self.num_servers,
            "total_clients_served": total_clients,
            "total_lost_clients": total_lost,
            "overall_average_rating": round(avg_rating, 2),
            "queue_size": self.client_queue.qsize(),
            "active_servers": sum(1 for server in self.servers if server.current_client is not None)
        }
    
    def reset_daily_counts(self):
        """Reset daily counts for all servers"""
        for server in self.servers:
            with server.lock:
                server.daily_count = 0
        log_info("Daily counts reset for all servers")
    
    def reset_monthly_counts(self):
        """Reset monthly counts for all servers"""
        for server in self.servers:
            with server.lock:
                server.monthly_count = 0
        log_info("Monthly counts reset for all servers")
    
    def get_available_servers(self):
        """Get list of available (not busy) servers"""
        available = []
        for server in self.servers:
            if server.current_client is None:
                available.append(server)
        return available
    
    def get_busy_servers(self):
        """Get list of busy servers"""
        busy = []
        for server in self.servers:
            if server.current_client is not None:
                busy.append(server)
        return busy
    
    def wait_for_completion(self):
        """Wait for all server threads to complete"""
        for thread in self.server_threads:
            thread.join()
        log_info("All server threads completed")
    
    def is_running(self):
        """Check if server pool is running"""
        return self.running
    
    def get_queue_size(self):
        """Get current queue size"""
        return self.client_queue.qsize()