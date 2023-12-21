"""Module providing functionality for networks programming"""
import sys
import socket
import threading
import logging
import os
import random

logging.basicConfig(filename='server.log',
                    filemode='w',
                    format='%(asctime)s - %(levelname)s - %(message)s',
                    level=logging.DEBUG)

HEADERSIZE = 10
ENCODING = 'utf-8'
FILE_MSG = '0'
TEXT_MSG = '1'

class Server:
    """Class representing a server"""
    def __init__(self, host='127.0.0.1', port=1234):
        # Setup server socket
        self.server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server.settimeout(1)
        self.server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.server.bind((host, port))
        self.server.listen()
        logging.info('Opened server')

        # Setup storage for client info in the form (address, username)
        self.clients = {}

        # Setup mapping back from username to socket
        self.taken_names = {}

        self.running = True

        folder_name = 'download'
        self.make_folder(folder_name)

    def delete_folder(self, folder_name):
        """Function to delete a folder and its contents"""
        if os.path.exists(folder_name):
            for entry in os.scandir(folder_name):
                if entry.is_file():
                    os.unlink(entry.path)
                    print(f"Deleted file: {os.path.basename(entry.path)}")

            os.rmdir(folder_name)
            print(f"Folder '{folder_name}' has been deleted")

    def make_folder(self, folder_name):
        """Function to initialize a folder"""
        self.delete_folder(folder_name)
        os.makedirs(folder_name)
        logging.debug('Created folder %s', folder_name)

        # Populate folder with random files of size between 128 to 2048 bytes
        num_of_files = 5
        for i in range(num_of_files):
            file_path = os.path.join(folder_name, f'file_{i+1}.bin')
            with open(file_path, 'wb') as f:
                f.write(os.urandom(random.randint(128, 2048)))
        logging.debug('Created %s random binary files in %s', num_of_files, folder_name)

    def get_files(self, folder_name):
        """Function to return all files in a folder"""
        files = ''
        for entry in os.scandir(folder_name):
            if entry.is_file():
                files += f'   |--- {os.path.basename(entry.path)}\n'
        return files

    def get_message(self, client):
        """Function to receive full messages with header size"""
        # For the first recv, the file size is retrieved
        # Also checks for if client is alive
        message_length = None
        while message_length is None:
            try:
                message_length = client.recv(10).decode(ENCODING)
                if not message_length:
                    return ''
            except socket.timeout:
                continue
            except ConnectionResetError:
                return ''

        message_length = int(message_length)
        full_message = ''
        while True:
            # Receive either 8192, or the remaining, whichever is smaller
            # since we do not want to read into the next data
            try:
                message = client.recv(min(message_length, 8192)).decode(ENCODING)
            except ConnectionResetError:
                return ''

            if not message:
                return ''
            message_length -= len(message)
            full_message += message
            if not message_length:
                return full_message

    def broadcast(self, message, mode=0, broadcaster=None, broadcastee=None):
        """Function to send messages"""
        pre_encoded_message = message
        # For binary data, send as-is
        # First bit is for type of message
        if isinstance(message, bytes):
            header = f'{FILE_MSG}{len(message):<{HEADERSIZE-1}}'.encode(ENCODING)
            message = header + message
        else:
            message = f'{TEXT_MSG}{len(message):<{HEADERSIZE-1}}' + message
            message = message.encode(ENCODING)
        match mode:
            # Broadcast to all (Server mode)
            case 1:
                for client in self.clients:
                    client.sendall(message)
            # Broadcast to all but broadcaster
            case 2:
                for client in self.clients:
                    if client != broadcaster:
                        client.sendall(message)
                logging.info("Broadcast '%s' to all but %s",
                            pre_encoded_message, self.clients[broadcaster][1])
            # Broadcast to individual
            case 3:
                broadcastee.sendall(message)

    def kill_connection(self, client):
        """Function to kill connection to unresponsive clients"""
        address, username = self.clients[client]
        client.close()
        self.clients.pop(client)
        self.taken_names.pop(username)
        self.broadcast(f'[SERVER]: {username} just left. Goodbye!', mode=1)
        logging.info("Broadcasted '%s just left. Goodbye!'", username)
        logging.info('Disconnected with %s. Remove client named %s', address, username)
        print(f"Disconnected with {address}. Remove client named {username}")

    def run_command(self, command, client=None):
        """Function to run commands when a forward slash given"""
        command_type = command.split(' ')[0]
        match command_type:
            case 'download':
                # If only /download, return the download folder content
                if command_type == command:
                    message = self.get_files('download')
                    self.broadcast('[SERVER]: The following files are in ' +
                                   '[download]\n\ndownload/\n' + message +
                                   '\n[SERVER]: To download a file, type /download [file_name]',
                                   mode=3, broadcastee=client)
                    logging.info("Unicast files in download folder to %s", self.clients[client][1])
                else:
                    _, file_name = command.split(' ')
                    logging.info("Unicast file named %s to %s", file_name, self.clients[client][1])
                    file_name = os.path.join('download', file_name)
                    if os.path.exists(file_name):
                        with open(file_name, 'rb') as file_data:
                            file_content = file_data.read()
                            self.broadcast(file_content, mode=3, broadcastee=client)
                    else:
                        self.broadcast('File requested does not exist',
                                       mode=3, broadcastee=client)
                        logging.info("Unicast 'File requested does not exist' to %s",
                                     self.clients[client][1])

            case 'whisper':
                _, target, message = command.split(' ', 2)
                if target not in self.taken_names:
                    self.broadcast('[SERVER]: Username does not exist', mode=3, broadcastee=client)
                    logging.info("Unicast 'Username does not exist' to %s",
                                 self.clients[client][1])
                elif target == self.clients[client][1]:
                    self.broadcast('[SERVER]: You cannot whisper to yourself',
                                   mode=3, broadcastee=client)
                    logging.info("Unicast 'You cannot whisper to yourself' to %s",
                                 self.clients[client][1])
                else:
                    self.broadcast(f'[{self.clients[client][1]} (WHISPER)]: {message}',
                               mode=3, broadcastee=self.taken_names[target])
                    logging.info("%s unicast '%s' to %s",
                                 self.clients[client][1], message, target)

            case 'leave':
                self.kill_connection(client)

            case _:
                self.broadcast('[SERVER]: Invalid command', mode=3, broadcastee=client)
                logging.info("Unicast 'Invalid command' to %s", self.clients[client][1])

    def handle(self, client):
        """Function to handle messages received from clients"""
        while True:
            try:
                message = self.get_message(client)
                if not message:
                    if not self.running:
                        sys.exit(0)
                    self.kill_connection(client)
                elif message[0] == '/':
                    self.run_command(message[1:], client=client)
                else:
                    self.broadcast(f'[{self.clients[client][1]}]: ' + message,
                                   mode=2, broadcaster=client)
            except OSError:
                sys.exit(0)

    def run(self):
        """Function to run the server"""
        try:
            while True:
                # If CTRL+C pressed, server closes
                client = None
                while not client:
                    try:
                        client, address = self.server.accept()
                    except socket.timeout:
                        continue
                    except KeyboardInterrupt:
                        self.kill_server()

                client.settimeout(5)
                username = self.get_message(client)

                # Disallow duplicate username in chat
                if username in self.taken_names:
                    self.broadcast('[SERVER]: Username taken', mode=3, broadcastee=client)
                    logging.info("Unicast 'Username taken' to incoming socket")
                    client.close()
                    continue

                # Store clients' address and username with the socket as key
                self.clients[client] = (address, username)
                self.taken_names[username] = client

                # Broadcast after as it loops over clients dictionary
                logging.info('Connected with %s. Add client named %s', address, username)
                print(f'Connected with {address}. Add client named {username}')
                self.broadcast(f'[SERVER]: {username} just joined. Welcome!', mode=1)
                logging.info("Broadcast '%s just joined. Welcome!'", username)
                thread = threading.Thread(target=self.handle, args=(client,))
                thread.daemon = True
                thread.start()
        except KeyboardInterrupt:
            self.kill_server()

    def kill_server(self):
        """Function to close the server gracefully"""
        self.server.close()
        for client, info in self.clients.items():
            client.close()
            logging.info('Disconnected with %s. Remove client named %s',
                        info[0], info[1])
            print(f"Disconnected with {info[0]}. Remove client named {info[1]}")
        logging.warning('Closed server')
        print('Disconnecting...')
        self.running = False
        sys.exit(0)

if __name__ == '__main__':
    if len(sys.argv) <= 1:
        print('Need 1 arguments')
        sys.exit(0)

    server = Server(port=int(sys.argv[1]))
    server.run()
    