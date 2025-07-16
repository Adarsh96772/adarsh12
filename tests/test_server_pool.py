import unittest
import threading
import time
import socket
from unittest.mock import Mock, patch, MagicMock
import sys
import os

# Add the parent directory to the path to import project modules
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from server_pool import ServerPool
from server import ChatServer
from config import Config


class TestServerPool(unittest.TestCase):
    """Test suite for ServerPool class"""
    
    def setUp(self):
        """Set up test fixtures before each test method"""
        self.pool_size = 3
        self.base_port = 8000
        self.server_pool = ServerPool(self.pool_size, self.base_port)
        
    def tearDown(self):
        """Clean up after each test method"""
        if hasattr(self, 'server_pool'):
            self.server_pool.shutdown()
            
    def test_initialization(self):
        """Test ServerPool initialization"""
        self.assertEqual(len(self.server_pool.servers), self.pool_size)
        self.assertEqual(self.server_pool.base_port, self.base_port)
        self.assertEqual(self.server_pool.current_index, 0)
        
    def test_server_creation(self):
        """Test that servers are created with correct ports"""
        for i, server in enumerate(self.server_pool.servers):
            expected_port = self.base_port + i
            self.assertEqual(server.port, expected_port)
            
    def test_get_next_server(self):
        """Test round-robin server selection"""
        # Test round-robin behavior
        first_server = self.server_pool.get_next_server()
        second_server = self.server_pool.get_next_server()
        third_server = self.server_pool.get_next_server()
        fourth_server = self.server_pool.get_next_server()
        
        # Should cycle back to first server
        self.assertEqual(first_server, fourth_server)
        self.assertNotEqual(first_server, second_server)
        self.assertNotEqual(second_server, third_server)
        
    def test_start_all_servers(self):
        """Test starting all servers in the pool"""
        with patch.object(ChatServer, 'start') as mock_start:
            self.server_pool.start_all()
            
            # Verify all servers were started
            self.assertEqual(mock_start.call_count, self.pool_size)
            
    def test_stop_all_servers(self):
        """Test stopping all servers in the pool"""
        with patch.object(ChatServer, 'stop') as mock_stop:
            self.server_pool.stop_all()
            
            # Verify all servers were stopped
            self.assertEqual(mock_stop.call_count, self.pool_size)
            
    def test_get_server_status(self):
        """Test getting status of all servers"""
        with patch.object(ChatServer, 'is_running', return_value=True):
            status = self.server_pool.get_server_status()
            
            self.assertEqual(len(status), self.pool_size)
            for server_status in status:
                self.assertIn('port', server_status)
                self.assertIn('status', server_status)
                self.assertIn('client_count', server_status)
                
    def test_get_total_clients(self):
        """Test getting total client count across all servers"""
        with patch.object(ChatServer, 'get_client_count', return_value=5):
            total_clients = self.server_pool.get_total_clients()
            self.assertEqual(total_clients, self.pool_size * 5)
            
    def test_find_least_loaded_server(self):
        """Test finding the server with the least load"""
        # Mock different client counts for each server
        client_counts = [10, 5, 15]
        
        def mock_get_client_count(server_index):
            return client_counts[server_index]
            
        with patch.object(ChatServer, 'get_client_count', side_effect=lambda: mock_get_client_count(0)):
            self.server_pool.servers[0].get_client_count = lambda: 10
            self.server_pool.servers[1].get_client_count = lambda: 5
            self.server_pool.servers[2].get_client_count = lambda: 15
            
            least_loaded = self.server_pool.find_least_loaded_server()
            self.assertEqual(least_loaded, self.server_pool.servers[1])
            
    def test_shutdown(self):
        """Test graceful shutdown of the server pool"""
        with patch.object(ChatServer, 'stop') as mock_stop:
            self.server_pool.shutdown()
            
            # Verify all servers were stopped
            self.assertEqual(mock_stop.call_count, self.pool_size)
            
    def test_health_check(self):
        """Test health check functionality"""
        with patch.object(ChatServer, 'is_running', return_value=True):
            health_status = self.server_pool.health_check()
            
            self.assertIn('healthy_servers', health_status)
            self.assertIn('unhealthy_servers', health_status)
            self.assertIn('total_servers', health_status)
            self.assertEqual(health_status['total_servers'], self.pool_size)
            
    def test_restart_server(self):
        """Test restarting a specific server"""
        server_index = 1
        
        with patch.object(ChatServer, 'stop') as mock_stop, \
             patch.object(ChatServer, 'start') as mock_start:
            
            self.server_pool.restart_server(server_index)
            
            # Verify server was stopped and started
            mock_stop.assert_called_once()
            mock_start.assert_called_once()
            
    def test_concurrent_access(self):
        """Test thread safety of server pool operations"""
        results = []
        
        def get_server_worker():
            for _ in range(10):
                server = self.server_pool.get_next_server()
                results.append(server)
                time.sleep(0.01)
                
        # Create multiple threads accessing the pool
        threads = []
        for _ in range(5):
            thread = threading.Thread(target=get_server_worker)
            threads.append(thread)
            thread.start()
            
        # Wait for all threads to complete
        for thread in threads:
            thread.join()
            
        # Verify we got the expected number of results
        self.assertEqual(len(results), 50)
        
    def test_load_balancing(self):
        """Test load balancing across servers"""
        # Mock different loads for testing
        with patch.object(ChatServer, 'get_client_count', side_effect=[2, 5, 1]):
            server = self.server_pool.get_least_loaded_server()
            # Should return server with index 2 (client count = 1)
            self.assertEqual(server, self.server_pool.servers[2])
            
    def test_server_failure_handling(self):
        """Test handling of server failures"""
        # Mock a server failure
        with patch.object(ChatServer, 'is_running', side_effect=[False, True, True]):
            failed_servers = self.server_pool.get_failed_servers()
            self.assertEqual(len(failed_servers), 1)
            self.assertEqual(failed_servers[0], self.server_pool.servers[0])
            
    def test_metrics_collection(self):
        """Test collection of pool metrics"""
        with patch.object(ChatServer, 'get_metrics') as mock_metrics:
            mock_metrics.return_value = {
                'messages_processed': 100,
                'uptime': 3600,
                'memory_usage': 50.5
            }
            
            pool_metrics = self.server_pool.get_pool_metrics()
            
            self.assertIn('total_messages_processed', pool_metrics)
            self.assertIn('average_uptime', pool_metrics)
            self.assertIn('total_memory_usage', pool_metrics)
            self.assertIn('server_count', pool_metrics)


