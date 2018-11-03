"""
    Author: Heidi Neuhäuser
"""
import socket
import sys
from time import sleep
import traceback
from _thread import *


class Client:

    def __init__(self, host, port):
        self.host = host
        self.port = port
        self.listening = True
        self.client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    def connect_to_server(self):
        """
        Connects client to game server.
        """
        print("\nClient connecting to server.")
        self.client_socket.connect((self.host, self.port))

    def disconnect(self, reason):
        """
        Ends the thread used to listen for incoming messages.
        Closes the socket connection and terminates the programme.
        """
        self.listening = False
        sleep(0.05)
        self.client_socket.close()
        print("%s. Shut down." % reason)
        sys.exit(0)

    def send_message(self, m):
        """
        Send message to server.
        """
        self.client_socket.send(m.encode('utf-8'))

    def listen_to_server(self):
        """
        Threaded function used to listen for incoming messages from the server.
        """
        try:
            while self.listening:
                received = self.client_socket.recv(256)
                msg = received.decode('utf-8')
                if len(msg) > 1:
                    self.read_message(msg)
        except socket.error:
            traceback.print_exc(file=sys.stdout)
            print("Error receiving on socket.")

    def read_message(self, msg):
        """
        Processes the messages received by the server.
        """
        print("Message from Server: %s" % msg)


if __name__ == "__main__":
    h = "127.0.0.1"
    p = 22222

    c = Client(h, p)
    c.connect_to_server()
    start_new_thread(c.listen_to_server, ())
    c.send_message("Hello from client.")
    c.disconnect("Client disconnected.")
