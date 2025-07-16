#!/usr/bin/env python3

import sys
import os
import time
import subprocess
import json
from datetime import datetime
import webbrowser
from threading import Timer

# Add parent directory to path to import modules
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from performance_monitor import PerformanceMonitor
from logger import Logger

class LoadTester:
    def __init__(self, num_clients=1000, num_servers=3, test_duration=300, open_dashboard=False):
        self.num_clients = num_clients
        self.num_servers = num_servers
        self.test_duration = test_duration
        self.open_dashboard = open_dashboard
        self.logger = Logger("load_test")
        self.performance_monitor = PerformanceMonitor()
        self.results = {}

        if self.open_dashboard:
            self._launch_dashboard()

    def _launch_dashboard(self):
        try:
            dashboard_path = os.path.join(os.path.dirname(__file__), "..", "dashboard_server.py")
            subprocess.Popen([sys.executable, dashboard_path], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            Timer(2.5, lambda: webbrowser.open("http://127.0.0.1:5000")).start()
            print("🌐 Flask dashboard launched.")
        except Exception as e:
            print(f"❌ Failed to launch dashboard: {e}")

    def run_simulation(self, simulation_type):
        print(f"\n=== Running {simulation_type} simulation ===")
        simulation_script = f"simulation_{simulation_type}.py"

        if not os.path.exists(simulation_script):
            print(f"❌ Error: {simulation_script} not found")
            return None

        start_time = time.time()
        self.performance_monitor.start_monitoring()

        try:
            cmd = [
                sys.executable, simulation_script,
                "--clients", str(self.num_clients),
                "--servers", str(self.num_servers),
                "--duration", str(self.test_duration)
            ]

            process = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
            stdout, stderr = process.communicate(timeout=self.test_duration + 60)
            execution_time = time.time() - start_time

            metrics = self.performance_monitor.stop_monitoring()

            print(stdout)
            if stderr.strip():
                print("\n[stderr]:\n", stderr.strip())

            result = {
                'simulation_type': simulation_type,
                'execution_time': execution_time,
                'return_code': process.returncode,
                'stdout': stdout,
                'stderr': stderr,
                'timestamp': datetime.now().isoformat()
            }

            sim_output_file = f"{simulation_type}_simulation_results.json"
            print(f"🔍 Looking for simulation result file: {sim_output_file}")

            if os.path.exists(sim_output_file):
                with open(sim_output_file, 'r') as f:
                    sim_data = json.load(f)

                total_served = sim_data.get("metrics", {}).get("total_clients_served", 0)

                result['status'] = 'PASSED' if total_served > 0 else 'FAILED'
                result['total_clients_served'] = total_served
                result['performance_metrics'] = sim_data.get("performance_metrics", {
                    "avg_cpu_usage": 0,
                    "avg_memory_usage": 0,
                    "disk_io_read": 0,
                    "disk_io_write": 0
                })

            else:
                result['status'] = 'FAILED'
                result['error'] = "Simulation result file missing"

            self.logger.log_info(f"{simulation_type} simulation completed in {execution_time:.2f}s")
            return result

        except subprocess.TimeoutExpired:
            process.kill()
            self.logger.log_error(f"{simulation_type} simulation timed out")
            return {'status': 'FAILED', 'error': 'TimeoutExpired'}

        except Exception as e:
            self.logger.log_error(f"Error running {simulation_type} simulation: {e}")
            return {'status': 'FAILED', 'error': str(e)}

    def run_all_simulations(self):
        simulation_types = ['iterative', 'threading', 'forking']
        for sim_type in simulation_types:
            print(f"\nPreparing {sim_type} simulation...")
            result = self.run_simulation(sim_type)

            if result:
                self.results[sim_type] = result
                print(f"✓ {sim_type} simulation completed\n")
            else:
                print(f"✗ {sim_type} simulation failed\n")

            time.sleep(2)

    def generate_report(self):
        report_path = f"load_test_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        summary = {
            sim: {
                'status': result.get('status', 'UNKNOWN'),
                'execution_time': result.get('execution_time', 0),
                'total_clients_served': result.get('total_clients_served', 0),
                'avg_cpu_usage': result.get('performance_metrics', {}).get('avg_cpu_usage', 0),
                'avg_memory_usage': result.get('performance_metrics', {}).get('avg_memory_usage', 0),
                'disk_io_read': result.get('performance_metrics', {}).get('disk_io_read', 0),
                'disk_io_write': result.get('performance_metrics', {}).get('disk_io_write', 0)
            }
            for sim, result in self.results.items()
        }

        report = {
            'test_config': {
                'clients': self.num_clients,
                'servers': self.num_servers,
                'duration_seconds': self.test_duration,
                'timestamp': datetime.now().isoformat()
            },
            'summary': summary,
            'raw_results': self.results
        }

        with open(report_path, 'w') as f:
            json.dump(report, f, indent=2)

        print(f"\n✅ Report generated: {report_path}")
        self._print_summary(summary)

    def _print_summary(self, summary):
        print("\n" + "=" * 50)
        print("LOAD TEST SUMMARY")
        print("=" * 50)

        for sim, stats in summary.items():
            print(f"\n{sim.upper()} SIMULATION: {stats['status']}")
            if stats['status'] == 'PASSED':
                print(f"  Clients Served: {stats['total_clients_served']}")
                print(f"  Execution Time: {stats['execution_time']:.2f}s")
                print(f"  Avg CPU Usage: {stats['avg_cpu_usage']:.1f}%")
                print(f"  Avg Memory Usage: {stats['avg_memory_usage']:.1f}MB")
                print(f"  Disk I/O Read: {stats['disk_io_read']:.1f}MB")
                print(f"  Disk I/O Write: {stats['disk_io_write']:.1f}MB")
            else:
                print(f"  ⚠ Simulation failed or did not serve any clients.")


def main():
    import argparse

    parser = argparse.ArgumentParser(description="Run load tests for chat server")
    parser.add_argument("--clients", type=int, default=1000, help="Number of clients")
    parser.add_argument("--servers", type=int, default=3, help="Number of servers")
    parser.add_argument("--duration", type=int, default=300, help="Test duration in seconds")
    parser.add_argument("--simulation", choices=["iterative", "threading", "forking", "all"], default="all",
                        help="Simulation type to run")
    parser.add_argument("--open-dashboard", action="store_true", help="Open dashboard in browser after simulation")

    args = parser.parse_args()

    print(f"Starting load test with {args.clients} clients and {args.servers} servers")
    print(f"Test duration: {args.duration} seconds")

    tester = LoadTester(args.clients, args.servers, args.duration, open_dashboard=args.open_dashboard)

    if args.simulation == 'all':
        tester.run_all_simulations()
    else:
        result = tester.run_simulation(args.simulation)
        if result:
            tester.results[args.simulation] = result

    if tester.results:
        tester.generate_report()
    else:
        print("❌ No valid results to report.")


if __name__ == "__main__":
    main()