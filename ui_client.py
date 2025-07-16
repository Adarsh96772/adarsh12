import tkinter as tk
from tkinter import ttk, scrolledtext, messagebox
import threading
import socket
import json
import time
from datetime import datetime
from typing import Optional, Dict, Any

from config import Config
from constants import *

class ClientUI:
    def __init__(self, client_name: str):
        self.client_name = client_name
        self.root = tk.Tk()
        self.root.title(f"Chat Client - {client_name}")
        self.root.geometry("600x500")

        self.socket = None
        self.connected = False
        self.server_name = "Not Connected"
        self.session_id = None

        self.chat_ended = False

        self._create_ui()
        self.root.after(1000, self._update_datetime)
        self.root.protocol("WM_DELETE_WINDOW", self._on_closing)

    def _create_ui(self):
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))

        info_frame = ttk.LabelFrame(main_frame, text="Client Information", padding="10")
        info_frame.grid(row=0, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(0, 10))

        ttk.Label(info_frame, text="Client Name:").grid(row=0, column=0, sticky=tk.W)
        self.client_name_var = tk.StringVar(value=self.client_name)
        ttk.Label(info_frame, textvariable=self.client_name_var, font=("Arial", 12, "bold")).grid(row=0, column=1, sticky=tk.W, padx=(10, 0))

        ttk.Label(info_frame, text="Date & Time:").grid(row=1, column=0, sticky=tk.W)
        self.datetime_var = tk.StringVar()
        ttk.Label(info_frame, textvariable=self.datetime_var).grid(row=1, column=1, sticky=tk.W, padx=(10, 0))

        ttk.Label(info_frame, text="Server:").grid(row=2, column=0, sticky=tk.W)
        self.server_name_var = tk.StringVar(value=self.server_name)
        ttk.Label(info_frame, textvariable=self.server_name_var, font=("Arial", 10, "bold")).grid(row=2, column=1, sticky=tk.W, padx=(10, 0))

        conn_frame = ttk.LabelFrame(main_frame, text="Connection", padding="10")
        conn_frame.grid(row=1, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(0, 10))

        ttk.Label(conn_frame, text="Server Port:").grid(row=0, column=0, sticky=tk.W)
        self.port_var = tk.StringVar(value="8001")
        port_combo = ttk.Combobox(conn_frame, textvariable=self.port_var, values=["8001", "8002", "8003"], width=10)
        port_combo.grid(row=0, column=1, sticky=tk.W, padx=(10, 0))

        self.connect_btn = ttk.Button(conn_frame, text="Connect", command=self._connect_to_server)
        self.connect_btn.grid(row=0, column=2, padx=(20, 0))

        self.status_var = tk.StringVar(value="Disconnected")
        ttk.Label(conn_frame, textvariable=self.status_var).grid(row=0, column=3, padx=(20, 0))

        chat_frame = ttk.LabelFrame(main_frame, text="Chat", padding="10")
        chat_frame.grid(row=2, column=0, columnspan=2, sticky=(tk.W, tk.E, tk.N, tk.S), pady=(0, 10))

        self.chat_text = scrolledtext.ScrolledText(chat_frame, height=15, width=60, state=tk.DISABLED)
        self.chat_text.grid(row=0, column=0, columnspan=2, sticky=(tk.W, tk.E, tk.N, tk.S))

        self.message_var = tk.StringVar()
        self.message_entry = ttk.Entry(chat_frame, textvariable=self.message_var, width=50)
        self.message_entry.grid(row=1, column=0, sticky=(tk.W, tk.E), padx=(0, 10), pady=(10, 0))
        self.message_entry.bind('<Return>', self._send_message)

        self.send_btn = ttk.Button(chat_frame, text="Send", command=self._send_message)
        self.send_btn.grid(row=1, column=1, pady=(10, 0))

        control_frame = ttk.Frame(main_frame)
        control_frame.grid(row=3, column=0, columnspan=2, sticky=(tk.W, tk.E))

        self.finish_btn = ttk.Button(control_frame, text="Finish Chat", command=self._finish_chat, state=tk.DISABLED)
        self.finish_btn.grid(row=0, column=0, padx=(0, 10))

        self.clear_btn = ttk.Button(control_frame, text="Clear Chat", command=self._clear_chat)
        self.clear_btn.grid(row=0, column=1)

        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        main_frame.columnconfigure(0, weight=1)
        main_frame.rowconfigure(2, weight=1)
        chat_frame.columnconfigure(0, weight=1)
        chat_frame.rowconfigure(0, weight=1)

        self._set_chat_state(False)

    def _connect_to_server(self):
        if self.connected:
            self._disconnect()
            return

        try:
            port = int(self.port_var.get())
            self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.socket.connect(('localhost', port))

            self.connected = True
            self.status_var.set("Connected")
            self.connect_btn.config(text="Disconnect")
            self._set_chat_state(True)

            threading.Thread(target=self._receive_messages, daemon=True).start()

            client_info = {
                'type': 'client_info',
                'client_name': self.client_name,
                'timestamp': datetime.now().isoformat()
            }
            self._send_json(client_info)
            self._add_chat_message("System", f"Connected to server on port {port}")
        except Exception as e:
            messagebox.showerror("Connection Error", f"Failed to connect: {e}")
            self.status_var.set("Connection Failed")

    def _disconnect(self):
        if self.socket:
            try:
                self.socket.close()
            except:
                pass
            self.socket = None

        self.connected = False
        self.status_var.set("Disconnected")
        self.connect_btn.config(text="Connect")
        self.server_name_var.set("Not Connected")
        self._set_chat_state(False)
        self._add_chat_message("System", "Disconnected from server")

    def _receive_messages(self):
        while self.connected and self.socket:
            try:
                data = self.socket.recv(1024)
                if not data:
                    break
                message = json.loads(data.decode())
                self._handle_server_message(message)
            except:
                break

        if self.connected:
            self._disconnect()

    def _handle_server_message(self, message: Dict[str, Any]):
        msg_type = message.get('type', 'unknown')
        if msg_type == 'welcome':
            self.server_name = message.get('server_name', 'Unknown')
            self.session_id = message.get('session_id')
            self.server_name_var.set(self.server_name)
            self._add_chat_message("Server", message.get('message', 'Welcome!'))
        elif msg_type == 'message':
            self._add_chat_message(message.get('sender', 'Server'), message.get('content', ''))
        elif msg_type == 'waiting':
            self._add_chat_message("System", message.get('message', 'Please wait...'))
        elif msg_type == 'lost':
            self._add_chat_message("System", message.get('message', 'Session ended'))
            self._disconnect()
        elif msg_type == 'chat_ended':
            self._add_chat_message("System", "Chat session ended")
            self.chat_ended = True
            self._show_rating_dialog()
        elif msg_type == 'error':
            self._add_chat_message("Error", message.get('message', 'Unknown error'))

    def _send_message(self, event=None):
        if not self.connected or not self.message_var.get().strip():
            return

        message = self.message_var.get().strip()
        self.message_var.set("")
        msg_data = {
            'type': 'chat_message',
            'content': message,
            'timestamp': datetime.now().isoformat()
        }
        self._send_json(msg_data)
        self._add_chat_message("You", message)

    def _send_json(self, data: Dict[str, Any]):
        if self.socket:
            try:
                self.socket.send(json.dumps(data).encode())
            except Exception as e:
                print(f"Send error: {e}")

    def _add_chat_message(self, sender: str, message: str):
        timestamp = datetime.now().strftime("%H:%M:%S")
        self.chat_text.config(state=tk.NORMAL)
        self.chat_text.insert(tk.END, f"[{timestamp}] {sender}: {message}\n")
        self.chat_text.see(tk.END)
        self.chat_text.config(state=tk.DISABLED)

    def _finish_chat(self):
        if not self.connected:
            return
        self._send_json({'type': 'finish_chat', 'timestamp': datetime.now().isoformat()})
        self.finish_btn.config(state=tk.DISABLED)
        self._add_chat_message("System", "Chat session ending...")

    def _clear_chat(self):
        self.chat_text.config(state=tk.NORMAL)
        self.chat_text.delete("1.0", tk.END)
        self.chat_text.config(state=tk.DISABLED)

    def _show_rating_dialog(self):
        dialog = RatingDialog(self.root, self.server_name)
        rating = dialog.result
        if rating is not None:
            self._send_json({'type': 'rating', 'rating': rating, 'timestamp': datetime.now().isoformat()})
            self._add_chat_message("System", f"Rating sent: {rating}/5")
        self.root.after(2000, self._disconnect)

    def _set_chat_state(self, enabled: bool):
        state = tk.NORMAL if enabled else tk.DISABLED
        self.message_entry.config(state=state)
        self.send_btn.config(state=state)
        self.finish_btn.config(state=state if enabled else tk.DISABLED)

    def _update_datetime(self):
        self.datetime_var.set(datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
        self.root.after(1000, self._update_datetime)

    def _on_closing(self):
        if self.connected:
            self._disconnect()
        self.root.destroy()

    def run(self):
        self.root.mainloop()

class RatingDialog:
    def __init__(self, parent, server_name: str):
        self.result = None
        self.dialog = tk.Toplevel(parent)
        self.dialog.title("Rate Server")
        self.dialog.geometry("300x200")
        self.dialog.transient(parent)
        self.dialog.grab_set()

        self.dialog.update_idletasks()
        x = (parent.winfo_screenwidth() // 2) - 150
        y = (parent.winfo_screenheight() // 2) - 100
        self.dialog.geometry(f"+{x}+{y}")

        frame = ttk.Frame(self.dialog, padding="20")
        frame.grid(row=0, column=0)

        ttk.Label(frame, text=f"Rate {server_name}", font=("Arial", 12, "bold")).grid(row=0, column=0, columnspan=2, pady=(0, 10))
        ttk.Label(frame, text="How was your chat experience?").grid(row=1, column=0, columnspan=2)

        self.rating_var = tk.IntVar(value=5)
        for i in range(1, 6):
            ttk.Radiobutton(frame, text=f"{i}", variable=self.rating_var, value=i).grid(row=2, column=i-1, pady=(10, 10))

        ttk.Button(frame, text="Submit", command=self._submit).grid(row=3, column=0, padx=10, pady=(10, 0))
        ttk.Button(frame, text="Cancel", command=self._cancel).grid(row=3, column=1, padx=10, pady=(10, 0))

        self.dialog.wait_window()

    def _submit(self):
        self.result = self.rating_var.get()
        self.dialog.destroy()

    def _cancel(self):
        self.result = None
        self.dialog.destroy()