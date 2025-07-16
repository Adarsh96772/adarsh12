import json
from datetime import datetime
from threading import Lock
from uuid import uuid4
from logger import Logger

# Create a logger instance for this module
logger = Logger("session_manager")

class SessionManager:
    def __init__(self):
        self.sessions = {}
        self.lock = Lock()

    def create_session(self, client_id, server_name):
        """Create a new session for a client"""
        session_id = str(uuid4())
        with self.lock:
            self.sessions[session_id] = {
                "client_id": client_id,
                "server_name": server_name,
                "start_time": datetime.now().isoformat(),
                "end_time": None,
                "rating": None,
                "status": "ACTIVE"
            }
        logger.log_info(f"Created session {session_id} for client {client_id} on {server_name}")
        return session_id

    def end_session(self, session_id, rating=None):
        """End a session and update rating"""
        with self.lock:
            if session_id in self.sessions:
                self.sessions[session_id]["end_time"] = datetime.now().isoformat()
                self.sessions[session_id]["rating"] = rating
                self.sessions[session_id]["status"] = "COMPLETED"
                logger.log_info(f"Ended session {session_id} with rating {rating}")
            else:
                logger.log_warning(f"Session {session_id} not found to end")

    def get_session(self, session_id):
        """Retrieve session info"""
        with self.lock:
            return self.sessions.get(session_id)

    def archive_sessions(self, path='data/session_data.json'):
        """Write all session data to a file"""
        with self.lock:
            try:
                with open(path, 'w') as f:
                    json.dump(self.sessions, f, indent=2)
                logger.log_info(f"Archived sessions to {path}")
            except Exception as e:
                logger.log_error(f"Failed to archive sessions: {e}")