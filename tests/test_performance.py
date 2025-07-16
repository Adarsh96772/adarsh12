import unittest
import time
import threading
import socket
import json
from unittest.mock import Mock, patch
import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from performance_monitor import PerformanceMonitor
from metrics_collector import MetricsCollector
from database import Database
from logger import Logger
from utils import ThreadSafeCounter, RateLimiter, calculate_response_time

class TestPerformanceMonitor(unittest.TestCase):
    """Test cases for performance monitoring."""
    
    def setUp(self):
        self.mock_db = Mock(spec=Database)
        self.mock_logger = Mock(spec=Logger)
        self.performance_monitor = PerformanceMonitor(self.mock_db, self.mock_logger)
    
    def test_response_time_calculation(self):
        """Test response time calculation."""
        start_time = time.time()
        time.sleep(0.1)  # 100ms
        response_time = calculate_response_time(start_time)
        
        self.assertGreaterEqual(response_time, 100)
        self.assertLessEqual(response_time, 150)  # Allow some tolerance
    
    def test_performance_monitor_initialization(self):
        """Test performance monitor initialization."""
        self.assertIsNotNone(self.performance_monitor)
        self.assertEqual(self.performance_monitor.db, self.mock_db)
        self.assertEqual(self.performance_monitor.logger, self.mock_logger)
    
    def test_concurrent_monitoring(self):
        """Test performance monitoring under concurrent load."""
        results = []
        
        def monitor_task():
            start_time = time.time()
            time.sleep(0.05)  # Simulate work
            response_time = calculate_response_time(start_time)
            results.append(response_time)
        
        threads = []
        for i in range(10):
            thread = threading.Thread(target=monitor_task)
            threads.append(thread)
            thread.start()
        
        for thread in threads:
            thread.join()
        
        self.assertEqual(len(results), 10)
        self.assertTrue(all(r >= 50 for r in results))

class TestMetricsCollector(unittest.TestCase):
    """Test cases for metrics collection."""
    
    def setUp(self):
        self.mock_db = Mock(spec=Database)
        self.mock_logger = Mock(spec=Logger)
        self.metrics_collector = MetricsCollector(self.mock_db, self.mock_logger)
    
    def test_counter_operations(self):
        """Test thread-safe counter operations."""
        counter = ThreadSafeCounter()
        
        # Test increment
        result = counter.increment()
        self.assertEqual(result, 1)
        
        # Test decrement
        result = counter.decrement()
        self.assertEqual(result, 0)
        
        # Test get_value
        self.assertEqual(counter.get_value(), 0)
    
    def test_concurrent_counter_operations(self):
        """Test counter under concurrent access."""
        counter = ThreadSafeCounter()
        
        def increment_task():
            for _ in range(100):
                counter.increment()
        
        threads = []
        for i in range(10):
            thread = threading.Thread(target=increment_task)
            threads.append(thread)
            thread.start()
        
        for thread in threads:
            thread.join()
        
        self.assertEqual(counter.get_value(), 1000)
    
    def test_metrics_recording(self):
        """Test metrics recording functionality."""
        self.metrics_collector.record_connection(True)
        self.metrics_collector.record_message()
        self.metrics_collector.record_request()
        self.metrics_collector.record_error()
        
        self.assertEqual(self.metrics_collector.connection_count.get_value(), 1)
        self.assertEqual(self.metrics_collector.message_count.get_value(), 1)
        self.assertEqual(self.metrics_collector.request_count.get_value(), 1)
        self.assertEqual(self.metrics_collector.error_count.get_value(), 1)
    
    def test_response_time_recording(self):
        """Test response time recording."""
        response_times = [100, 150, 200, 120, 180]
        
        for rt in response_times:
            self.metrics_collector.record_response_time(rt)
        
        avg_time = self.metrics_collector._calculate_avg_response_time()
        expected_avg = sum(response_times) / len(response_times)
        self.assertEqual(avg_time, expected_avg)
    
    @patch('psutil.cpu_percent')
    @patch('psutil.virtual_memory')
    @patch('psutil.disk_usage')
    @patch('psutil.net_io_counters')
    def test_system_metrics_collection(self, mock_net, mock_disk, mock_memory, mock_cpu):
        """Test system metrics collection."""
        # Mock system metrics
        mock_cpu.return_value = 50.0
        mock_memory.return_value = Mock(total=8000000000, used=4000000000, percent=50.0)
        mock_disk.return_value = Mock(total=1000000000, used=500000000, percent=50.0)
        mock_net.return_value = Mock(bytes_sent=1000000, bytes_recv=2000000)
        
        metrics = self.metrics_collector._collect_system_metrics()
        
        self.assertIn('cpu_percent', metrics)
        self.assertIn('memory_percent', metrics)
        self.assertIn('disk_percent', metrics)
        self.assertEqual(metrics['cpu_percent'], 50.0)
        self.assertEqual(metrics['memory_percent'], 50.0)
        self.assertEqual(metrics['disk_percent'], 50.0)

