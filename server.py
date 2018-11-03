"""
    Author: Heidi Neuhäuser
"""
import socket
from _thread import *
import sys
import traceback

class Server:
    """
    Server class manages socket connections to clients.
    """

    def __init__(self, ip, port):
        self.host = ip
        self.port = port
        self.clients = {}

    def notify_clients(self, msg, client_to_be_left_out=None):
        """
        Used to send messages to all clients.
        Can be used to forward movements from one client, without this client receiving his own updates
        by specifying client_to_be_left_out.

        :param msg: message to be send to players.
        :param client_to_be_left_out: player that sends the message and thus does not need to receive it.
        """
        for client_id in self.clients:
            if client_id != client_to_be_left_out:
                try:
                    self.clients[client_id].send(msg.encode('utf-8'))
                except ConnectionResetError:
                    print("Socket connection closed by client %s" % client_id)
                    del self.clients[client_id]

    def notify_one_client(self, msg, client_id):
        """
        Used to send message to one client.
        If client is no longer active, he is deleted from the clients list.

        :param msg: message from server.
        :param client_id: client recipient.
        """
        try:
            self.clients[client_id].send(msg)
        except ConnectionResetError:
            print("Socket connection closed by client %s" % client_id)
            del self.clients[client_id]

    def listen_to_client(self, clientsocket, address):
        """
        Listen to incoming messages from clients. Each client gets a new thread for listening to its socket.
        Also checks if the connection was closed on client side.

        :param clientsocket: Socket that is listened to.
        :param address: Port and identifier of the client.
        """
        while True:
            try:
                # receive only 256 bytes
                data = clientsocket.recv(256)
                if data:
                    msg = data.decode('utf-8')
                    self.read_message(address, msg)
            except (ConnectionResetError, OSError):
                print("Socket connection closed by client %s" % address)
                clientsocket.close()
                if address in self.clients:
                    del self.clients[address]
                break

    def read_message(self, client_id, msg):
        """
        Processes a message received by client by forwarding it to every other client.

        :param client_id: Id of client who sent the message.
        :param msg: message that was received.
        """
        print("Server received message from client %s: '%s'" % (client_id, msg))
        self.notify_clients(msg, client_to_be_left_out=client_id)

    def start_server(self):
        """
        Starts the server and binds the TCP socket. Server is shut down by keyboard interrupt.
        """
        try:
            serversocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            serversocket.bind((self.host, self.port))
            print("Server started.")

            serversocket.listen(5)

            try:
                while True:
                    clientsocket, addr = serversocket.accept()
                    print("Established connection to client with ip %s, port %s" % (addr[0], addr[1]))
                    self.clients[addr[1]] = clientsocket
                    msg = "Connection to server established."
                    self.notify_one_client(msg.encode('utf-8'), addr[1])
                    start_new_thread(self.listen_to_client, (clientsocket, addr[1],))
            except KeyboardInterrupt:
                print("Server interrupted. Shut down.")
                serversocket.close()
                sys.exit(0)
        except socket.error:
            traceback.print_exc(file=sys.stdout)
            print("Failed to create Socket.")
            sys.exit()


if __name__ == "__main__":
    host = "127.0.0.1"
    port = 22222

    s = Server(host, port)
    s.start_server()
