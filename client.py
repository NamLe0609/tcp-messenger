"""Module providing functionality for networks programming"""
import socket
import threading
import sys
import os

HEADERSIZE = 10
ENCODING = 'utf-8'

class Client:
    """Class representing a client"""
    def __init__(self, username='John_Pork', host='127.0.0.1', port='1234'):
        # Setup client socket
        self.client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.client.connect((host, port))
        self.username = username

        # Define two seperate thread handling reads and writes from and to the server
        self.receive_thread = threading.Thread(target=self.receive, args=())
        self.write_thread = threading.Thread(target=self.write, args=())

        # State to check if client should be running
        self.running = True

    def get_message(self):
        """Function to receive full messages with header size"""
        full_message = ''
        while True:
            message = self.client.recv(10)
            if not message:
                return ''

            if full_message == '':
                message_length = int(message[:HEADERSIZE])

            full_message += message.decode(ENCODING)
            if len(full_message) - HEADERSIZE == message_length:
                return full_message[HEADERSIZE:]

    def send_message(self, message):
        """Function to send encoded messages with header size"""
        message = f'{len(message):<{HEADERSIZE}}' + message
        self.client.sendall(message.encode(ENCODING))

    def receive(self):
        """Function to receive and display messages from the server"""
        while self.running:
            message = self.get_message()
            # If the other thread is not alive then quit
            if not self.write_thread.is_alive():
                sys.exit(0)
            if message:
                print(message)
            else:
                print('Something went wrong. Press any key to exit. Disconnecting...')
                self.running = False
                self.client.close()
                sys.exit(0)

    def write(self):
        """Function to send messages to the server"""
        while self.running:
            body = input()
            # If the other thread is not alive then quit
            if not self.receive_thread.is_alive():
                sys.exit(0)

            if not body:
                continue

            # Commands start with a '/'
            if body[0] == '/':
                body = self.run_command(body)

            self.send_message(body)

    def run_command(self, command):
        """Function to run commands when a forward slash given"""
        command_type = command.split(' ')[0]
        match command_type[1:]:
            case 'help':
                pass

            case 'make_folder':
                pass

            case 'download':
                if len(command.split(' ')) < 2:
                    print('Fetching download folder content...')
                else:
                    print('Downloading...')

            case 'whisper':
                if len(command.split(' ')) < 3:
                    return '/'
                print('Whispering...')

            case 'leave':
                print('Leaving...')
                self.running = False

        return command

    def run(self):
        """Function to run the client object"""
        self.receive_thread.start()
        self.write_thread.start()

        # Send username to server
        self.send_message(self.username)

if __name__ == '__main__':
    if len(sys.argv) <= 3:
        print('Need 3 arguments')
        sys.exit()

    client = Client(username=sys.argv[1], host=sys.argv[2], port=int(sys.argv[3]))
    client.run()
    