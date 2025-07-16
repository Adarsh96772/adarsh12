import os
import json
from typing import Dict, Any
from constants import *

class Config:
    def __init__(self, config_file: str = "config.json"):
        self.config_file = config_file
        self.config = self._load_default_config()
        self._load_config_file()
        
    def _load_default_config(self) -> Dict[str, Any]:
        """Load default configuration values"""
        return {
            "server": {
                "max_servers": MAX_SERVERS,
                "max_clients_per_server": MAX_CLIENTS_PER_SERVER,
                "server_names": SERVER_NAMES,
                "port": DEFAULT_PORT,
                "host": HOST
            },
            "client": {
                "max_clients": MAX_CLIENTS,
                "waiting_time_minutes": CLIENT_WAITING_TIME_MINUTES,
                "max_session_duration_minutes": MAX_SESSION_DURATION_MINUTES
            },
            "rating": {
                "min": RATING_MIN,
                "max": RATING_MAX,
                "default": DEFAULT_RATING
            },
            "simulation": {
                "clients": SIMULATION_CLIENTS,
                "duration_minutes": SIMULATION_DURATION_MINUTES,
                "ramp_up_seconds": LOAD_TEST_RAMP_UP_SECONDS,
                "steady_state_seconds": LOAD_TEST_STEADY_STATE_SECONDS
            },
            "database": {
                "path": DATABASE_PATH,
                "session_data_path": SESSION_DATA_PATH,
                "archive_path": ARCHIVE_PATH
            },
            "threading": {
                "max_threads": MAX_THREADS,
                "thread_pool_size": THREAD_POOL_SIZE,
                "fork_process_limit": FORK_PROCESS_LIMIT
            },
            "logging": {
                "buffer_size": BUFFER_SIZE,
                "flush_interval_seconds": FLUSH_INTERVAL_SECONDS,
                "max_queue_size": MAX_QUEUE_SIZE,
                "rotation_size_mb": LOG_ROTATION_SIZE_MB
            },
            "performance": {
                "metrics_update_interval": METRICS_UPDATE_INTERVAL_SECONDS,
                "cpu_threshold": CPU_THRESHOLD_PERCENT,
                "memory_threshold": MEMORY_THRESHOLD_PERCENT,
                "response_time_threshold": RESPONSE_TIME_THRESHOLD_MS
            },
            "concurrency": {
                "default_method": DEFAULT_CONCURRENCY_METHOD,
                "available_methods": [CONCURRENCY_ITERATIVE, CONCURRENCY_THREADING, CONCURRENCY_FORKING]
            }
        }

    def _load_config_file(self):
        """Load configuration from file if it exists"""
        if os.path.exists(self.config_file):
            try:
                with open(self.config_file, 'r') as f:
                    file_config = json.load(f)
                    self._merge_config(file_config)
                print(f"Configuration loaded from {self.config_file}")
            except Exception as e:
                print(f"Error loading config file: {e}")
                print("Using default configuration")
        else:
            print(f"Config file {self.config_file} not found, using defaults")

    def _merge_config(self, file_config: Dict[str, Any]):
        """Merge file configuration with defaults"""
        for section, values in file_config.items():
            if section in self.config:
                if isinstance(values, dict):
                    self.config[section].update(values)
                else:
                    self.config[section] = values
            else:
                self.config[section] = values

    def get(self, section: str, key: str, default=None):
        """Get configuration value"""
        return self.config.get(section, {}).get(key, default)

    def get_section(self, section: str) -> Dict[str, Any]:
        """Get entire configuration section"""
        return self.config.get(section, {})

    def set(self, section: str, key: str, value: Any):
        """Set configuration value"""
        if section not in self.config:
            self.config[section] = {}
        self.config[section][key] = value

    def save_config(self):
        """Save current configuration to file"""
        try:
            with open(self.config_file, 'w') as f:
                json.dump(self.config, f, indent=2)
            print(f"Configuration saved to {self.config_file}")
        except Exception as e:
            print(f"Error saving config: {e}")

    def validate_config(self) -> bool:
        """Validate configuration values"""
        try:
            assert self.get("server", "max_servers") > 0
            assert self.get("server", "max_clients_per_server") > 0
            assert len(self.get("server", "server_names")) >= self.get("server", "max_servers")

            assert self.get("client", "max_clients") > 0
            assert self.get("client", "waiting_time_minutes") > 0

            assert self.get("rating", "min") < self.get("rating", "max")
            assert self.get("rating", "min") >= 1
            assert self.get("rating", "max") <= 5

            assert self.get("simulation", "clients") > 0
            assert self.get("simulation", "duration_minutes") > 0

            print("Configuration validation successful!")
            return True
        except AssertionError as e:
            print(f"Configuration validation failed: {e}")
            return False
        except Exception as e:
            print(f"Error during validation: {e}")
            return False

    def create_sample_config(self):
        """Create a sample configuration file"""
        sample_config = {
            "server": {
                "max_servers": 3,
                "max_clients_per_server": 15,
                "server_names": ["Server_A", "Server_B", "Server_C", "Server_D"],
                "port": 8080,
                "host": "localhost"
            },
            "client": {
                "max_clients": 150,
                "waiting_time_minutes": 7,
                "max_session_duration_minutes": 45
            },
            "simulation": {
                "clients": 1500,
                "duration_minutes": 45
            },
            "concurrency": {
                "default_method": "threading"
            }
        }

        try:
            with open("config_sample.json", 'w') as f:
                json.dump(sample_config, f, indent=2)
            print("Sample configuration created as config_sample.json")
        except Exception as e:
            print(f"Error creating sample config: {e}")

    def __str__(self):
        return json.dumps(self.config, indent=2)


# Global config instance
config = Config()

# Convenience functions
def get_config(section: str, key: str, default=None):
    return config.get(section, key, default)

def get_server_config():
    return config.get_section("server")

def get_client_config():
    return config.get_section("client")

def get_simulation_config():
    return config.get_section("simulation")

def get_database_config():
    return config.get_section("database")


if __name__ == "__main__":
    print("Testing configuration system...")
    config.validate_config()
    print("\nCurrent Configuration:")
    print(config)
    config.create_sample_config()
    print(f"\nMax Servers: {get_config('server', 'max_servers')}")
    print(f"Max Clients: {get_config('client', 'max_clients')}")
    print(f"Rating Range: {get_config('rating', 'min')}-{get_config('rating', 'max')}")