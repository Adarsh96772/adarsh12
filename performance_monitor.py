import time
import threading
import psutil
from logger import Logger

class PerformanceMonitor:
    def __init__(self, interval=1):
        self.interval = interval
        self.running = False
        self.cpu_usage = []
        self.memory_usage = []
        self.lock = threading.Lock()
        self.logger = Logger("performance_monitor")

    def start_monitoring(self):
        """Start performance monitoring in a background thread."""
        self.running = True
        self.thread = threading.Thread(target=self._monitor_loop, daemon=True)
        self.thread.start()
        self.logger.log_info("Started performance monitoring.")

    def _monitor_loop(self):
        """Collect CPU and memory usage at regular intervals."""
        while self.running:
            with self.lock:
                self.cpu_usage.append(psutil.cpu_percent(interval=None))
                self.memory_usage.append(psutil.virtual_memory().percent)
            time.sleep(self.interval)

    def stop_monitoring(self):
        """Stop monitoring and return average CPU and memory usage."""
        self.running = False
        if hasattr(self, "thread"):
            self.thread.join(timeout=5)

        with self.lock:
            avg_cpu = sum(self.cpu_usage) / len(self.cpu_usage) if self.cpu_usage else 0
            avg_mem = sum(self.memory_usage) / len(self.memory_usage) if self.memory_usage else 0

        self.logger.log_info(
            f"Stopped performance monitoring. "
            f"CPU: {avg_cpu:.2f}%, Memory: {avg_mem:.2f}%"
        )

        return {
            "average_cpu": avg_cpu,
            "average_memory": avg_mem,
            "samples": len(self.cpu_usage)
        }

    def get_current_metrics(self):
        """Return a snapshot of current CPU and memory usage."""
        return {
            "cpu": psutil.cpu_percent(interval=None),
            "memory": psutil.virtual_memory().percent
        }