import unittest
import time
import threading
import json
from unittest.mock import Mock, patch, MagicMock
import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from session_manager import SessionManager
from database import Database
from logger import Logger
from utils import generate_session_id

class TestSessionManager(unittest.TestCase):
    """Test cases for session management."""
    
    def setUp(self):
        self.mock_db = Mock(spec=Database)
        self.mock_logger = Mock(spec=Logger)
        self.session_manager = SessionManager(self.mock_db, self.mock_logger)
    
    def test_session_creation(self):
        """Test session creation."""
        client_id = "test_client"
        session_id = self.session_manager.create_session(client_id)
        
        self.assertIsNotNone(session_id)
        self.assertTrue(self.session_manager.is_session_active(session_id))
        self.assertEqual(len(session_id), 16)  # Expected session ID length
    
    def test_session_validation(self):
        """Test session validation."""
        client_id = "test_client"
        session_id = self.session_manager.create_session(client_id)
        
        # Valid session
        self.assertTrue(self.session_manager.validate_session(session_id))
        
        # Invalid session
        self.assertFalse(self.session_manager.validate_session("invalid_session"))
    
    def test_session_termination(self):
        """Test session termination."""
        client_id = "test_client"
        session_id = self.session_manager.create_session(client_id)
        
        # Session should be active
        self.assertTrue(self.session_manager.is_session_active(session_id))
        
        # Terminate session
        self.session_manager.terminate_session(session_id)
        
        # Session should be inactive
        self.assertFalse(self.session_manager.is_session_active(session_id))
    
    def test_session_data_storage(self):
        """Test session data storage and retrieval."""
        client_id = "test_client"
        session_id = self.session_manager.create_session(client_id)
        
        # Store data
        test_data = {"key": "value", "number": 42}
        self.session_manager.store_session_data(session_id, test_data)
        
        # Retrieve data
        retrieved_data = self.session_manager.get_session_data(session_id)
        self.assertEqual(retrieved_data, test_data)
    
    def test_session_timeout(self):
        """Test session timeout functionality."""
        client_id = "test_client"
        session_id = self.session_manager.create_session(client_id, timeout=1)  # 1 second timeout
        
        # Session should be active initially
        self.assertTrue(self.session_manager.is_session_active(session_id))
        
        # Wait for timeout
        time.sleep(1.5)
        
        # Clean up expired sessions
        self.session_manager.cleanup_expired_sessions()
        
        # Session should be expired
        self.assertFalse(self.session_manager.is_session_active(session_id))
    
    def test_session_activity_tracking(self):
        """Test session activity tracking."""
        client_id = "test_client"
        session_id = self.session_manager.create_session(client_id)
        
        # Update activity
        self.session_manager.update_session_activity(session_id)
        
        # Get session info
        session_info = self.session_manager.get_session_info(session_id)
        self.assertIsNotNone(session_info)
        self.assertIn('last_activity', session_info)
        self.assertIn('created_at', session_info)
        self.assertIn('client_id', session_info)
    
    def test_concurrent_session_access(self):
        """Test concurrent session access."""
        client_id = "test_client"
        session_id = self.session_manager.create_session(client_id)
        
        results = []
        
        def access_session():
            for i in range(10):
                self.session_manager.update_session_activity(session_id)
                results.append(self.session_manager.is_session_active(session_id))
        
        threads = []
        for i in range(5):
            thread = threading.Thread(target=access_session)
            threads.append(thread)
            thread.start()
        
        for thread in threads:
            thread.join()
        
        # All accesses should return True
        self.assertEqual(len(results), 50)
        self.assertTrue(all(results))
    
    def test_session_cleanup(self):
        """Test session cleanup functionality."""
        # Create multiple sessions with different timeouts
        sessions = []
        for i in range(5):
            client_id = f"client_{i}"
            timeout = 1 if i < 3 else 10  # First 3 expire quickly
            session_id = self.session_manager.create_session(client_id, timeout=timeout)
            sessions.append(session_id)
        
        # Wait for some sessions to expire
        time.sleep(1.5)
        
        # Clean up expired sessions
        cleaned_count = self.session_manager.cleanup_expired_sessions()
        
        # Should have cleaned up 3 sessions
        self.assertEqual(cleaned_count, 3)
        
        # Check remaining sessions
        active_sessions = [s for s in sessions if self.session_manager.is_session_active(s)]
        self.assertEqual(len(active_sessions), 2)
    
    def test_session_statistics(self):
        """Test session statistics tracking."""
        # Create multiple sessions
        for i in range(10):
            client_id = f"client_{i}"
            self.session_manager.create_session(client_id)
        
        # Get statistics
        stats = self.session_manager.get_session_statistics()
        
        self.assertIn('total_sessions', stats)
        self.assertIn('active_sessions', stats)
        self.assertIn('expired_sessions', stats)
        self.assertEqual(stats['active_sessions'], 10)
    
    def test_session_persistence(self):
        """Test session persistence to database."""
        client_id = "test_client"
        session_id = self.session_manager.create_session(client_id)
        
        # Store session data
        test_data = {"persistent": True, "data": "test"}
        self.session_manager.store_session_data(session_id, test_data)
        
        # Persist to database
        self.session_manager.persist_session_data(session_id)
        
        # Verify database call
        self.mock_db.save_session.assert_called_once()
    
    def test_session_recovery(self):
        """Test session recovery from database."""
        # Mock database return
        session_data = {
            'session_id': 'test_session',
            'client_id': 'test_client',
            'created_at': time.time(),
            'last_activity': time.time(),
            'data': {'recovered': True}
        }
        self.mock_db.get_session.return_value = session_data
        
        # Recover session
        recovered = self.session_manager.recover_session('test_session')
        
        self.assertTrue(recovered)
        self.assertTrue(self.session_manager.is_session_active('test_session'))
    
    def test_session_migration(self):
        """Test session migration between servers."""
        client_id = "test_client"
        session_id = self.session_manager.create_session(client_id)
        
        # Store some data
        test_data = {"migrated": True}
        self.session_manager.store_session_data(session_id, test_data)
        
        # Export session data
        export_data = self.session_manager.export_session_data(session_id)
        
        # Verify export format
        self.assertIn('session_id', export_data)
        self.assertIn('client_id', export_data)
        self.assertIn('data', export_data)
        self.assertEqual(export_data['data'], test_data)
    
    def test_session_security(self):
        """Test session security features."""
        client_id = "test_client"
        session_id = self.session_manager.create_session(client_id)
        
        # Test session hijacking protection
        different_client = "different_client"
        self.assertFalse(
            self.session_manager.validate_session_for_client(session_id, different_client)
        )
        
        # Test valid client
        self.assertTrue(
            self.session_manager.validate_session_for_client(session_id, client_id)
        )

