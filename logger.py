# logger.py
import logging
import os
from datetime import datetime
from threading import Lock
from config import Config

# Global archive lock for thread-safe writes
archive_lock = Lock()

class Logger:
    def __init__(self, name="chat_server", log_file=None):
        self.logger = logging.getLogger(name)
        self.logger.setLevel(logging.DEBUG)

        if not self.logger.handlers:
            formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")

            # Console handler
            console_handler = logging.StreamHandler()
            console_handler.setFormatter(formatter)
            console_handler.setLevel(logging.INFO)
            self.logger.addHandler(console_handler)

            # File handler
            if log_file is None:
                try:
                    config = Config()
                    log_file = config.get("logging", "file", "logs/chat_server.log")
                except Exception:
                    log_file = "logs/chat_server.log"

            os.makedirs(os.path.dirname(log_file), exist_ok=True)
            file_handler = logging.FileHandler(log_file)
            file_handler.setFormatter(formatter)
            file_handler.setLevel(logging.DEBUG)
            self.logger.addHandler(file_handler)

    def log_info(self, message):
        self.logger.info(message)

    def log_warning(self, message):
        self.logger.warning(message)

    def log_error(self, message):
        self.logger.error(message)

    def log_debug(self, message):
        self.logger.debug(message)

# Global logger
global_logger = Logger("global_logger")

def log_session(server_name, client_name, rating):
    try:
        os.makedirs("logs", exist_ok=True)
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        session_entry = f"[{timestamp}] Server: {server_name}, Client: {client_name}, Rating: {rating}\n"
        with archive_lock:
            with open("archive.txt", "a") as archive_file:
                archive_file.write(session_entry)
    except Exception as e:
        global_logger.error(f"Failed to log session: {e}")