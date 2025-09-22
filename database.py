import sqlite3
import threading
import json
from datetime import datetime
from config import Config


class DatabaseManager:
    def __init__(self, db_path=None):
        self.config = Config()
        self.db_path = db_path or self.config.get("database", "path")
        self.lock = threading.Lock()
        self.create_tables()

    def create_tables(self):
        """Create required tables in the database."""
        with self.lock:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()

            # Table to store server metrics
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS server_metrics (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    server_name TEXT NOT NULL,
                    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                    daily_count INTEGER DEFAULT 0,
                    monthly_count INTEGER DEFAULT 0,
                    total_clients INTEGER DEFAULT 0,
                    lost_clients INTEGER DEFAULT 0,
                    rating_sum INTEGER DEFAULT 0,
                    rating_count INTEGER DEFAULT 0,
                    current_client TEXT
                )
            ''')

            # Table to store session details
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS sessions (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    client_name TEXT NOT NULL,
                    server_name TEXT NOT NULL,
                    start_time DATETIME NOT NULL,
                    end_time DATETIME,
                    rating INTEGER,
                    status TEXT DEFAULT 'ACTIVE'
                )
            ''')

            # Table to store performance test results
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS performance_metrics (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                    simulation_type TEXT NOT NULL,
                    total_clients INTEGER,
                    successful_sessions INTEGER,
                    lost_clients INTEGER,
                    avg_response_time REAL,
                    throughput REAL,
                    disk_io_operations INTEGER
                )
            ''')

            conn.commit()
            conn.close()

    def add_server(self, server_name, status='active'):
        """Add initial server metrics"""
        self.insert_server_metrics(
            server_name=server_name,
            daily_count=0,
            monthly_count=0,
            total_clients=0,
            lost_clients=0,
            rating_sum=0,
            rating_count=0,
            current_client=None
        )

    def insert_server_metrics(self, server_name, daily_count, monthly_count,
                              total_clients, lost_clients, rating_sum, rating_count, current_client):
        """Insert server metrics"""
        with self.lock:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            cursor.execute('''
                INSERT INTO server_metrics (
                    server_name, daily_count, monthly_count, total_clients,
                    lost_clients, rating_sum, rating_count, current_client
                )
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            ''', (server_name, daily_count, monthly_count, total_clients,
                  lost_clients, rating_sum, rating_count, current_client))
            conn.commit()
            conn.close()

    def insert_session(self, client_name, server_name, start_time, end_time=None, rating=None, status='ACTIVE'):
        """Insert session details"""
        with self.lock:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            cursor.execute('''
                INSERT INTO sessions (
                    client_name, server_name, start_time, end_time, rating, status
                )
                VALUES (?, ?, ?, ?, ?, ?)
            ''', (client_name, server_name, start_time, end_time, rating, status))
            session_id = cursor.lastrowid
            conn.commit()
            conn.close()
            return session_id

    def update_session(self, session_id, end_time, rating, status='COMPLETED'):
        """Update session record"""
        with self.lock:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            cursor.execute('''
                UPDATE sessions
                SET end_time = ?, rating = ?, status = ?
                WHERE id = ?
            ''', (end_time, rating, status, session_id))
            conn.commit()
            conn.close()

    def insert_performance_metrics(self, simulation_type, total_clients, successful_sessions,
                                   lost_clients, avg_response_time, throughput, disk_io_ops):
        """Insert performance test results"""
        with self.lock:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            cursor.execute('''
                INSERT INTO performance_metrics (
                    simulation_type, total_clients, successful_sessions,
                    lost_clients, avg_response_time, throughput, disk_io_operations
                )
                VALUES (?, ?, ?, ?, ?, ?, ?)
            ''', (simulation_type, total_clients, successful_sessions,
                  lost_clients, avg_response_time, throughput, disk_io_ops))
            conn.commit()
            conn.close()

    def get_all_sessions(self):
        with self.lock:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            cursor.execute('SELECT * FROM sessions')
            sessions = cursor.fetchall()
            conn.close()
            return sessions

    def cleanup_old_data(self, days=30):
        """Delete old data from database"""
        with self.lock:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            cursor.execute(f'''
                DELETE FROM server_metrics
                WHERE timestamp < datetime('now', '-{days} days')
            ''')
            cursor.execute(f'''
                DELETE FROM sessions
                WHERE start_time < datetime('now', '-{days} days')
            ''')
            cursor.execute(f'''
                DELETE FROM performance_metrics
                WHERE timestamp < datetime('now', '-{days} days')
            ''')
            conn.commit()
            conn.close()