class TestRateLimiter(unittest.TestCase):
    """Test cases for rate limiting."""
    
    def setUp(self):
        self.rate_limiter = RateLimiter(max_requests=5, time_window=1)
    
    def test_rate_limiting_allows_requests(self):
        """Test that rate limiter allows requests within limit."""
        client_id = "test_client"
        
        # Should allow 5 requests
        for i in range(5):
            self.assertTrue(self.rate_limiter.allow_request(client_id))
        
        # Should block 6th request
        self.assertFalse(self.rate_limiter.allow_request(client_id))
    
    def test_rate_limiting_resets_after_time_window(self):
        """Test that rate limiter resets after time window."""
        client_id = "test_client"
        
        # Exhaust the limit
        for i in range(5):
            self.rate_limiter.allow_request(client_id)
        
        # Should be blocked
        self.assertFalse(self.rate_limiter.allow_request(client_id))
        
        # Wait for time window to pass
        time.sleep(1.1)
        
        # Should be allowed again
        self.assertTrue(self.rate_limiter.allow_request(client_id))
    
    def test_rate_limiting_per_client(self):
        """Test that rate limiting is per-client."""
        client1 = "client1"
        client2 = "client2"
        
        # Exhaust limit for client1
        for i in range(5):
            self.rate_limiter.allow_request(client1)
        
        # client1 should be blocked
        self.assertFalse(self.rate_limiter.allow_request(client1))
        
        # client2 should still be allowed
        self.assertTrue(self.rate_limiter.allow_request(client2))

class TestLoadTesting(unittest.TestCase):
    """Test cases for load testing scenarios."""
    
    def test_concurrent_connections(self):
        """Test handling of concurrent connections."""
        connection_count = ThreadSafeCounter()
        
        def simulate_connection():
            connection_count.increment()
            time.sleep(0.1)  # Simulate connection duration
            connection_count.decrement()
        
        threads = []
        for i in range(50):
            thread = threading.Thread(target=simulate_connection)
            threads.append(thread)
            thread.start()
        
        # Check peak connections
        time.sleep(0.05)  # Let some threads start
        peak_connections = connection_count.get_value()
        self.assertGreater(peak_connections, 0)
        
        # Wait for all threads to complete
        for thread in threads:
            thread.join()
        
        # All connections should be closed
        self.assertEqual(connection_count.get_value(), 0)
    
    def test_memory_usage_under_load(self):
        """Test memory usage under simulated load."""
        import psutil
        
        initial_memory = psutil.virtual_memory().used
        
        # Simulate memory-intensive operations
        data_store = []
        for i in range(1000):
            data_store.append("x" * 1000)  # 1KB per item
        
        peak_memory = psutil.virtual_memory().used
        memory_increase = peak_memory - initial_memory
        
        # Should see some memory increase
        self.assertGreater(memory_increase, 0)
        
        # Clean up
        data_store.clear()
    
    def test_performance_degradation_detection(self):
        """Test detection of performance degradation."""
        response_times = []
        
        # Simulate increasing response times
        for i in range(10):
            start_time = time.time()
            time.sleep(0.01 * (i + 1))  # Increasing delay
            response_time = calculate_response_time(start_time)
            response_times.append(response_time)
        
        # Check for performance degradation
        first_half_avg = sum(response_times[:5]) / 5
        second_half_avg = sum(response_times[5:]) / 5
        
        self.assertGreater(second_half_avg, first_half_avg)

class TestStressScenarios(unittest.TestCase):
    """Test cases for stress scenarios."""
    
    def test_rapid_connection_cycling(self):
        """Test rapid connection establishment and teardown."""
        connection_events = []
        
        def rapid_connect_disconnect():
            for i in range(100):
                connection_events.append(('connect', time.time()))
                time.sleep(0.001)  # Very short connection
                connection_events.append(('disconnect', time.time()))
        
        start_time = time.time()
        rapid_connect_disconnect()
        total_time = time.time() - start_time
        
        # Should complete within reasonable time
        self.assertLess(total_time, 1.0)
        self.assertEqual(len(connection_events), 200)
    
    def test_message_flood_handling(self):
        """Test handling of message flood."""
        message_count = ThreadSafeCounter()
        
        def flood_messages():
            for i in range(1000):
                message_count.increment()
                time.sleep(0.0001)  # Very rapid messages
        
        start_time = time.time()
        flood_messages()
        total_time = time.time() - start_time
        
        # Should handle flood efficiently
        self.assertEqual(message_count.get_value(), 1000)
        self.assertLess(total_time, 1.0)

if __name__ == '__main__':
    unittest.main(verbosity=2)