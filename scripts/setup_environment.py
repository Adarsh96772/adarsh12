import os
import sys
import json
from pathlib import Path
from datetime import datetime

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from database import DatabaseManager
from config import Config

def create_directories():
    """Create necessary directories"""
    directories = [
        "data",
        "logs",
        "tests",
        "scripts"
    ]
    
    for directory in directories:
        Path(directory).mkdir(exist_ok=True)
        print(f"✓ Created directory: {directory}")

def initialize_database():
    """Initialize database with required tables"""
    print("Initializing database...")
    
    try:
        config = Config()
        db_manager = DatabaseManager(config.get("database", "path"))

        # Insert initial server data
        servers = [
            ("Server A", "active"),
            ("Server B", "active"),
            ("Server C", "active")
        ]
        
        for server_name, status in servers:
            db_manager.insert_server_metrics(
                server_name,
                daily_count=0,
                monthly_count=0,
                total_clients=0,
                lost_clients=0,
                rating_sum=0,
                rating_count=0,
                current_client=None
            )
        
        print("✓ Database initialized successfully")
        
    except Exception as e:
        print(f"✗ Database initialization failed: {e}")
        return False
    
    return True

def create_session_data_file():
    """Create initial session data file"""
    session_file = "data/session_data.json"
    
    initial_data = {
        "sessions": {},
        "server_stats": {
            "Server A": {
                "clients_today": 0,
                "clients_month": 0,
                "total_clients": 0,
                "lost_clients": 0,
                "ratings": [],
                "current_client": None
            },
            "Server B": {
                "clients_today": 0,
                "clients_month": 0,
                "total_clients": 0,
                "lost_clients": 0,
                "ratings": [],
                "current_client": None
            },
            "Server C": {
                "clients_today": 0,
                "clients_month": 0,
                "total_clients": 0,
                "lost_clients": 0,
                "ratings": [],
                "current_client": None
            }
        },
        "last_updated": datetime.now().isoformat()
    }
    
    try:
        with open(session_file, 'w') as f:
            json.dump(initial_data, f, indent=2)
        print(f"✓ Created session data file: {session_file}")
        return True
    except Exception as e:
        print(f"✗ Failed to create session data file: {e}")
        return False

def create_client_data():
    """Create sample client data file"""
    client_file = "clients.csv"
    
    # Generate sample client data
    client_data = "client_id,client_name,priority\n"
    for i in range(1, 1001):
        client_data += f"client_{i:04d},Client {i},{i % 3 + 1}\n"
    
    try:
        with open(client_file, 'w') as f:
            f.write(client_data)
        print(f"✓ Created client data file: {client_file}")
        return True
    except Exception as e:
        print(f"✗ Failed to create client data file: {e}")
        return False

def setup_logging():
    """Setup logging configuration"""
    log_config = {
        "version": 1,
        "formatters": {
            "detailed": {
                "format": "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
            }
        },
        "handlers": {
            "file": {
                "class": "logging.FileHandler",
                "filename": "logs/chat_server.log",
                "formatter": "detailed",
                "level": "INFO"
            },
            "console": {
                "class": "logging.StreamHandler",
                "formatter": "detailed",
                "level": "DEBUG"
            }
        },
        "loggers": {
            "chat_server": {
                "level": "DEBUG",
                "handlers": ["file", "console"]
            }
        }
    }
    
    try:
        with open("logging_config.json", 'w') as f:
            json.dump(log_config, f, indent=2)
        print("✓ Created logging configuration")
        return True
    except Exception as e:
        print(f"✗ Failed to create logging configuration: {e}")
        return False

def create_config_file():
    """Create configuration file"""
    config_data = {
        "server": {
            "max_servers": 3,
            "waiting_time": 300,
            "port_range": [8000, 8010]
        },
        "client": {
            "max_clients": 1000,
            "timeout": 30,
            "retry_attempts": 3
        },
        "database": {
            "path": "data/server_metrics.db",
            "backup_interval": 3600
        },
        "logging": {
            "level": "INFO",
            "file": "logs/chat_server.log",
            "archive_file": "archive.txt"
        },
        "performance": {
            "monitor_interval": 1,
            "metrics_retention": 86400
        }
    }
    
    try:
        with open("config.json", 'w') as f:
            json.dump(config_data, f, indent=2)
        print("✓ Created configuration file")
        return True
    except Exception as e:
        print(f"✗ Failed to create configuration file: {e}")
        return False

def check_dependencies():
    """Check if required dependencies are installed"""
    required_packages = [
        "psutil"
    ]
    
    missing_packages = []
    
    for package in required_packages:
        try:
            __import__(package)
        except ImportError:
            missing_packages.append(package)
    
    if missing_packages:
        print(f"✗ Missing packages: {', '.join(missing_packages)}")
        print("Please install missing packages using: pip install -r requirements.txt")
        return False
    else:
        print("✓ All dependencies are installed")
        return True

def create_requirements_file():
    """Create requirements.txt file"""
    requirements = [
        "psutil>=5.8.0"
    ]
    
    try:
        with open("requirements.txt", 'w') as f:
            for req in requirements:
                f.write(f"{req}\n")
        print("✓ Created requirements.txt")
        return True
    except Exception as e:
        print(f"✗ Failed to create requirements.txt: {e}")
        return False

def main():
    """Main setup function"""
    print("Setting up chat server environment...")
    print("=" * 40)
    
    success = True
    
    # Check dependencies first
    if not check_dependencies():
        success = False
    
    # Create directories
    create_directories()
    
    # Create configuration
    if not create_config_file():
        success = False
    
    # Initialize database
    if not initialize_database():
        success = False
    
    # Create session data
    if not create_session_data_file():
        success = False
    
    # Create client data
    if not create_client_data():
        success = False
    
    # Setup logging
    if not setup_logging():
        success = False
    
    # Create requirements file
    if not create_requirements_file():
        success = False
    
    print("=" * 40)
    
    if success:
        print("✓ Environment setup completed successfully!")
        print("\nNext steps:")
        print("1. Install dependencies: pip install -r requirements.txt")
        print("2. Run load tests: python scripts/run_load_test.py")
        print("3. Start servers: python server.py")
        print("4. Run clients: python client.py")
    else:
        print("✗ Environment setup completed with errors!")
        print("Please check the error messages above and fix any issues.")
    
    return success

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)