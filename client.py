"""Module providing functionality for networks programming"""
import socket
import threading
import sys

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

    def receive(self):
        """Function to receive messages from the server"""
        while self.running:
            message = self.client.recv(1024).decode(ENCODING)
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
            # Commands start with a '/'
            if body and body[0] == '/':
                self.run_command(body[1:])
            else:
                self.client.send(body.encode(ENCODING))
    def run_command(self, command):
        """Function to run commands when a forward slash given"""
        match command:
            case 'wisper':
                pass
            case 'help':
                pass
            case 'leave':
                print('Quitting...')
                self.running = False
                self.client.send('/leave'.encode(ENCODING))
                sys.exit(0)
    def run(self):
        """Function to run the client object"""
        self.receive_thread.start()
        self.write_thread.start()
        # Send username to server
        self.client.send(self.username.encode(ENCODING))

if __name__ == '__main__':
    if len(sys.argv) <= 3:
        print('Need 3 arguments')
        sys.exit()
    client = Client(username=sys.argv[1], host=sys.argv[2], port=int(sys.argv[3]))
    client.run()
    