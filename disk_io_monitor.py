import psutil
import time
import threading
from logger import Logger

logger = Logger("disk_io_monitor")

class DiskIOMonitor:
    def __init__(self, interval=1.0):
        self.interval = interval
        self.running = False
        self.thread = None
        self.metrics = {
            "read_bytes": 0,
            "write_bytes": 0,
            "read_count": 0,
            "write_count": 0,
        }
        self.lock = threading.Lock()
        self.last_counters = psutil.disk_io_counters()

    def _monitor_loop(self):
        while self.running:
            try:
                time.sleep(self.interval)
                counters = psutil.disk_io_counters()
                with self.lock:
                    self.metrics["read_bytes"] += counters.read_bytes - self.last_counters.read_bytes
                    self.metrics["write_bytes"] += counters.write_bytes - self.last_counters.write_bytes
                    self.metrics["read_count"] += counters.read_count - self.last_counters.read_count
                    self.metrics["write_count"] += counters.write_count - self.last_counters.write_count
                    self.last_counters = counters
            except Exception as e:
                logger.log_error(f"Error monitoring disk I/O: {e}")

    def start_monitoring(self):
        self.running = True
        self.thread = threading.Thread(target=self._monitor_loop, daemon=True)
        self.thread.start()
        logger.log_info("Disk I/O monitoring started")

    def stop_monitoring(self):
        self.running = False
        if self.thread:
            self.thread.join(timeout=5)
        logger.log_info("Disk I/O monitoring stopped")
        return self.get_metrics()

    def get_metrics(self):
        with self.lock:
            return {
                "read_MB": round(self.metrics["read_bytes"] / (1024 * 1024), 2),
                "write_MB": round(self.metrics["write_bytes"] / (1024 * 1024), 2),
                "read_ops": self.metrics["read_count"],
                "write_ops": self.metrics["write_count"]
            }