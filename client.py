# client.py
import datetime
import socket
import time

class Client:
    def __init__(self, name, host="127.0.0.1", port=8000):
        self.name = name
        self.host = host
        self.port = port
        self.server_name = None
        self.session_start = datetime.datetime.now()
        self.session_end = None
        self.rating = None

    def show_details(self):
        print("\n--- Client Session Info ---")
        print("Client Name:", self.name)
        print("Date & Time:", self.session_start.strftime("%Y-%m-%d %H:%M:%S"))

    def connect_and_chat(self):
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
                sock.connect((self.host, self.port))
                self.server_name = f"{self.host}:{self.port}"
                self.show_details()
                print("Connected to server:", self.server_name)

                # Send and receive some messages
                for i in range(5):
                    msg = f"{self.name} message {i+1}"
                    sock.sendall(msg.encode())
                    reply = sock.recv(1024).decode()
                    print("Server replied:", reply)
                    time.sleep(1)

                # Send rating
                self.send_rating(sock)

        except Exception as e:
            print(f"Error during communication: {e}")
        finally:
            self.session_end = datetime.datetime.now()

    def send_rating(self, sock):
        while True:
            try:
                rating = int(input("Rate the server from 1 to 5: "))
                if 1 <= rating <= 5:
                    self.rating = rating
                    sock.sendall(f"RATING:{rating}".encode())
                    break
                else:
                    print("Enter rating from 1 to 5.")
            except ValueError:
                print("Enter a valid number.")

        print("Thank you for your feedback!\n")

    def get_session_summary(self):
        return {
            "client_name": self.name,
            "server_name": self.server_name,
            "start_time": str(self.session_start),
            "end_time": str(self.session_end),
            "rating": self.rating
        }