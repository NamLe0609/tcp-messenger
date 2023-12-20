"""Module providing functionality for networks programming"""
import sys
import socket
import threading
import logging

#logging.basicConfig(filename='server.log', filemode='w', format='%(levelname)s:%(message)s', level=logging.DEBUG)
logging.basicConfig(format='%(levelname)s - %(asctime)s: %(message)s', level=logging.DEBUG)

HEADERSIZE = 10
ENCODING = 'utf-8'

class Server:
    """Class representing a server"""
    def __init__(self, host='127.0.0.1', port=1234):
        # Setup server socket
        self.server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server.bind((host, port))
        self.server.listen()

        # Setup storage for client info in the form (address, username)
        self.clients = {}
        # Setup mapping back from username to socket
        self.taken_names = {}

    def broadcast(self, message, mode=0, broadcaster=None, broadcastee=None):
        """Function to send messages"""
        # Append a fixed size header
        message = f'{len(message):<{HEADERSIZE}}' + message
        match mode:
            # Broadcast to all (Server mode)
            case 1:
                for client in self.clients:
                    client.sendall(message.encode(ENCODING))
            # Broadcast to all but broadcaster
            case 2:
                for client in self.clients:
                    if client != broadcaster:
                        client.sendall(message.encode(ENCODING))
            # Broadcast to individual
            case 3:
                broadcastee.sendall(message.encode(ENCODING))

    def get_message(self, client):
        """Function to receive full messages with header size"""
        full_message = ''
        while True:
            message = client.recv(10)
            if not message:
                return ''

            if full_message == '':
                message_length = int(message[:HEADERSIZE])

            full_message += message.decode(ENCODING)
            if len(full_message) - HEADERSIZE == message_length:
                return full_message[HEADERSIZE:]

    def handle(self, client):
        """Function to handle messages received from clients"""
        while True:
            try:
                message = self.get_message(client)
                if not message:
                    self.kill_connection(client)
                elif message[0] == '/':
                    self.run_command(message[1:], client=client)
                else:
                    self.broadcast(f'[{self.clients[client][1]}]: ' + message,
                                   mode=2, broadcaster=client)
            except OSError:
                break

    def kill_connection(self, client):
        """Function to kill connection to unresponsive clients"""
        address, username = self.clients[client]
        client.close()
        self.clients.pop(client)
        self.taken_names.pop(username)
        self.broadcast(f'[SERVER]: {username} just left. Goodbye!', mode=1)
        print(f'Disonnected with {str(address)}. Remove client named {username}')

    def run_command(self, command, client=None):
        """Function to run commands when a forward slash given"""
        command_type = command.split(' ')[0]
        match command_type:
            case 'whisper':
                _, target, message = command.split(' ', 2)
                if target not in self.taken_names:
                    self.broadcast('[SERVER]: Username does not exist', mode=3, broadcastee=client)
                elif target == self.clients[client][1]:
                    self.broadcast('[SERVER]: You cannot whisper to yourself',
                                   mode=3, broadcastee=client)
                else:
                    self.broadcast(f'[{self.clients[client][1]} (WHISPER)]: {message}',
                               mode=3, broadcastee=self.taken_names[target])
            case 'leave':
                self.kill_connection(client)
            case _:
                self.broadcast('[SERVER]: Invalid command', mode=3, broadcastee=client)

    def run(self):
        """Function to run The server"""
        while True:
            client, address = self.server.accept()
            username = self.get_message(client)

            # Disallow duplicate username in chat
            if username in self.taken_names:
                self.broadcast('[SERVER]: Username taken', mode=3, broadcastee=client)
                client.close()
                continue

            # Store clients' address and username with the socket as key
            self.clients[client] = (address, username)
            self.taken_names[username] = client

            # Broadcast after as it loops over clients dictionary
            print(f'Connected with {str(address)}. Add client named {username}')
            self.broadcast(f'[SERVER]: {username} just joined. Welcome!', mode=1)
            thread = threading.Thread(target=self.handle, args=(client,))
            thread.start()

if __name__ == '__main__':
    if len(sys.argv) <= 1:
        print('Need 1 arguments')
        sys.exit()

    server = Server(port=int(sys.argv[1]))
    server.run()
    