class TestSessionDataHandling(unittest.TestCase):
    """Test cases for session data handling."""
    
    def setUp(self):
        self.mock_db = Mock(spec=Database)
        self.mock_logger = Mock(spec=Logger)
        self.session_manager = SessionManager(self.mock_db, self.mock_logger)
    
    def test_session_data_serialization(self):
        """Test session data serialization."""
        client_id = "test_client"
        session_id = self.session_manager.create_session(client_id)
        
        # Test complex data structures
        complex_data = {
            'string': 'test',
            'number': 42,
            'list': [1, 2, 3],
            'dict': {'nested': 'value'},
            'boolean': True,
            'null': None
        }
        
        self.session_manager.store_session_data(session_id, complex_data)
        retrieved_data = self.session_manager.get_session_data(session_id)
        
        self.assertEqual(retrieved_data, complex_data)
    
    def test_session_data_updates(self):
        """Test session data updates."""
        client_id = "test_client"
        session_id = self.session_manager.create_session(client_id)
        
        # Initial data
        initial_data = {"counter": 1}
        self.session_manager.store_session_data(session_id, initial_data)
        
        # Update data
        updated_data = {"counter": 2, "new_field": "added"}
        self.session_manager.update_session_data(session_id, updated_data)
        
        # Verify update
        final_data = self.session_manager.get_session_data(session_id)
        self.assertEqual(final_data["counter"], 2)
        self.assertEqual(final_data["new_field"], "added")
    
    def test_session_data_deletion(self):
        """Test session data deletion."""
        client_id = "test_client"
        session_id = self.session_manager.create_session(client_id)
        
        # Store data
        test_data = {"to_delete": True}
        self.session_manager.store_session_data(session_id, test_data)
        
        # Delete specific field
        self.session_manager.delete_session_data_field(session_id, "to_delete")
        
        # Verify deletion
        remaining_data = self.session_manager.get_session_data(session_id)
        self.assertNotIn("to_delete", remaining_data)
    
    def test_session_data_size_limits(self):
        """Test session data size limits."""
        client_id = "test_client"
        session_id = self.session_manager.create_session(client_id)
        
        # Try to store large data
        large_data = {"large_field": "x" * 10000}  # 10KB
        
        # Should handle reasonable size
        result = self.session_manager.store_session_data(session_id, large_data)
        self.assertTrue(result)
        
        # Test extremely large data
        extremely_large_data = {"huge_field": "x" * 1000000}  # 1MB
        
        # Should reject or handle gracefully
        result = self.session_manager.store_session_data(session_id, extremely_large_data)
        # Implementation should handle this appropriately

