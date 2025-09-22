import tkinter as tk
from tkinter import ttk, scrolledtext
import threading
import time
import json
from datetime import datetime, timedelta
from typing import Dict, Any
import queue

from config import Config
from constants import *
from database import MetricsDatabase
from logger import ArchiveLogger

class ServerUI:
    def __init__(self, server_name: str, port: int):
        self.server_name = server_name
        self.port = port
        self.root = tk.Tk()
        self.root.title(f"Chat Server - {server_name}")
        self.root.geometry("800x600")
        
        # Data
        self.daily_clients = 0
        self.monthly_clients = 0
        self.ratings = []
        self.total_clients = 0
        self.lost_clients = 0
        self.current_client = "None"
        
        # Components
        self.db = MetricsDatabase()
        self.logger = ArchiveLogger()
        
        # Update queue for thread-safe UI updates
        self.update_queue = queue.Queue()
        
        # Create UI elements
        self._create_ui()
        
        # Start update threads
        self._start_update_threads()
        
        # Schedule periodic updates
        self.root.after(1000, self._process_updates)
    
    def _create_ui(self):
        """Create the user interface elements"""
        # Main frame
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Server info frame
        info_frame = ttk.LabelFrame(main_frame, text="Server Information", padding="10")
        info_frame.grid(row=0, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(0, 10))
        
        # Server name
        ttk.Label(info_frame, text="Server Name:").grid(row=0, column=0, sticky=tk.W)
        self.server_name_var = tk.StringVar(value=self.server_name)
        ttk.Label(info_frame, textvariable=self.server_name_var, font=("Arial", 12, "bold")).grid(row=0, column=1, sticky=tk.W, padx=(10, 0))
        
        # Date and time
        ttk.Label(info_frame, text="Date & Time:").grid(row=1, column=0, sticky=tk.W)
        self.datetime_var = tk.StringVar()
        ttk.Label(info_frame, textvariable=self.datetime_var).grid(row=1, column=1, sticky=tk.W, padx=(10, 0))
        
        # Port
        ttk.Label(info_frame, text="Port:").grid(row=2, column=0, sticky=tk.W)
        ttk.Label(info_frame, text=str(self.port)).grid(row=2, column=1, sticky=tk.W, padx=(10, 0))
        
        # Statistics frame
        stats_frame = ttk.LabelFrame(main_frame, text="Statistics", padding="10")
        stats_frame.grid(row=1, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(0, 10))
        
        # Daily clients
        ttk.Label(stats_frame, text="Clients Today:").grid(row=0, column=0, sticky=tk.W)
        self.daily_clients_var = tk.StringVar(value="0")
        ttk.Label(stats_frame, textvariable=self.daily_clients_var, font=("Arial", 10, "bold")).grid(row=0, column=1, sticky=tk.W, padx=(10, 0))
        
        # Monthly clients
        ttk.Label(stats_frame, text="Clients This Month:").grid(row=1, column=0, sticky=tk.W)
        self.monthly_clients_var = tk.StringVar(value="0")
        ttk.Label(stats_frame, textvariable=self.monthly_clients_var, font=("Arial", 10, "bold")).grid(row=1, column=1, sticky=tk.W, padx=(10, 0))
        
        # Average rating
        ttk.Label(stats_frame, text="Average Rating:").grid(row=2, column=0, sticky=tk.W)
        self.avg_rating_var = tk.StringVar(value="N/A")
        ttk.Label(stats_frame, textvariable=self.avg_rating_var, font=("Arial", 10, "bold")).grid(row=2, column=1, sticky=tk.W, padx=(10, 0))
        
        # Total clients
        ttk.Label(stats_frame, text="Total Clients:").grid(row=3, column=0, sticky=tk.W)
        self.total_clients_var = tk.StringVar(value="0")
        ttk.Label(stats_frame, textvariable=self.total_clients_var, font=("Arial", 10, "bold")).grid(row=3, column=1, sticky=tk.W, padx=(10, 0))
        
        # Lost clients
        ttk.Label(stats_frame, text="Lost Clients:").grid(row=4, column=0, sticky=tk.W)
        self.lost_clients_var = tk.StringVar(value="0")
        ttk.Label(stats_frame, textvariable=self.lost_clients_var, font=("Arial", 10, "bold")).grid(row=4, column=1, sticky=tk.W, padx=(10, 0))
        
        # Current client frame
        current_frame = ttk.LabelFrame(main_frame, text="Current Activity", padding="10")
        current_frame.grid(row=2, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(0, 10))
        
        ttk.Label(current_frame, text="Current Client:").grid(row=0, column=0, sticky=tk.W)
        self.current_client_var = tk.StringVar(value="None")
        ttk.Label(current_frame, textvariable=self.current_client_var, font=("Arial", 10, "bold")).grid(row=0, column=1, sticky=tk.W, padx=(10, 0))
        
        # Activity log frame
        log_frame = ttk.LabelFrame(main_frame, text="Activity Log", padding="10")
        log_frame.grid(row=3, column=0, columnspan=2, sticky=(tk.W, tk.E, tk.N, tk.S), pady=(0, 10))
        
        # Log text area
        self.log_text = scrolledtext.ScrolledText(log_frame, height=15, width=70)
        self.log_text.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Control buttons frame
        control_frame = ttk.Frame(main_frame)
        control_frame.grid(row=4, column=0, columnspan=2, sticky=(tk.W, tk.E))
        
        ttk.Button(control_frame, text="Clear Log", command=self._clear_log).grid(row=0, column=0, padx=(0, 10))
        ttk.Button(control_frame, text="Export Stats", command=self._export_stats).grid(row=0, column=1, padx=(0, 10))
        ttk.Button(control_frame, text="Refresh", command=self._refresh_data).grid(row=0, column=2)
        
        # Configure grid weights
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        main_frame.columnconfigure(0, weight=1)
        main_frame.rowconfigure(3, weight=1)
        log_frame.columnconfigure(0, weight=1)
        log_frame.rowconfigure(0, weight=1)
    
    def _start_update_threads(self):
        """Start background threads for data updates"""
        # Thread for updating statistics
        stats_thread = threading.Thread(target=self._update_stats_thread, daemon=True)
        stats_thread.start()
        
        # Thread for monitoring log file
        log_thread = threading.Thread(target=self._monitor_log_thread, daemon=True)
        log_thread.start()
    
    def _update_stats_thread(self):
        """Background thread to update statistics"""
        while True:
            try:
                # Get current stats from database
                stats = self._get_current_stats()
                
                # Queue update
                self.update_queue.put(('stats', stats))
                
                time.sleep(5)  # Update every 5 seconds
                
            except Exception as e:
                print(f"Error updating stats: {e}")
                time.sleep(10)
    
    def _monitor_log_thread(self):
        """Background thread to monitor log file"""
        try:
            with open(Config.ARCHIVE_FILE, 'r') as f:
                # Go to end of file
                f.seek(0, 2)
                
                while True:
                    line = f.readline()
                    if line:
                        # Parse log entry
                        try:
                            log_entry = json.loads(line.strip())
                            if log_entry.get('server_name') == self.server_name:
                                self.update_queue.put(('log', log_entry))
                        except json.JSONDecodeError:
                            pass
                    else:
                        time.sleep(0.1)
                        
        except FileNotFoundError:
            pass
        except Exception as e:
            print(f"Error monitoring log: {e}")
    
    def _get_current_stats(self) -> Dict[str, Any]:
        """Get current server statistics"""
        try:
            # Get stats from database
            stats = self.db.get_server_stats(self.server_name)
            
            # Get today's date
            today = datetime.now().date()
            month_start = today.replace(day=1)
            
            # Calculate daily and monthly clients
            daily_clients = len([s for s in stats if s['date'] == today.isoformat()])
            monthly_clients = len([s for s in stats if s['date'] >= month_start.isoformat()])
            
            # Calculate average rating
            ratings = [s['rating'] for s in stats if s['rating'] is not None]
            avg_rating = sum(ratings) / len(ratings) if ratings else 0
            
            # Get total and lost clients
            total_clients = len(stats)
            lost_clients = len([s for s in stats if s['status'] == 'lost'])
            
            return {
                'daily_clients': daily_clients,
                'monthly_clients': monthly_clients,
                'avg_rating': avg_rating,
                'total_clients': total_clients,
                'lost_clients': lost_clients
            }
            
        except Exception as e:
            print(f"Error getting stats: {e}")
            return {
                'daily_clients': 0,
                'monthly_clients': 0,
                'avg_rating': 0,
                'total_clients': 0,
                'lost_clients': 0
            }
    
    def _process_updates(self):
        """Process updates from background threads"""
        try:
            while True:
                update_type, data = self.update_queue.get_nowait()
                
                if update_type == 'stats':
                    self._update_stats_display(data)
                elif update_type == 'log':
                    self._update_log_display(data)
                elif update_type == 'current_client':
                    self.current_client_var.set(data)
                    
        except queue.Empty:
            pass
        
        # Update date/time
        self.datetime_var.set(datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
        
        # Schedule next update
        self.root.after(1000, self._process_updates)
    
    def _update_stats_display(self, stats: Dict[str, Any]):
        """Update statistics display"""
        self.daily_clients_var.set(str(stats['daily_clients']))
        self.monthly_clients_var.set(str(stats['monthly_clients']))
        self.avg_rating_var.set(f"{stats['avg_rating']:.1f}" if stats['avg_rating'] > 0 else "N/A")
        self.total_clients_var.set(str(stats['total_clients']))
        self.lost_clients_var.set(str(stats['lost_clients']))
    
    def _update_log_display(self, log_entry: Dict[str, Any]):
        """Update log display with new entry"""
        timestamp = log_entry.get('timestamp', datetime.now().isoformat())
        event_type = log_entry.get('event_type', 'UNKNOWN')
        message = log_entry.get('message', '')
        
        log_line = f"[{timestamp}] {event_type}: {message}\n"
        
        self.log_text.insert(tk.END, log_line)
        self.log_text.see(tk.END)
        
        # Keep only last 1000 lines
        lines = self.log_text.get("1.0", tk.END).split('\n')
        if len(lines) > 1000:
            self.log_text.delete("1.0", f"{len(lines) - 1000}.0")
    
    def _clear_log(self):
        """Clear the log display"""
        self.log_text.delete("1.0", tk.END)
    
    def _export_stats(self):
        """Export current statistics to file"""
        try:
            stats = self._get_current_stats()
            filename = f"server_stats_{self.server_name}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
            
            with open(filename, 'w') as f:
                json.dump(stats, f, indent=2)
            
            # Show status message
            self.log_text.insert(tk.END, f"[{datetime.now().isoformat()}] EXPORT: Stats exported to {filename}\n")
            self.log_text.see(tk.END)
            
        except Exception as e:
            self.log_text.insert(tk.END, f"[{datetime.now().isoformat()}] ERROR: Failed to export stats - {e}\n")
            self.log_text.see(tk.END)
    
    def _refresh_data(self):
        """Manually refresh all data"""
        stats = self._get_current_stats()
        self.update_queue.put(('stats', stats))
    
    def update_current_client(self, client_name: str):
        """Update current client name"""
        self.update_queue.put(('current_client', client_name))
    
    def run(self):
        """Run the UI main loop"""
        self.root.mainloop()

def main():
    """Main function for testing"""
    import sys
    
    if len(sys.argv) != 3:
        print("Usage: python ui_server.py <server_name> <port>")
        sys.exit(1)
    
    server_name = sys.argv[1]
    port = int(sys.argv[2])
    
    ui = ServerUI(server_name, port)
    ui.run()

if __name__ == "__main__":
    main()