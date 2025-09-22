Cleanup script to reset the chat server environment.
Removes log files, databases, and temporary data.
"""

import os
import shutil
import sqlite3
import json
import glob
from pathlib import Path

def cleanup_logs():
    """Remove all log files"""
    log_files = glob.glob("*.log")
    for log_file in log_files:
        try:
            os.remove(log_file)
            print(f"Removed log file: {log_file}")
        except FileNotFoundError:
            pass
        except Exception as e:
            print(f"Error removing {log_file}: {e}")

def cleanup_database():
    """Reset database files"""
    db_path = "data/server_metrics.db"
    if os.path.exists(db_path):
        try:
            os.remove(db_path)
            print(f"Removed database: {db_path}")
        except Exception as e:
            print(f"Error removing database: {e}")

def cleanup_session_data():
    """Reset session data"""
    session_path = "data/session_data.json"
    if os.path.exists(session_path):
        try:
            with open(session_path, 'w') as f:
                json.dump({}, f)
            print(f"Reset session data: {session_path}")
        except Exception as e:
            print(f"Error resetting session data: {e}")

def cleanup_archive():
    """Clean archive files"""
    archive_files = ["archive.txt", "archive.log"]
    for archive_file in archive_files:
        if os.path.exists(archive_file):
            try:
                os.remove(archive_file)
                print(f"Removed archive file: {archive_file}")
            except Exception as e:
                print(f"Error removing {archive_file}: {e}")

def cleanup_temp_files():
    """Remove temporary files"""
    temp_patterns = ["*.tmp", "*.temp", "*.pid", "__pycache__"]
    for pattern in temp_patterns:
        files = glob.glob(pattern)
        for file in files:
            try:
                if os.path.isdir(file):
                    shutil.rmtree(file)
                    print(f"Removed directory: {file}")
                else:
                    os.remove(file)
                    print(f"Removed temp file: {file}")
            except Exception as e:
                print(f"Error removing {file}: {e}")

def ensure_data_directory():
    """Ensure data directory exists"""
    data_dir = Path("data")
    data_dir.mkdir(exist_ok=True)
    print("Ensured data directory exists")

def main():
    """Main cleanup function"""
    print("Starting cleanup process...")
    
    cleanup_logs()
    cleanup_database()
    cleanup_session_data()
    cleanup_archive()
    cleanup_temp_files()
    ensure_data_directory()
    
    print("Cleanup completed successfully!")

if __name__ == "__main__":
    main()