class TestSessionConcurrency(unittest.TestCase):
    """Test cases for session concurrency handling."""
    
    def setUp(self):
        self.mock_db = Mock(spec=Database)
        self.mock_logger = Mock(spec=Logger)
        self.session_manager = SessionManager(self.mock_db, self.mock_logger)
    
    def test_concurrent_session_creation(self):
        """Test concurrent session creation."""
        results = []
        
        def create_session_task(client_id):
            session_id = self.session_manager.create_session(client_id)
            results.append(session_id)
        
        threads = []
        for i in range(20):
            thread = threading.Thread(target=create_session_task, args=(f"client_{i}",))
            threads.append(thread)
            thread.start()
        
        for thread in threads:
            thread.join()
        
        # All sessions should be created successfully
        self.assertEqual(len(results), 20)
        # All session IDs should be unique
        self.assertEqual(len(set(results)), 20)
    
    def test_concurrent_session_data_access(self):
        """Test concurrent session data access."""
        client_id = "test_client"
        session_id = self.session_manager.create_session(client_id)
        
        # Initial data
        self.session_manager.store_session_data(session_id, {"counter": 0})
        
        def increment_counter():
            for i in range(10):
                current_data = self.session_manager.get_session_data(session_id)
                current_data["counter"] += 1
                self.session_manager.store_session_data(session_id, current_data)
        
        threads = []
        for i in range(5):
            thread = threading.Thread(target=increment_counter)
            threads.append(thread)
            thread.start()
        
        for thread in threads:
            thread.join()
        
        # Final counter value should be 50 (5 threads * 10 increments)
        final_data = self.session_manager.get_session_data(session_id)
        self.assertEqual(final_data["counter"], 50)
    
    def test_session_cleanup_during_access(self):
        """Test session cleanup while sessions are being accessed."""
        # Create sessions with short timeout
        sessions = []
        for i in range(10):
            client_id = f"client_{i}"
            session_id = self.session_manager.create_session(client_id, timeout=2)
            sessions.append(session_id)
        
        access_results = []
        
        def access_sessions():
            for session_id in sessions:
                time.sleep(0.1)
                result = self.session_manager.is_session_active(session_id)
                access_results.append(result)
        
        def cleanup_sessions():
            time.sleep(1)
            self.session_manager.cleanup_expired_sessions()
        
        # Start access thread
        access_thread = threading.Thread(target=access_sessions)
        cleanup_thread = threading.Thread(target=cleanup_sessions)
        
        access_thread.start()
        cleanup_thread.start()
        
        access_thread.join()
        cleanup_thread.join()
        
        # Some sessions should have been accessed before cleanup
        self.assertGreater(len(access_results), 0)

if __name__ == '__main__':
    unittest.main(verbosity=2)