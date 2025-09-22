import os
import random
import sys
import time
import json
import hashlib
import threading
import logging
from typing import Dict, Any, Optional, List
from datetime import datetime, timedelta

# Basic utility for rating generation
def generate_rating() -> int:
    return random.randint(1, 5)

# Current datetime formatted
def current_datetime() -> str:
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")

# Format session log
def format_log(server_name: str, client_name: str, rating: Optional[int] = None, lost: bool = False) -> str:
    status = "LOST" if lost else f"RATING: {rating}"
    return f"{current_datetime()} | Server: {server_name} | Client: {client_name} | {status}\n"

# Generate session ID
def generate_session_id() -> str:
    timestamp = str(time.time())
    return hashlib.md5(timestamp.encode()).hexdigest()[:16]

# Format timestamp for logging
def format_timestamp(timestamp: float = None) -> str:
    if timestamp is None:
        timestamp = time.time()
    return datetime.fromtimestamp(timestamp).strftime('%Y-%m-%d %H:%M:%S')

# Validate incoming message JSON structure
def validate_message_format(message: str) -> bool:
    try:
        data = json.loads(message)
        required_fields = ['type', 'timestamp']
        return all(field in data for field in required_fields)
    except json.JSONDecodeError:
        return False

# JSON-encode a message
def serialize_message(msg_type: str, data: Dict[str, Any], sender_id: str = None) -> str:
    message = {
        'type': msg_type,
        'timestamp': time.time(),
        'data': data
    }
    if sender_id:
        message['sender_id'] = sender_id
    return json.dumps(message)

# JSON-decode a message
def deserialize_message(message: str) -> Dict[str, Any]:
    try:
        return json.loads(message)
    except json.JSONDecodeError:
        return {}

# Response time calculation
def calculate_response_time(start_time: float, end_time: float = None) -> float:
    if end_time is None:
        end_time = time.time()
    return (end_time - start_time) * 1000

# Convert bytes to readable units
def format_bytes(bytes_value: int) -> str:
    for unit in ['B', 'KB', 'MB', 'GB']:
        if bytes_value < 1024.0:
            return f"{bytes_value:.2f} {unit}"
        bytes_value /= 1024.0
    return f"{bytes_value:.2f} TB"

# System resource usage snapshot
def get_system_info() -> Dict[str, Any]:
    import psutil
    return {
        'cpu_percent': psutil.cpu_percent(interval=1),
        'memory_percent': psutil.virtual_memory().percent,
        'disk_percent': psutil.disk_usage('/').percent,
        'timestamp': time.time()
    }

# Thread-safe counter
class ThreadSafeCounter:
    def __init__(self, initial_value: int = 0):
        self._value = initial_value
        self._lock = threading.Lock()

    def increment(self, amount: int = 1) -> int:
        with self._lock:
            self._value += amount
            return self._value

    def decrement(self, amount: int = 1) -> int:
        with self._lock:
            self._value -= amount
            return self._value

    def get_value(self) -> int:
        with self._lock:
            return self._value

    def reset(self) -> None:
        with self._lock:
            self._value = 0

# Basic rate limiter
class RateLimiter:
    def __init__(self, max_requests: int, time_window: int):
        self.max_requests = max_requests
        self.time_window = time_window
        self.requests = {}
        self.lock = threading.Lock()

    def allow_request(self, client_id: str) -> bool:
        current_time = time.time()
        with self.lock:
            if client_id not in self.requests:
                self.requests[client_id] = []

            self.requests[client_id] = [
                req_time for req_time in self.requests[client_id]
                if current_time - req_time < self.time_window
            ]

            if len(self.requests[client_id]) < self.max_requests:
                self.requests[client_id].append(current_time)
                return True
            return False

# Retry wrapper
def retry_operation(func, max_retries: int = 3, delay: float = 1.0):
    for attempt in range(max_retries):
        try:
            return func()
        except Exception as e:
            if attempt == max_retries - 1:
                raise e
            time.sleep(delay * (2 ** attempt))

# Safe JSON loading
def safe_json_load(file_path: str, default: Any = None) -> Any:
    try:
        with open(file_path, 'r') as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError) as e:
        logging.warning(f"Failed to load JSON from {file_path}: {e}")
        return default

# Safe JSON saving
def safe_json_save(data: Any, file_path: str) -> bool:
    try:
        with open(file_path, 'w') as f:
            json.dump(data, f, indent=2)
        return True
    except Exception as e:
        logging.error(f"Failed to save JSON to {file_path}: {e}")
        return False

# File cleanup utility
def cleanup_old_files(directory: str, max_age_days: int = 7) -> int:
    cutoff_time = time.time() - (max_age_days * 24 * 60 * 60)
    cleaned_count = 0
    try:
        for filename in os.listdir(directory):
            file_path = os.path.join(directory, filename)
            if os.path.isfile(file_path) and os.path.getmtime(file_path) < cutoff_time:
                os.remove(file_path)
                cleaned_count += 1
    except Exception as e:
        logging.error(f"Error cleaning up files: {e}")
    return cleaned_count


def generate_client_id(index: int) -> str:
    return f"Client_{index:04d}"