class TestServerPoolIntegration(unittest.TestCase):
    """Integration tests for ServerPool"""
    
    def setUp(self):
        """Set up integration test fixtures"""
        self.pool_size = 2
        self.base_port = 9000
        
    def test_full_lifecycle(self):
        """Test complete server pool lifecycle"""
        # Create pool
        pool = ServerPool(self.pool_size, self.base_port)
        
        try:
            # Test server creation
            self.assertEqual(len(pool.servers), self.pool_size)
            
            # Test server selection
            server1 = pool.get_next_server()
            server2 = pool.get_next_server()
            server3 = pool.get_next_server()  # Should cycle back to first
            
            self.assertEqual(server1, server3)
            self.assertNotEqual(server1, server2)
            
        finally:
            # Clean up
            pool.shutdown()
            
    def test_concurrent_operations(self):
        """Test concurrent pool operations"""
        pool = ServerPool(self.pool_size, self.base_port)
        
        try:
            # Test concurrent server access
            servers = []
            
            def worker():
                for _ in range(10):
                    server = pool.get_next_server()
                    servers.append(server)
                    
            threads = [threading.Thread(target=worker) for _ in range(3)]
            
            for thread in threads:
                thread.start()
                
            for thread in threads:
                thread.join()
                
            # Verify all operations completed
            self.assertEqual(len(servers), 30)
            
        finally:
            pool.shutdown()


if __name__ == '__main__':
    # Run tests with verbose output
    unittest.main(verbosity=2)