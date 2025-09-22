import time
import threading
import psutil
import json
from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta
from database import Database
from logger import Logger
from utils import ThreadSafeCounter, format_timestamp

class MetricsCollector:
    """Collects and stores system and application metrics."""
    
    def __init__(self, db: Database, logger: Logger, collection_interval: int = 5):
        self.db = db
        self.logger = logger
        self.collection_interval = collection_interval
        self.is_running = False
        self.collection_thread = None
        
        # Metrics counters
        self.connection_count = ThreadSafeCounter()
        self.message_count = ThreadSafeCounter()
        self.error_count = ThreadSafeCounter()
        self.request_count = ThreadSafeCounter()
        
        # Performance metrics
        self.response_times = []
        self.response_times_lock = threading.Lock()
        
        # System metrics cache
        self.last_system_metrics = {}
        self.metrics_cache = []
        self.cache_lock = threading.Lock()
    
    def start_collection(self):
        """Start metrics collection in background thread."""
        if not self.is_running:
            self.is_running = True
            self.collection_thread = threading.Thread(target=self._collect_metrics_loop)
            self.collection_thread.daemon = True
            self.collection_thread.start()
            self.logger.info("Metrics collection started")
    
    def stop_collection(self):
        """Stop metrics collection."""
        self.is_running = False
        if self.collection_thread:
            self.collection_thread.join()
        self.logger.info("Metrics collection stopped")
    
    def _collect_metrics_loop(self):
        """Main metrics collection loop."""
        while self.is_running:
            try:
                metrics = self._collect_system_metrics()
                self._store_metrics(metrics)
                self._update_cache(metrics)
                time.sleep(self.collection_interval)
            except Exception as e:
                self.logger.error(f"Error in metrics collection: {e}")
                time.sleep(self.collection_interval)
    
    def _collect_system_metrics(self) -> Dict[str, Any]:
        """Collect system performance metrics."""
        try:
            # CPU metrics
            cpu_percent = psutil.cpu_percent(interval=1)
            cpu_count = psutil.cpu_count()
            
            # Memory metrics
            memory = psutil.virtual_memory()
            
            # Disk metrics
            disk = psutil.disk_usage('/')
            
            # Network metrics (if available)
            network = psutil.net_io_counters()
            
            return {
                'timestamp': time.time(),
                'cpu_percent': cpu_percent,
                'cpu_count': cpu_count,
                'memory_total': memory.total,
                'memory_used': memory.used,
                'memory_percent': memory.percent,
                'disk_total': disk.total,
                'disk_used': disk.used,
                'disk_percent': disk.percent,
                'network_bytes_sent': network.bytes_sent,
                'network_bytes_recv': network.bytes_recv,
                'connections': self.connection_count.get_value(),
                'messages_processed': self.message_count.get_value(),
                'errors': self.error_count.get_value(),
                'requests': self.request_count.get_value(),
                'avg_response_time': self._calculate_avg_response_time()
            }
        except Exception as e:
            self.logger.error(f"Error collecting system metrics: {e}")
            return {'timestamp': time.time(), 'error': str(e)}
    
    def _store_metrics(self, metrics: Dict[str, Any]):
        """Store metrics in database."""
        try:
            self.db.insert_metrics(metrics)
        except Exception as e:
            self.logger.error(f"Error storing metrics: {e}")
    
    def _update_cache(self, metrics: Dict[str, Any]):
        """Update metrics cache for quick access."""
        with self.cache_lock:
            self.metrics_cache.append(metrics)
            # Keep only last 100 entries
            if len(self.metrics_cache) > 100:
                self.metrics_cache.pop(0)
            self.last_system_metrics = metrics
    
    def _calculate_avg_response_time(self) -> float:
        """Calculate average response time."""
        with self.response_times_lock:
            if not self.response_times:
                return 0.0
            return sum(self.response_times) / len(self.response_times)
    
    def record_connection(self, increment: bool = True):
        """Record connection event."""
        if increment:
            self.connection_count.increment()
        else:
            self.connection_count.decrement()
    
    def record_message(self):
        """Record message processing."""
        self.message_count.increment()
    
    def record_error(self):
        """Record error event."""
        self.error_count.increment()
    
    def record_request(self):
        """Record request event."""
        self.request_count.increment()
    
    def record_response_time(self, response_time: float):
        """Record response time."""
        with self.response_times_lock:
            self.response_times.append(response_time)
            # Keep only last 1000 response times
            if len(self.response_times) > 1000:
                self.response_times.pop(0)
    
    def get_current_metrics(self) -> Dict[str, Any]:
        """Get current system metrics."""
        with self.cache_lock:
            return self.last_system_metrics.copy()
    
    def get_metrics_history(self, hours: int = 1) -> List[Dict[str, Any]]:
        """Get metrics history for specified hours."""
        cutoff_time = time.time() - (hours * 3600)
        
        try:
            return self.db.get_metrics_since(cutoff_time)
        except Exception as e:
            self.logger.error(f"Error getting metrics history: {e}")
            return []
    
    def get_performance_summary(self) -> Dict[str, Any]:
        """Get performance summary."""
        current_metrics = self.get_current_metrics()
        
        return {
            'timestamp': format_timestamp(),
            'active_connections': self.connection_count.get_value(),
            'total_messages': self.message_count.get_value(),
            'total_errors': self.error_count.get_value(),
            'total_requests': self.request_count.get_value(),
            'avg_response_time_ms': self._calculate_avg_response_time(),
            'cpu_usage_percent': current_metrics.get('cpu_percent', 0),
            'memory_usage_percent': current_metrics.get('memory_percent', 0),
            'disk_usage_percent': current_metrics.get('disk_percent', 0),
            'uptime_seconds': time.time() - getattr(self, 'start_time', time.time())
        }
    
    def reset_counters(self):
        """Reset all counters."""
        self.connection_count.reset()
        self.message_count.reset()
        self.error_count.reset()
        self.request_count.reset()
        
        with self.response_times_lock:
            self.response_times.clear()
        
        self.logger.info("Metrics counters reset")
    
    def export_metrics(self, file_path: str, hours: int = 24) -> bool:
        """Export metrics to JSON file."""
        try:
            metrics_data = {
                'export_timestamp': time.time(),
                'summary': self.get_performance_summary(),
                'history': self.get_metrics_history(hours)
            }
            
            with open(file_path, 'w') as f:
                json.dump(metrics_data, f, indent=2)
            
            self.logger.info(f"Metrics exported to {file_path}")
            return True
        except Exception as e:
            self.logger.error(f"Error exporting metrics: {e}")
            return False
    
    def get_alert_conditions(self) -> List[Dict[str, Any]]:
        """Check for alert conditions."""
        alerts = []
        current_metrics = self.get_current_metrics()
        
        # CPU alert
        if current_metrics.get('cpu_percent', 0) > 80:
            alerts.append({
                'type': 'cpu_high',
                'message': f"High CPU usage: {current_metrics['cpu_percent']:.1f}%",
                'severity': 'warning'
            })
        
        # Memory alert
        if current_metrics.get('memory_percent', 0) > 85:
            alerts.append({
                'type': 'memory_high',
                'message': f"High memory usage: {current_metrics['memory_percent']:.1f}%",
                'severity': 'warning'
            })
        
        # Disk alert
        if current_metrics.get('disk_percent', 0) > 90:
            alerts.append({
                'type': 'disk_high',
                'message': f"High disk usage: {current_metrics['disk_percent']:.1f}%",
                'severity': 'critical'
            })
        
        # Error rate alert
        error_rate = self.error_count.get_value() / max(self.request_count.get_value(), 1)
        if error_rate > 0.1:  # 10% error rate
            alerts.append({
                'type': 'error_rate_high',
                'message': f"High error rate: {error_rate:.1%}",
                'severity': 'warning'
            })
        
        return alerts